from __future__ import annotations

from abc import ABC
from typing import Generic, TYPE_CHECKING

from .model_data import ModelDataType

if TYPE_CHECKING:
    from qprsim.core import event_system as ev_sys
    from qprsim.execution import SimulationContext
    from qprsim.core import managers


class WithEventQueue:

    def __init__(self, event_queue: ev_sys.EventQueue, *args, **kwargs) -> None:
        super(WithEventQueue, self).__init__(*args, **kwargs)
        self.event_queue = event_queue

    @property
    def event_queue(self) -> ev_sys.EventQueue:
        return self.__event_queue

    @event_queue.setter
    def event_queue(self, value) -> None:
        assert value is not None
        self.__event_queue = value


class WithModelData(Generic[ModelDataType], ABC):

    def __init__(self, data: ModelDataType = None, *args, **kwargs) -> None:
        super(WithModelData, self).__init__(*args, **kwargs)
        self.__data = data

    @property
    def data(self) -> ModelDataType:
        return self.__data

    @data.setter
    def data(self, value: ModelDataType):
        assert value is not None
        self.__data = value


class WithSimulationContext:

    def __init__(self, simulation_context: SimulationContext, **kwargs) -> None:
        super(WithSimulationContext, self).__init__(**kwargs)
        self.simulation_context = simulation_context


class WithActivityManager:

    def __init__(self, activity_manager: managers.ActivityManager, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__activity_manager = activity_manager

    @property
    def activity_manager(self) -> managers.ActivityManager:
        return self.__activity_manager

    @activity_manager.setter
    def activity_manager(self, value: managers.ActivityManager):
        assert value is not None
        self.__activity_manager = value


class WithResourceManager:

    def __init__(self, resource_manager: managers.ResourceManager, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__resource_manager = resource_manager

    @property
    def resource_manager(self) -> managers.ResourceManager:
        return self.__resource_manager

    @resource_manager.setter
    def resource_manager(self, value: managers.ResourceManager):
        assert value is not None
        self.__resource_manager = value
