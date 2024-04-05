from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta, datetime
from typing import List, Any, Dict, Tuple, Generic, Callable, Type, TypeVar
from typing import TYPE_CHECKING

import qprsim.core.event_system as ev_sys
from qprsim.shared.base_classes import auto_str
from qprsim.shared.enums import ActivityProperty, ActivityState, ResourceProperty, ResourceState, PropertyEnumType, \
    StateEnumType

if TYPE_CHECKING:
    import qprsim.core.case as sc
    import qprsim.model.conceptual_models as cm
    import qprsim.model.graph_models as gm


class HasProperties(ev_sys.Updatable, Generic[PropertyEnumType]):
    propertyType: Type[PropertyEnumType]

    def __init__(self, properties: dict[PropertyEnumType, Any] = None, **kwargs) -> None:
        super(HasProperties, self).__init__(**kwargs)
        self._properties = self.initial_properties()
        if properties is not None:
            self._properties.update(properties)

    @staticmethod
    @abstractmethod
    def initial_properties() -> dict[PropertyEnumType, Any]:
        ...

    @property
    def properties(self) -> dict[PropertyEnumType, Any]:
        return self._properties

    @properties.setter
    def properties(self, value: dict[PropertyEnumType, Any]):
        assert value is not None
        self._properties = value

    def peek_at_property(self, key: PropertyEnumType) -> Any:
        return self.properties.get(key)

    def receive_event(self, event: ev_sys.DictUpdateEvent):
        property_key = self.propertyType.cast(event.key)
        if property_key is not None:
            self.properties[property_key] = event.new_value


class HasState(ev_sys.Updatable, Generic[StateEnumType]):
    stateType: Type[StateEnumType]

    def __init__(self, **kwargs) -> None:
        super(HasState, self).__init__(**kwargs)
        self._state: dict[StateEnumType, Any] = self.initial_state()

    @staticmethod
    @abstractmethod
    def initial_state() -> dict[StateEnumType, Any]:
        ...

    def peek_at_state(self, key: StateEnumType) -> Any:
        return self._state.get(key)

    def receive_event(self, event: ev_sys.DictUpdateEvent):
        state_key = self.stateType.cast(event.key)
        if state_key is not None:
            self._state[state_key] = event.new_value


class ModelData(HasProperties[PropertyEnumType], HasState[StateEnumType], ABC):

    def receive_event(self, event: ev_sys.DictUpdateEvent):
        key = event.key
        if self.stateType.can_cast(key):
            HasState.receive_event(self, event)
        if self.propertyType.can_cast(key):
            HasProperties.receive_event(self, event)


ModelDataType = TypeVar('ModelDataType', bound=ModelData)

@auto_str
class ActivityData(ModelData[ActivityProperty, ActivityState]):
    stateType = ActivityState
    propertyType = ActivityProperty

    def __init__(self, activity_model: gm.ActivityModel, **kwargs) -> None:
        super(ActivityData, self).__init__(**kwargs)
        self.activity_model = activity_model
        self.__is_demanding: bool = False

    @staticmethod
    def initial_properties():
        from qprsim.config import impls
        return {
            ActivityProperty.QueueingDiscipline: impls.Fifo,
            ActivityProperty.ProcessingTimeSampler: impls.StaticSampler(timedelta(minutes=60)),
            # ActivityProperty.MaxQueueLength: False
        }

    @staticmethod
    def initial_state():
        return {ActivityState.InBusiness: False,
                ActivityState.QueueLength: 0}

    @property
    def is_demanding(self) -> bool:
        return self.__is_demanding

    def queue_changed(self) -> None:
        self._state[ActivityState.QueueLength] = len(self.activity_model.waiting_queue)
        self._determine_status()

    def receive_event(self, event: ev_sys.DictUpdateEvent) -> None:
        super().receive_event(event)
        self._determine_status()

    def _determine_status(self):
        new_status = self._state[ActivityState.InBusiness] and self._state[ActivityState.QueueLength] > 0
        if self.is_demanding is not new_status:
            self.__is_demanding = new_status
            self.activity_model.demand_changed()

    def dequeue(self, queue: List[Tuple[datetime, sc.Case]]) -> sc.Case:
        return queue.pop(self.properties[ActivityProperty.QueueingDiscipline].select(queue))[1]

    def sample_processing_time(self, case: sc.Case, resource: cm.ResourceProvider) -> timedelta:
        return self.properties[ActivityProperty.ProcessingTimeSampler].sample(case, resource)

    def has_external_discarding_handler(self) -> bool:
        return ActivityProperty.ExternalDiscardingHandler in self.properties and self.properties[
            ActivityProperty.ExternalDiscardingHandler] is not None

    def has_external_processing_handler(self) -> bool:
        return ActivityProperty.ExternalProcessingHandler in self.properties and self.properties[
            ActivityProperty.ExternalProcessingHandler] is not None

    def submit_to_external_processing_handler(self, callback: ev_sys.Callback,
                                              event: ev_sys.ProcessingCompletionEvent):
        handler = self.get_external_processing_handler()
        return handler(callback, event.case, event.resource) if handler is not None else False

    def submit_to_external_discard_handler(self, case: sc.Case) -> None:
        handler = self.get_external_discarding_handler()
        return handler(case) if handler is not None else False

    def get_external_processing_handler(self) -> Callable[[ev_sys.Callback, sc.Case,
                                                           cm.ResourceProvider], ...]:
        if ActivityProperty.ExternalProcessingHandler in self.properties:
            return self.properties[ActivityProperty.ExternalProcessingHandler]

    def get_external_discarding_handler(self) -> Callable[[sc.Case], ...]:
        if ActivityProperty.ExternalDiscardingHandler in self.properties:
            return self.properties[ActivityProperty.ExternalDiscardingHandler]

    def sample_delay(self, current_time, case: sc.Case) -> timedelta | None:
        if ActivityProperty.DelaySampler in self.properties:
            return self.properties[ActivityProperty.DelaySampler].sample(current_time, case=case)

    def generate_event_attributes(self, case: sc.Case, resource: cm.ResourceProvider, lifecycle: str, **kwargs) -> Dict[
        str, Any]:
        if ActivityProperty.EventAttributeGenerator in self.properties:
            return self.properties[ActivityProperty.EventAttributeGenerator].generate(case=case, resource=resource,
                                                                                      lifecycle=lifecycle, **kwargs)
        else:
            return {}


@auto_str
class ResourceData(ModelData[ResourceProperty, ResourceState]):
    stateType = ResourceState
    propertyType = ResourceProperty

    def __init__(self, resource: cm.ResourceModel, **kwargs) -> None:
        super(ResourceData, self).__init__(**kwargs)
        self.resource = resource
        self.__is_supplying: bool = False

    @staticmethod
    def initial_properties():
        return {ResourceProperty.Capacity: 1, ResourceProperty.Cooldown: timedelta(seconds=1)}

    @staticmethod
    def initial_state():
        return {ResourceState.InBusiness: False,
                ResourceState.CurrentlyAssigned: 0,
                ResourceState.OnCooldown: False,
                ResourceState.Disabled: False}

    @property
    def is_supplying(self) -> bool:
        return self.__is_supplying

    def assignment_changed(self, released: bool):
        # TODO what was cooldown needed for again?
        # if released:
        #    self.__state[ResourceState.OnCooldown] = True
        #    self.resource.cooldown(self.properties[ResourceProperty.Cooldown])
        self._state[ResourceState.CurrentlyAssigned] = len(self.resource.current_assignments)
        self._determine_status()

    def receive_event(self, event: ev_sys.DictUpdateEvent) -> None:
        super().receive_event(event)
        self._determine_status()

    def _determine_status(self):
        new_state = (not self._state[ResourceState.Disabled]) \
                    and self._state[ResourceState.InBusiness] \
                    and (not self._state[ResourceState.OnCooldown]) \
                    and self.properties[ResourceProperty.Capacity] > self._state[ResourceState.CurrentlyAssigned]
        if new_state is not self.is_supplying:
            self.__is_supplying = new_state
            self.resource.supply_changed()
