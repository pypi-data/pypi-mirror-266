from qprsim.core import oc_managers as ocm


class WithEventManager:

    def __init__(self, event_manager: ocm.EventManager, *args, **kwargs) -> None:
        super(WithEventManager, self).__init__(*args, **kwargs)
        self.__event_manager = event_manager

    @property
    def event_manager(self) -> ocm.EventManager:
        return self.__event_manager

    @event_manager.setter
    def event_manager(self, value) -> None:
        assert value is not None
        self.__event_manager = value


class WithObjectManager:

    def __init__(self, object_manager: ocm.ObjectManager, *args, **kwargs) -> None:
        super(WithObjectManager, self).__init__(*args, **kwargs)
        self.__object_manager = object_manager

    @property
    def object_manager(self) -> ocm.ObjectManager:
        return self.__object_manager

    @object_manager.setter
    def object_manager(self, value) -> None:
        assert value is not None
        self.__object_manager = value


class WithSynchronizationManager:

    def __init__(self, sync_manager: ocm.SynchronizationManager, *args, **kwargs) -> None:
        super(WithSynchronizationManager, self).__init__(*args, **kwargs)
        self.__sync_manager = sync_manager

    @property
    def sync_manager(self) -> ocm.SynchronizationManager:
        return self.__sync_manager

    @sync_manager.setter
    def sync_manager(self, value) -> None:
        assert value is not None
        self.__sync_manager = value
