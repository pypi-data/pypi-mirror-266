from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

import qprsim.core.event_system as ev_sys
from qprsim.config.oc_model_configuration import OCArrivalProcessConfig
from qprsim.execution.oc_simulation import OCSimulationModel
from qprsim.utils import time_utils

if TYPE_CHECKING:
    import qprsim.model.model_parameters as params
    from qprsim.shared.enums import ResourceProperty, OCActivityProperty, OCObjectBirthplaceProperty


@dataclass(unsafe_hash=True)
class BusinessHoursAdaptationEvent(ev_sys.Event):
    target: str
    new_business_hours: params.BusinessHours


@dataclass(unsafe_hash=True)
class ArrivalProcessAdaptationEvent(ev_sys.Event):
    ...


@dataclass(unsafe_hash=True)
class ArrivalProcessInsertionEvent(ArrivalProcessAdaptationEvent):
    new_process: str
    new_config: OCArrivalProcessConfig


@dataclass(unsafe_hash=True)
class ArrivalProcessRemovalEvent(ArrivalProcessAdaptationEvent):
    old_process: str


@dataclass(unsafe_hash=True)
class ArrivalProcessSwapEvent(ArrivalProcessAdaptationEvent):
    old_process: str
    new_process: str
    new_config: OCArrivalProcessConfig


class ButWhatIf:

    def __init__(self, sim_model: OCSimulationModel) -> None:
        self.sim_model = sim_model
        self.scheduling_manager = sim_model.scheduling_manager
        self.working_set = {}
        self.scheduled_changes = []
        self.activity_datas = dict(sim_model.scheduling_manager.activity_datas)
        self.resource_datas = dict(sim_model.scheduling_manager.resource_datas)
        self.birthplace_datas = {k: v.data for k, v in sim_model.scheduling_manager.birthplaces.items()}

    def add(self, when, callback, event):
        self.scheduled_changes.append(ev_sys.TimedCallback(time_utils.make_timezone_aware(when), callback, event))

    def hot(self, what):
        self.scheduling_manager.perform_hot_change(what)

    def schedule_activity_property_change(self, when: datetime.datetime, activity: str, key: OCActivityProperty,
                                          new_value: Any) -> None:
        self.add(when, self.activity_datas[activity].receive_event, ev_sys.DictUpdateEvent(key, new_value))

    def schedule_resource_property_change(self, when: datetime.datetime, resource: str, key: ResourceProperty,
                                          new_value: Any) -> None:
        self.add(when, self.resource_datas[resource].receive_event,
                 ev_sys.DictUpdateEvent(key, new_value))

    def schedule_birthplace_property_change(self, when: datetime.datetime, birthplace: str, key: OCObjectBirthplaceProperty,
                                            new_value: Any) -> None:
        self.add(when, self.birthplace_datas[birthplace].receive_event,
                 ev_sys.DictUpdateEvent(key, new_value))

    def _activity_business_hours_change(self, event: BusinessHoursAdaptationEvent):
        def change():
            self.scheduling_manager.set_activity_business_hours(event.target, event.new_business_hours)

        self.hot(change)

    def _resource_business_hours_change(self, event: BusinessHoursAdaptationEvent):
        def change():
            self.scheduling_manager.set_resource_business_hours(event.target, event.new_business_hours)

        self.hot(change)

    def _arrival_process_change(self, event: ArrivalProcessAdaptationEvent):
        def change():
            if isinstance(event, ArrivalProcessRemovalEvent):
                self.scheduling_manager.remove_arrival_process(event.old_process)
            elif isinstance(event, ArrivalProcessInsertionEvent):
                self.scheduling_manager.add_arrival_process(event.new_process, event.new_config)
            elif isinstance(event, ArrivalProcessSwapEvent):
                self.scheduling_manager.remove_arrival_process(event.old_process)
                self.scheduling_manager.add_arrival_process(event.new_process, event.new_config)

        self.hot(change)

    def schedule_activity_business_hours_change(self, when: datetime.datetime, resource: str,
                                                new_business_hours: params.BusinessHours) -> None:
        self.add(when, self._activity_business_hours_change, BusinessHoursAdaptationEvent(resource, new_business_hours))

    def schedule_resource_business_hours_change(self, when: datetime.datetime, resource: str,
                                                new_business_hours: params.BusinessHours) -> None:
        self.add(when, self._resource_business_hours_change, BusinessHoursAdaptationEvent(resource, new_business_hours))

    def schedule_arrival_process_removal(self, when: datetime.datetime, arrival_label: str):
        self.add(when, self._arrival_process_change, ArrivalProcessRemovalEvent(arrival_label))

    def schedule_arrival_process_insertion(self, when: datetime.datetime, arrival_label: str,
                                           config: OCArrivalProcessConfig):
        self.add(when, self._arrival_process_change, ArrivalProcessInsertionEvent(arrival_label, config))

    def schedule_arrival_process_swap(self, when: datetime.datetime, arrival_label: str,
                                      config: OCArrivalProcessConfig):
        self.add(when, self._arrival_process_change, ArrivalProcessSwapEvent(arrival_label, arrival_label, config))

    def apply(self):
        for timed_callback in self.scheduled_changes:
            self.sim_model.event_queue.offer(timed_callback)
