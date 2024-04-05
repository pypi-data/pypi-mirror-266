from __future__ import annotations
from datetime import timedelta, datetime
from typing import TYPE_CHECKING, Any

from qprsim.config import parameter_implementations as pimpls, oc_parameter_implementations as ocpi
from qprsim.shared.enums import OCActivityProperty, ActivityState, PropertyEnumType, OCObjectBirthplaceProperty, \
    OCObjectBirthplaceState, \
    StateEnumType
from .model_data import ModelData

if TYPE_CHECKING:
    from qprsim.core import object_def as obd
    from . import conceptual_models as cm
    from . import oc_graph_models as gm
    import oc_model_parameters as ocpa


class OCActivityData(ModelData[OCActivityProperty, ActivityState]):
    stateType = ActivityState
    propertyType = OCActivityProperty

    def __init__(self, activity_model: gm.OCActivityModel, properties: dict[PropertyEnumType, Any] = None,
                 **kwargs) -> None:
        super().__init__(properties, **kwargs)
        self.activity_model: gm.OCActivityModel = activity_model
        self.__is_demanding = False

    @staticmethod
    def initial_state() -> dict[StateEnumType, Any]:
        return {ActivityState.InBusiness: False, ActivityState.QueueLength: 0}

    @staticmethod
    def initial_properties() -> dict[PropertyEnumType, Any]:
        return {OCActivityProperty.ProcessingTimeSampler: pimpls.ZeroSampler, OCActivityProperty.QueueingDiscipline: pimpls.Fifo,
                OCActivityProperty.ObjectQualifier: ocpi.DefaultObjectQualifier}

    def sample_processing_time(self, carrier: obd.Carrier, resource: cm.ResourceProvider) -> timedelta:
        return self.properties[OCActivityProperty.ProcessingTimeSampler].sample(carrier, resource)

    def generate_event_attributes(self, carrier: obd.Carrier, **kwargs) -> dict[str, Any]:
        if OCActivityProperty.EventAttributeGenerator in self.properties:
            return self.properties[OCActivityProperty.EventAttributeGenerator].generate(carrier, **kwargs)
        else:
            return {}

    def generate_carrier_attributes(self, carrier: obd.Carrier, **kwargs) -> dict[obd.Object, dict[str, Any]]:
        if OCActivityProperty.CarrierAttributeGenerator in self.properties:
            return self.properties[OCActivityProperty.CarrierAttributeGenerator].generate(carrier, **kwargs)
        else:
            return {}

    def determine_object_qualifiers(self, carrier: obd.Carrier, **kwargs) -> dict[obd.Qualifier, set[obd.Object]]:
        if OCActivityProperty.ObjectQualifier in self.properties:
            return self.properties[OCActivityProperty.ObjectQualifier].qualify(carrier, **kwargs)
        else:
            return {}

    def dequeue(self, queue: list[tuple[datetime, obd.Carrier]]) -> obd.Carrier:
        return queue.pop(self.properties[OCActivityProperty.QueueingDiscipline].select(queue))[1]

    def queue_changed(self):
        self._state[ActivityState.QueueLength] = len(self.activity_model.waiting_queue)
        self._determine_status()

    @property
    def is_demanding(self) -> bool:
        return self.__is_demanding

    def _determine_status(self):
        new_status = self._state[ActivityState.InBusiness] and self._state[ActivityState.QueueLength] > 0
        if self.is_demanding is not new_status:
            self.__is_demanding = new_status
            self.activity_model.demand_changed()


class OCObjectBirthplaceData(ModelData[OCObjectBirthplaceProperty, OCObjectBirthplaceState]):
    stateType = OCObjectBirthplaceState
    propertyType = OCObjectBirthplaceProperty

    def __init__(self, properties: dict[PropertyEnumType, Any] = None,
                 **kwargs) -> None:
        super().__init__(properties, **kwargs)


    @staticmethod
    def initial_properties() -> dict[PropertyEnumType, Any]:
        return {OCObjectBirthplaceProperty.ObjectType: 'default',
                OCObjectBirthplaceProperty.ObjectCreator: ocpi.EmptyObjectCreator('default')}

    @staticmethod
    def initial_state() -> dict[StateEnumType, Any]:
        return {OCObjectBirthplaceState.CreationCount: 0}

    def create_object(self, object_id_source, **context_info) -> obd.Object:
        og: ocpa.ObjectCreator = self.properties[OCObjectBirthplaceProperty.ObjectCreator]
        o = og.create_object(object_id_source(), **context_info)
        self._state[OCObjectBirthplaceState.CreationCount] += 1
        return o

    def create_o2o(self, obj: obd.Object, **context) -> obd.QualifiedO2ORelations:
        og: ocpa.ObjectCreator = self.properties[OCObjectBirthplaceProperty.ObjectCreator]
        o2o = og.generate_initial_o2o_relations(obj, **context)
        return o2o
