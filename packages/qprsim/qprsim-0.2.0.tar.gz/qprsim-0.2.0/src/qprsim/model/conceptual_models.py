from __future__ import annotations

import logging
from abc import abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import Set, TYPE_CHECKING, Any, Hashable

from qprsim.core import case as sc, event_system as ev_sys
from . import model_data as mdata
from .model_traits import WithModelData, WithEventQueue, WithResourceManager
from ..shared.shared_traits import WithLabel

if TYPE_CHECKING:
    from qprsim.core import managers


class ResourceToken:
    pass


@dataclass(unsafe_hash=True)
class Assignment(ResourceToken):
    activity: ResourceUser
    task: Hashable
    # timestamp: datetime


class ResourceProvider:

    @abstractmethod
    def provide_resource(self, user: ResourceUser, task: Hashable) -> ResourceToken: ...

    @abstractmethod
    def release_resource(self, token: ResourceToken): ...

    @property
    @abstractmethod
    def is_supplying(self) -> bool: ...


class ResourceUser:
    @abstractmethod
    def take_resource_from(self, resource: ResourceProvider): ...

    @property
    @abstractmethod
    def is_demanding(self) -> bool: ...


class ResourceModel(ResourceProvider, WithResourceManager, WithEventQueue, WithLabel, WithModelData[mdata.ResourceData]):

    def __init__(self, label: str, event_queue: ev_sys.EventQueue, resource_manager: managers.ResourceManager,
                 data: mdata.ResourceData = None) -> None:
        super(ResourceModel, self).__init__(label=label, data=data, event_queue=event_queue, resource_manager=resource_manager)
        self.current_assignments: set[Assignment] = set()

    @DeprecationWarning
    def cooldown(self, delta: timedelta):
        # not happy with this
        logging.info(f'{self.label} is cooling down for {delta}')
        self.event_queue.offer_delayed(delta, ev_sys.Callback(self.data.receive_event,
                                                              ev_sys.DictUpdateEvent('on_cooldown', False)))

    def provide_resource(self, user: ResourceUser, task: Hashable) -> Assignment:
        ass = Assignment(user, task)
        self.current_assignments.add(ass)
        self.data.assignment_changed(released=False)
        return ass

    def release_resource(self, ass: Assignment):
        self.current_assignments.remove(ass)
        self.data.assignment_changed(released=True)

    @property
    def is_supplying(self) -> bool:
        return self.data.is_supplying

    def supply_changed(self):
        self.resource_manager.resource_supply_change(self, self.is_supplying)

    def __repr__(self) -> str:
        return f'ResourceModel({self.label})'

    def __str__(self):
        return self.label
