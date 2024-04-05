from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from qprsim.shared.base_classes import FrozenDict
from .event_system import UpdateEvent
from ..utils import time_utils

if TYPE_CHECKING:
    from .object_def import Carrier, ObjectType, ObjectId, AttributeLabel


@dataclass(unsafe_hash=True)
class AttributesChangeEvent(UpdateEvent):
    time: datetime
    new_values: FrozenDict[AttributeLabel, Any]

    def __init__(self, time: datetime, **kwargs) -> None:
        self.time = time
        self.new_values = FrozenDict(kwargs)

def attribute_initialization_event(**initial_attributes) -> AttributesChangeEvent:
    return AttributesChangeEvent(time_utils.MIN_TIMESTAMP, **initial_attributes)

@dataclass(unsafe_hash=True)
class ProcessingCompletionEvent(UpdateEvent):
    carrier: Carrier
    info: FrozenDict[str, Any]

    def __init__(self, carrier: Carrier, **kwargs) -> None:
        self.carrier = carrier
        self.info = FrozenDict(kwargs)


@dataclass(unsafe_hash=True)
class ObjectArrivalEvent(UpdateEvent):
    source: str
    actual_arrival_index: int
    scheduled_arrival_index: int
    proposed_object_id: ObjectId
    time: datetime
