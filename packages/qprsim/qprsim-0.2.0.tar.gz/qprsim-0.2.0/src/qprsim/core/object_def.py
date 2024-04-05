from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TYPE_CHECKING

from qprsim.core import event_system as ev_sys
from qprsim.shared.base_classes import FrozenDict, StaticHashable
from qprsim.utils import time_utils

if TYPE_CHECKING:
    from qprsim.core import oc_events as oce

ObjectId = str
ObjectType = str
EventId = str
ActivityType = str
Qualifier = str
AttributeLabel = str


class Object(ev_sys.Updatable, StaticHashable):

    def __init__(self, object_id: ObjectId, object_type: ObjectType) -> None:
        super(Object, self).__init__(hash_obj=object_id)
        self.object_id: ObjectId = object_id
        self.object_type: ObjectType = object_type
        self.attributes: dict[AttributeLabel, Any] = {}
        self.events = []
        self.attribute_events: list[oce.AttributesChangeEvent] = []

    @classmethod
    def with_initial_attributes(cls, object_id: ObjectId, object_type: ObjectType, initialization_timestamp=time_utils.MIN_TIMESTAMP, **initial_attributes):
        o = Object(object_id, object_type)
        o.log_attribute_change(oce.AttributesChangeEvent(initialization_timestamp, **initial_attributes))
        return o

    def log_event(self, event):
        self.events.append(event)

    def log_attribute_change(self, attribute_change_event: oce.AttributesChangeEvent):
        self.attribute_events.append(attribute_change_event)
        self.attributes.update(attribute_change_event.new_values)

    def receive_event(self, event: oce.AttributesChangeEvent):
        self.log_attribute_change(event)

    def __str__(self):
        return f'Object(id={self.object_id}, type={self.object_type}, {self.attributes})'


O2ORelation = set[tuple[Object, Object]]
QualifiedO2ORelations = dict[Qualifier, O2ORelation]


@dataclass(unsafe_hash=True)
class ObjectEvent:
    event_id: EventId = field(init=False)  # is set later on: problematic with supposed immutability
    activity_type: ActivityType
    time: datetime
    objects: FrozenDict[Qualifier, frozenset[Object]] = field(default_factory=FrozenDict)
    attributes: FrozenDict[str, Any] = field(default_factory=FrozenDict)

    def __init__(self, activity_type: ActivityType, time: datetime, objects: dict[Qualifier, set[Object]],
                 **attributes) -> None:
        self.activity_type = activity_type
        self.time = time
        self.objects = FrozenDict({q: frozenset(os) for q, os in objects.items()}) if objects is not None else FrozenDict()
        self.attributes = FrozenDict(attributes)


class ObjectMap:

    def __init__(self) -> None:
        self.objects = set()
        self.qualified_o2o: QualifiedO2ORelations = defaultdict(set)

    def register_new_relations(self, **new_relations):
        new_relations: QualifiedO2ORelations
        for q, R in new_relations.items():
            for t in R:
                self.qualified_o2o[q].add(t)

    def register_new_objects(self, *objs):
        for o in objs:
            self.objects.add(o)


class Carrier(StaticHashable):

    def __init__(self, *objects) -> None:
        super().__init__(frozenset((o.object_id for o in objects)))
        self._contents = frozenset(objects)

    @property
    def contents(self) -> frozenset[Object]:
        return self._contents

    def derive_type(self) -> Counter[ObjectType]:
        return Counter(o.object_type for o in self._contents)

    def derive_type_map(self) -> dict[ObjectType, set[Object]]:
        res = defaultdict(set)
        for o in self.contents:
            res[o.object_type].add(o)
        return res

    def get_of_type(self, object_type: ObjectType) -> set[Object]:
        return {o for o in self._contents if o.object_type == object_type}

    def get_first_of_type(self, object_type: ObjectType) -> Object:
        return next(iter(self.get_of_type(object_type)))

    def as_singleton(self) -> Object:
        it = iter(self.contents)
        return next(it)

    def __iter__(self):
        return iter(self.contents)

    def __str__(self):
        return f'Carrier({list(map(str, self.contents))})'
