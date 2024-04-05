from collections import defaultdict

from . import object_def as obd


class ObjectManager:
    def __init__(self) -> None:
        super().__init__()
        self.object_map = obd.ObjectMap()
        self.active_objects: set[obd.Object] = set()
        self.retired_objects: set[obd.Object] = set()
        self.object_counts: dict[obd.ObjectType, int] = defaultdict(int)
        self.object_id_requests: dict[obd.ObjectType, int] = defaultdict(int)

    def generate_unique_idx(self, object_type: obd.ObjectType) -> int:
        i = self.object_id_requests[object_type]
        self.object_id_requests[object_type] += 1
        return i

    def generate_unique_id(self, object_type: obd.ObjectType) -> obd.ObjectId:
        return f'{object_type}:{self.generate_unique_idx(object_type)}'

    def birth(self, *objs: obd.Object):
        for obj in objs:
            self.active_objects.add(obj)
            self.object_counts[obj.object_type] += 1
        self.object_map.register_new_objects(*objs)

    def relate(self, **new_relations: obd.QualifiedO2ORelations):
        self.object_map.register_new_relations(**new_relations)

    def retire(self, *objs: obd.Object):
        for obj in objs:
            self.active_objects.remove(obj)
            self.retired_objects.add(obj)


class SynchronizationManager:
    ...


class EventManager:

    def __init__(self) -> None:
        self._events = []

    def generate_unique_id(self) -> obd.EventId:
        return f'event:{len(self._events)}'

    def log(self, event: obd.ObjectEvent):
        event.event_id = self.generate_unique_id()
        self._events.append(event)

    @property
    def collected_events(self) -> list[obd.ObjectEvent]:
        return self._events
