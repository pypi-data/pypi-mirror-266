from __future__ import annotations

import itertools
import logging
from abc import abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Collection

from qprsim.core import object_def as obd, event_system as ev_sys, oc_events as oc_ev
from qprsim.shared.enums import OCActivityProperty, OCObjectBirthplaceProperty, ActivityState
from qprsim.utils import time_utils
from . import oc_model_data as mdata
from .conceptual_models import ResourceUser, ResourceProvider, ResourceToken
from .model_traits import WithModelData, WithSimulationContext, WithEventQueue, ModelDataType, WithActivityManager
from .oc_model_traits import WithEventManager, WithObjectManager
from ..utils.utils import nice_dict_str

if TYPE_CHECKING:
    import oc_model_parameters as ocpa
    from . import oc_sim_graph as sgraph


class OCSimulationNodeModel:

    def __init__(self, node: sgraph.WithModel = None, **kwargs) -> None:
        super(OCSimulationNodeModel, self).__init__()
        self.__node = node

    @property
    def node(self) -> sgraph.WithModel:
        return self.__node

    @node.setter
    def node(self, value: sgraph.WithModel):
        assert value is not None
        self.__node = value

    @abstractmethod
    def accept(self, carrier: obd.Carrier):
        pass

    def forward(self, carrier: obd.Carrier, **kwargs):
        self.node.accept_from_model(carrier, **kwargs)


class OCDecisionModel(OCSimulationNodeModel):
    def __init__(self, classifier: ocpa.CarrierClassifier, **kwargs) -> None:
        super().__init__(**kwargs)
        self.classifier = classifier

    @property
    def classifier(self) -> ocpa.CarrierClassifier:
        return self._classifier

    @classifier.setter
    def classifier(self, value: ocpa.CarrierClassifier):
        self._classifier = value

    def accept(self, case: obd.Carrier):
        idx = self.classifier.classify(case)
        self.forward(case, successor_id=idx)


class OCActivityModel(WithModelData[mdata.OCActivityData], WithEventQueue, WithActivityManager, WithEventManager,
                      ResourceUser,
                      OCSimulationNodeModel):

    def __init__(self, data: ModelDataType = None, **kwargs) -> None:
        super().__init__(data=data, **kwargs)
        self.waiting_queue: list[tuple[datetime, obd.Carrier]] = []

    def accept(self, carrier: obd.Carrier):
        self._enqueue(carrier)

    @property
    def is_demanding(self) -> bool:
        return self.data.is_demanding

    def take_resource_from(self, resource: ResourceProvider):
        carrier = self.data.dequeue(self.waiting_queue)
        self._process(carrier, resource)
        self.data.queue_changed()

    def _create_event(self, carrier: obd.Carrier, time: datetime,
                      **attrs) -> obd.ObjectEvent:
        attrs.update(self.data.generate_event_attributes(carrier, time=time))
        # {s: o for s, o in attrs.items() if isinstance(o, obd.Object)}
        qualifiers = self.data.determine_object_qualifiers(carrier)
        return obd.ObjectEvent(self.data.peek_at_property(OCActivityProperty.EventType), time, qualifiers, **attrs)

    def _enqueue(self, carrier: obd.Carrier):
        self.waiting_queue.append((self.event_queue.global_time, carrier))
        self.data.queue_changed()

    def schedule(self, carrier: obd.Carrier):
        schedule_event = self._create_event(carrier, self.event_queue.global_time, lifecycle='schedule')
        self.event_manager.log(schedule_event)
        logging.info(f'{self} scheduled processing of {carrier}')
        self._enqueue(carrier)

    def _process(self, carrier: obd.Carrier, resource: ResourceProvider):
        time = self.event_queue.global_time

        rt = resource.provide_resource(self, carrier)

        processing_time = self.data.sample_processing_time(carrier, resource)
        start_event = self._create_event(carrier, time, resource=str(resource), lifecycle='start',
                                         duration=processing_time)

        self.event_manager.log(start_event)
        logging.info(f'{self} started processing of {carrier} with {resource}')

        completion_time = time_utils.add(time, processing_time)
        completion_event = oc_ev.ProcessingCompletionEvent(carrier, resource=resource, token=rt)

        self.event_queue.offer(ev_sys.TimedCallback(completion_time, self._after_processing, completion_event))

    def _after_processing(self, completion_event: oc_ev.ProcessingCompletionEvent):
        self._complete(completion_event.carrier, **completion_event.info)

    def _complete(self, carrier: obd.Carrier, resource: ResourceProvider, token: ResourceToken):
        global_time = self.event_queue.global_time

        attrs = self.data.generate_carrier_attributes(carrier, resource=resource, time=global_time)

        completion_event = self._create_event(carrier, global_time, resource=str(resource), lifecycle='complete')
        self.event_manager.log(completion_event)
        logging.info(f'{self} completed processing of {carrier} with {resource}')

        for o in carrier:
            if o in attrs:
                o.log_attribute_change(oc_ev.AttributesChangeEvent(global_time, **attrs[o]))

        resource.release_resource(token)

        self.forward(carrier)

    def demand_changed(self):
        self.activity_manager.activity_demand_change(self, self.is_demanding)

    def __str__(self) -> str:
        return self.data.peek_at_property(OCActivityProperty.EventType)


class OCGraveyardModel(WithSimulationContext, WithObjectManager, OCSimulationNodeModel):

    def __init__(self, **kwargs) -> None:
        super(OCGraveyardModel, self).__init__(**kwargs)
        self.__observed_objects = []

    @property
    def object_count(self):
        return len(self.observed_objects)

    @property
    def observed_objects(self) -> list[obd.Object]:
        return self.__observed_objects

    def accept(self, carrier: obd.Carrier):
        for o in carrier:
            self.observed_objects.append(o)
        self.object_manager.retire(*carrier)
        logging.info(f'OCGraveyardModel received {carrier} (total: {self.object_count} objects)')


class OCBirthplaceModel(WithModelData[mdata.OCObjectBirthplaceData], WithSimulationContext, WithObjectManager,
                        ev_sys.Updatable,
                        OCSimulationNodeModel):

    def __init__(self, **kwargs) -> None:
        super(OCBirthplaceModel, self).__init__(**kwargs)

    def accept(self, carrier: obd.Carrier):
        pass

    def receive_event(self, event: oc_ev.ObjectArrivalEvent):
        def id_source():
            return f'{self.object_manager.generate_unique_id(self.data.peek_at_property(OCObjectBirthplaceProperty.ObjectType))}:{event.proposed_object_id}'

        o = self.data.create_object(id_source, time=event.time)
        self.object_manager.birth(o)
        o2o = self.data.create_o2o(o)
        self.object_manager.relate(**o2o)

        logging.info(f'OCBirthplaceModel created object {o}')
        c = obd.Carrier(o)
        self.forward(c)


class OCSyncModel(OCSimulationNodeModel):

    def __init__(self, node: sgraph.WithModel = None, **kwargs) -> None:
        super().__init__(node, **kwargs)
        self._waiting: set[obd.Object] = set()
        self._expectations: dict[obd.Carrier, set[obd.Object]] = {}
        self._reverse_map: dict[obd.Object, obd.Carrier] = {}

    def set_expectation(self, expectation: obd.Carrier):
        self._expectations[expectation] = set(expectation)
        for o in expectation:
            # conflicting syncs not allowed here for simplicity
            assert o not in self._reverse_map
            self._reverse_map[o] = expectation

    def _free(self, obj: obd.Object):
        self._waiting.remove(obj)
        del self._reverse_map[obj]

    def _check_sync_possibility(self, newcomer: obd.Carrier) -> obd.Carrier:
        res = None
        for o in newcomer:
            c = self._reverse_map[o]
            missing_objects = self._expectations[c]
            missing_objects.remove(o)
            if len(missing_objects) == 0:
                del self._expectations[c]
                res = c

        return res

    def accept(self, carrier: obd.Carrier):
        for o in carrier:
            self._waiting.add(o)
        sync = self._check_sync_possibility(carrier)
        logging.info(f'OCSyncModel synchronized object {sync}')
        if sync:
            for o in sync:
                self._free(o)
            self.forward(sync)


class OCSplitModel(OCSimulationNodeModel):

    def __init__(self, splitter: ocpa.CarrierSplitter, node: sgraph.WithModel = None, **kwargs) -> None:
        super().__init__(node, **kwargs)
        self.splitter = splitter

    def accept(self, carrier: obd.Carrier):
        split = self.splitter.split_up(carrier)

        logging.info(f'OCSplitModel split {carrier} into {nice_dict_str(split)}')
        for c, idx in split.items():
            self.forward(c, successor_id=idx)


class OCCarrierGeneratorModel(WithObjectManager, OCSimulationNodeModel):

    def __init__(self, carrier_generator: ocpa.CarrierGenerator, node: sgraph.WithModel = None, **kwargs) -> None:
        super().__init__(node=node, **kwargs)
        self.carrier_generator = carrier_generator

    def accept(self, carrier: obd.Carrier):
        def gen_id(ot):
            return self.object_manager.generate_unique_id(ot)

        c, o2o = self.carrier_generator.create_carrier(gen_id, carrier=carrier)
        self.object_manager.birth(*c)
        self.object_manager.relate(**o2o)
        self.forward(obd.Carrier(*itertools.chain(carrier, c)))


##############################################################################
# FUTURE WORK
##############################################################################
class OCAttributeUpdaterModel(WithEventQueue, OCSimulationNodeModel):
    def accept(self, carrier: obd.Carrier):
        pass


CarrierForwarding = obd.Carrier | tuple[obd.Carrier, dict] | Collection[
    tuple[obd.Carrier, dict]]


class OCTransformerModel(OCSimulationNodeModel):
    def __init__(self, transformer: Callable[[obd.Carrier], CarrierForwarding], **kwargs) -> None:
        super(OCTransformerModel, self).__init__(**kwargs)
        self.transformer = transformer

    def accept(self, carrier: obd.Carrier):
        transformer = self.transformer(carrier)
        if isinstance(transformer, tuple):
            case, kwargs = transformer
            self.forward(case, **kwargs)
        elif isinstance(transformer, list):
            for case, kwargs in transformer:
                self.forward(case, **kwargs)
        else:
            self.forward(carrier)
