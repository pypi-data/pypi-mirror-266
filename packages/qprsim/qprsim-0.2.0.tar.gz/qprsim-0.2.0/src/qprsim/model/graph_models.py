from __future__ import annotations

import collections
import itertools
import logging
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Tuple, Collection, Callable, TYPE_CHECKING

from qprsim.core import case as sc, event_system as ev_sys
from qprsim.shared.enums import ActivityProperty, ActivityState
from qprsim.utils import time_utils
from . import sim_graph as sgraph, model_data as mdata, model_parameters as params
from .model_traits import WithModelData, WithEventQueue, WithSimulationContext, WithActivityManager
from ..shared.shared_traits import WithLabel

from .conceptual_models import ResourceUser, ResourceProvider, ResourceToken

if TYPE_CHECKING:
    from qprsim.core import managers

    # from conceptual_models import ResourceUser, ResourceProvider


class SimulationNodeModel:

    def __init__(self, node: sgraph.WithModel = None, **kwargs) -> None:
        super(SimulationNodeModel, self).__init__()
        self.__node = node

    @property
    def node(self) -> sgraph.WithModel:
        return self.__node

    @node.setter
    def node(self, value: sgraph.WithModel):
        assert value is not None
        self.__node = value

    def accept(self, case: sc.Case):
        pass

    def forward(self, case: sc.Case, **kwargs):
        self.node.accept_from_model(case, **kwargs)


class ActivityModel(WithModelData[mdata.ActivityData], WithActivityManager, WithEventQueue, WithLabel, ResourceUser,
                    SimulationNodeModel):

    def __init__(self, activity_node: sgraph.ActivityNode, event_queue: ev_sys.EventQueue,
                 activity_manager: managers.ActivityManager,
                 data: mdata.ActivityData = None, **kwargs) -> None:
        super(ActivityModel, self).__init__(label=activity_node.label, node=activity_node, data=data, event_queue=event_queue,
                                            activity_manager=activity_manager, **kwargs)
        # self.label = activity_node.label
        self.waiting_queue: List[Tuple[datetime, sc.Case]] = []
        self.__data = data

    @property
    def is_demanding(self) -> bool:
        return self.data.is_demanding

    def demand_changed(self):
        self.activity_manager.activity_demand_change(self, self.is_demanding)

    def take_resource_from(self, resource: ResourceProvider):
        case = self.data.dequeue(self.waiting_queue)
        self.process(case, resource)
        self.data.queue_changed()

    def accept(self, case: sc.Case):
        self.delay(case)

    def delay(self, case: sc.Case):
        global_time = self.event_queue.global_time
        delay = self.data.sample_delay(global_time, case)
        if delay is None:
            self.schedule(case)
        else:
            self.event_queue.offer_delayed(delay, ev_sys.Callback(self._after_delay, ev_sys.CaseDelayedEvent(case)))

    def _after_delay(self, delay_event: ev_sys.CaseDelayedEvent):
        self.schedule(delay_event.case)

    def _create_event(self, case: sc.Case, resource: ResourceProvider | None, time: datetime,
                      **attrs) -> sc.CaseEvent:
        attrs.update(self.data.generate_event_attributes(case, resource, attrs['lifecycle'], activity=self.label))
        return sc.CaseEvent(self.label, str(resource) if resource is not None else 'n/a', time, **attrs)

    def schedule(self, case: sc.Case):
        if self.data.peek_at_property(ActivityProperty.DiscardIfNotInBusiness) and not self.data.peek_at_state(
                ActivityState.InBusiness):
            logging.info(f'{self.label} discarded case {case.case_id} due to not being in business')
            self.discard(case)
            return
        max_length = self.data.peek_at_property(ActivityProperty.MaxQueueLength)
        if max_length is not None and len(self.waiting_queue) >= max_length:
            logging.info(f'{self.label} discarded case {case.case_id} due to max queue length')
            self.discard(case)
            return

        global_time = self.event_queue.global_time
        case.add_event(self._create_event(case, None, global_time, lifecycle='schedule'))
        logging.info(f'{self.label} enqueued case {case.case_id}')
        self.waiting_queue.append((global_time, case))
        self.data.queue_changed()

    def discard(self, case: sc.Case):
        if self.data.has_external_discarding_handler():
            self.data.submit_to_external_discard_handler(case)

    def process(self, case: sc.Case, resource: ResourceProvider):
        global_time = self.event_queue.global_time

        rt = resource.provide_resource(self, case)

        completion_event = ev_sys.ProcessingCompletionEvent(case, resource, rt)
        if self.data.has_external_processing_handler():
            handler = self.data.get_external_processing_handler()
            case.add_event(self._create_event(case, resource, global_time, lifecycle='start'))
            logging.info(
                f'{self.label} started processing of case {case.case_id} with {resource} until released by {handler}')
            self.event_queue.offer_immediate(ev_sys.Callback(self._handle_processing_externally, completion_event))
        else:
            processing_time = self.data.sample_processing_time(case, resource)
            completion_time = time_utils.add(global_time, processing_time)
            case.add_event(self._create_event(case, resource, global_time, lifecycle='start', duration=processing_time))
            logging.info(
                f'{self.label} started processing of case {case.case_id} with {resource} for {processing_time} (@{completion_time})')
            self._complete_processing_at(completion_time, completion_event)

    def _complete_processing_at(self, completion_time: datetime, completion_event: ev_sys.ProcessingCompletionEvent):
        self.event_queue.offer(ev_sys.TimedCallback(completion_time, self._after_processing, completion_event))

    def _handle_processing_externally(self, completion_event: ev_sys.ProcessingCompletionEvent):
        self.data.submit_to_external_processing_handler(ev_sys.Callback(self._after_processing, completion_event),
                                                        completion_event)

    def _after_processing(self, completion_event: ev_sys.ProcessingCompletionEvent):
        self.complete(completion_event.case, completion_event.resource, completion_event.token)

    def complete(self, case: sc.Case, resource: ResourceProvider, token: ResourceToken):
        global_time = self.event_queue.global_time
        complete = self._create_event(case, resource, global_time, lifecycle='complete')
        case.add_event(complete)
        logging.info(f'{self.label} completed processing of case {case.case_id} with {resource}')

        resource.release_resource(token)

        self.forward(case)

    def __str__(self) -> str:
        return self.label

    def __repr__(self) -> str:
        return f'ActivityModel({self.label})'


class DelayModel(WithEventQueue, SimulationNodeModel):

    def __init__(self, event_queue: ev_sys.EventQueue, delay_sampler: params.DelaySampler, **kwargs) -> None:
        super(DelayModel, self).__init__(event_queue=event_queue, **kwargs)
        self.delay_sampler = delay_sampler

    @property
    def delay_sampler(self) -> params.DelaySampler:
        return self._delay_sampler

    @delay_sampler.setter
    def delay_sampler(self, value: params.DelaySampler) -> None:
        self._delay_sampler = value

    def accept(self, case: sc.Case):
        self.delay(case)

    def delay(self, case: sc.Case) -> None:
        global_time = self.event_queue.global_time
        delta = self.delay_sampler.sample(global_time)
        self.event_queue.offer_delayed(delta, ev_sys.Callback(self.after_delay, ev_sys.CaseDelayedEvent(case)))

    def after_delay(self, case_delayed_event: ev_sys.CaseDelayedEvent) -> None:
        self.forward(case_delayed_event.case)


class DecisionModel(SimulationNodeModel):

    def __init__(self, classifier: params.CaseClassifier, **kwargs) -> None:
        super().__init__(**kwargs)
        self.classifier = classifier

    @property
    def classifier(self) -> params.CaseClassifier:
        return self._classifier

    @classifier.setter
    def classifier(self, value: params.CaseClassifier):
        self._classifier = value

    def accept(self, case: sc.Case):
        idx = self.classifier.classify(case)
        self.forward(case, successor_id=idx)


CaseForwarding = sc.Case | tuple[sc.Case, dict] | Collection[
    tuple[sc.Case, dict]]


@dataclass
class SyncResult:
    to_wait: Collection[sc.Case]
    to_remove: Collection[sc.Case]
    to_forward: Collection[tuple[sc.Case, dict]]

    @classmethod
    def skip(cls) -> SyncResult:
        return SyncResult([], [], [])

    @classmethod
    def enqueue(cls, case) -> SyncResult:
        return SyncResult([case], [], [])

    @classmethod
    def wave_through(cls, case, **kwargs) -> SyncResult:
        return SyncResult([], [], [(case, kwargs)])

    @classmethod
    def representative_sync(cls, case, **kwargs) -> SyncResult:
        return SyncResult([], [case], [(case, kwargs)])

    @classmethod
    def instant_representative_sync(cls, case, **kwargs) -> SyncResult:
        return cls.wave_through(case, **kwargs)

    @classmethod
    def group_sync(cls, synced_group: Collection[sc.Case], representative: sc.Case, **kwargs) -> SyncResult:
        return SyncResult([], synced_group, [(representative, kwargs)])

    @classmethod
    def group_multi_sync(cls, synced_group: Collection[sc.Case],
                         representatives: Collection[tuple[sc.Case, dict]]) -> SyncResult:
        return SyncResult([], synced_group, representatives)

    @property
    def was_successful(self):
        return len(self.to_forward) > 0


class SyncModel(SimulationNodeModel):

    def __init__(self, node: sgraph.WithModel = None, **kwargs) -> None:
        super(SyncModel, self).__init__(node, **kwargs)
        self.waiting_on_sync: dict[str, sc.Case] = {}

    @abstractmethod
    def _check_sync_possibility(self, newcomer: sc.Case) -> SyncResult:
        ...

    def accept(self, case: sc.Case):
        sync_result = self._check_sync_possibility(case)
        for c in sync_result.to_wait:
            self.waiting_on_sync[c.case_id] = c
        for c in sync_result.to_remove:
            del self.waiting_on_sync[c.case_id]
        for c, kwargs in sync_result.to_forward:
            self.forward(c, **kwargs)
        if sync_result.was_successful:
            logging.info(
                f'Synchronizer synced {[c.case_id for c in sync_result.to_remove]} into {[c.case_id for c, _ in sync_result.to_forward]}.')


class DirectSyncModel(SyncModel):

    def __init__(self, unifier: Callable[[dict[str, sc.Case], sc.Case], SyncResult] = None,
                 **kwargs) -> None:
        super(DirectSyncModel, self).__init__(**kwargs)
        self.unifier = unifier

    def _check_sync_possibility(self, newcomer: sc.Case):
        return self.unifier(self.waiting_on_sync, newcomer)


class SubsetSyncModel(SyncModel):

    def __init__(self, arity: int = 2,
                 unifier: Callable[[set[sc.Case]], None | sc.Case | tuple[sc.Case, dict]] = None,
                 **kwargs) -> None:
        super(SubsetSyncModel, self).__init__(**kwargs)
        self.arity = arity
        self.unifier = unifier

    def _check_sync_possibility(self, newcomer: sc.Case):
        for subset in itertools.combinations(self.waiting_on_sync, self.arity - 1):
            test_subset = set(subset) | {newcomer}
            unified = self.unifier(test_subset)
            if unified is not None:
                if isinstance(unified, tuple):
                    return SyncResult.group_sync(test_subset, unified[0], **unified[1])
                else:
                    return SyncResult.group_sync(test_subset, unified)
        return SyncResult.enqueue(newcomer)


class SimpleCountSyncModel(SyncModel):

    def __init__(self, expected_count: int, node: sgraph.WithModel = None, **kwargs) -> None:
        super(SimpleCountSyncModel, self).__init__(node, **kwargs)
        assert expected_count > 1
        self.expected_count = expected_count
        self.counts = collections.defaultdict(int)

    def _check_sync_possibility(self, newcomer: sc.Case) -> SyncResult:
        self.counts[newcomer.case_id] += 1
        if self.counts[newcomer.case_id] >= self.expected_count:
            del self.counts[newcomer.case_id]
            return SyncResult.representative_sync(newcomer)
        else:
            return SyncResult.enqueue(newcomer)


class AwaitChildrenSync(SyncModel):

    def __init__(self, calc_expectation: Callable[[sc.Case], int], child_classifier: Callable[[sc.Case], bool] = None, node: sgraph.WithModel = None,
                 **kwargs) -> None:
        super(AwaitChildrenSync, self).__init__(node, **kwargs)
        self.get_expectation = calc_expectation
        self.child_cases_left = collections.defaultdict(int)
        self.child_classifier = child_classifier

    def _check_sync_possibility(self, newcomer: sc.Case) -> SyncResult:
        if isinstance(newcomer, sc.ChildCase) and (self.child_classifier is None or self.child_classifier(newcomer)):
            pid = newcomer.parent.case_id
            self.child_cases_left[pid] -= 1
            if pid in self.waiting_on_sync and self.child_cases_left[pid] <= 0:
                parent = self.waiting_on_sync[pid]
                del self.child_cases_left[pid]
                return SyncResult.representative_sync(parent, successor_id=0)
        else:
            value = self.get_expectation(newcomer)
            self.child_cases_left[newcomer.case_id] += value
            if self.child_cases_left[newcomer.case_id] <= 0:
                del self.child_cases_left[newcomer.case_id]
                return SyncResult.instant_representative_sync(newcomer, successor_id=0)
            else:
                return SyncResult.enqueue(newcomer)
        return SyncResult.skip()


class CaseTransformerModel(SimulationNodeModel):

    def __init__(self, transformer: Callable[[sc.Case], CaseForwarding], **kwargs) -> None:
        super(CaseTransformerModel, self).__init__(**kwargs)
        self.transformer = transformer

    def accept(self, case: sc.Case):
        transformer = self.transformer(case)
        if isinstance(transformer, tuple):
            case, kwargs = transformer
            self.forward(case, **kwargs)
        elif isinstance(transformer, list):
            for case, kwargs in transformer:
                self.forward(case, **kwargs)
        else:
            self.forward(case)


class TerminalModel(WithSimulationContext, SimulationNodeModel):

    def __init__(self, label: str = None, **kwargs) -> None:
        super(TerminalModel, self).__init__(**kwargs)
        self.__arrived_cases = []
        self.observed_case_ids = set()
        label = getattr(self.node, 'label', label)
        self.simulation_context.register_case_collection(label, self.arrived_cases)

    @property
    def case_count(self):
        return len(self.arrived_cases)

    @property
    def arrived_cases(self) -> list[sc.Case]:
        return self.__arrived_cases

    def accept(self, case: sc.Case):
        self.simulation_context.register_case_completion(case)
        self.arrived_cases.append(case)
        assert case.case_id not in self.observed_case_ids
        self.observed_case_ids.add(case.case_id)
        logging.info(f'TerminalNode received case {case.case_id} (total: {self.case_count})')


class ArrivalModel(WithSimulationContext, ev_sys.Updatable, SimulationNodeModel):

    def __init__(self, **kwargs) -> None:
        super(ArrivalModel, self).__init__(**kwargs)

    def receive_event(self, event: ev_sys.CaseArrivalEvent):
        creation_no = self.simulation_context.started_cases_count
        attrs = dict(event.case_attributes)
        if 'case_creation_no' not in attrs:
            attrs['case_creation_no'] = creation_no
        case = sc.create_case(case_id=event.proposed_case_id, **attrs)
        self.simulation_context.register_case_creation(case)
        logging.info(f'ArrivalModel created case {case.case_id}')
        self.forward(case)
