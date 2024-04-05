from __future__ import annotations

import dataclasses
import datetime
import enum
from abc import abstractmethod, ABC
from copy import copy
from dataclasses import dataclass, field
from typing import Callable, Any, List, Iterator, Sequence

from qprsim.shared.base_classes import FrozenDict


class AttributeLevel(enum.Enum):
    Case = 'case'
    Event = 'event'


@dataclass(unsafe_hash=True)
class CaseEvent:
    activity: str
    resource: str
    timestamp: datetime.datetime
    lifecycle: str = 'complete'
    attributes: FrozenDict[str, Any] = field(default_factory=FrozenDict)

    def __init__(self, activity: str, resource: str, timestamp: datetime.datetime, lifecycle: str = 'complete',
                 **attributes) -> None:
        self.activity = activity
        self.resource = resource
        self.timestamp = timestamp
        self.lifecycle = lifecycle
        self.attributes = FrozenDict(attributes)

    def __str__(self) -> str:
        return f'{self.activity}[{self.lifecycle}] @{self.timestamp.strftime("%Y-%m-%d %H:%M")} by {self.resource} with {self.attributes}'

    def __copy__(self):
        return CaseEvent(**{k: copy(v) for k, v in dataclasses.asdict(self).items()})

    def map(self, **changes) -> CaseEvent:
        init_args = dataclasses.asdict(self)
        old_attrs = init_args.pop('attributes')
        init_args.update(changes.pop('attributes') if 'attributes' in changes else old_attrs)
        init_args.update(changes)
        return CaseEvent(**{k: copy(v) for k, v in init_args.items()})


class AbstractCase(Sequence):

    def __init__(self, case_id: str) -> None:
        super(AbstractCase, self).__init__()
        self.case_id = case_id

    @abstractmethod
    def add_event(self, event: CaseEvent) -> None:
        ...

    @abstractmethod
    def set_case_attribute(self, key: str, value: Any):
        ...

    def project(self, condition: Callable[[CaseEvent], bool] = None,
                projection: Callable[[CaseEvent], Any] = None, attr_filter: set[str] = None,
                case_id_redefinition: Callable[[Case], str] = None) -> AbstractCase:
        ...

    def filter(self, condition: Callable[[CaseEvent], bool]) -> AbstractCase:
        ...

    @abstractmethod
    def get_case_attr_value(self, attr_name: str) -> Any: ...

    @abstractmethod
    def get_latest_event_attr_value(self, attr_name: str) -> Any: ...


class Case(AbstractCase, ABC):

    def __init__(self, case_id: str, **kwargs) -> None:
        super().__init__(case_id)
        self.attributes = kwargs

    def set_case_attribute(self, key: str, value: Any):
        self.attributes[key] = value

    def get_case_attr_value(self, attr_name: str) -> Any:
        return self.attributes.get(attr_name)


# TODO StaticHashable usage, see sim_model
class BaseCase(Case):

    def __init__(self, case_id: str, events: List[CaseEvent] = None, **case_attributes):
        super(BaseCase, self).__init__(case_id, **case_attributes)  # hash_obj=case_id)
        self.events = events if events else []

    def __getitem__(self, i: int) -> CaseEvent:
        return self.events[i]

    def index(self, x: Any, start: int = ..., end: int = ...) -> int:
        return self.events.index(x, start, end)

    def count(self, x: Any) -> int:
        return self.events.count(x)

    def __contains__(self, x: object) -> bool:
        return x in self.events

    def __iter__(self) -> Iterator[CaseEvent]:
        return iter(self.events)

    def __reversed__(self) -> Iterator[CaseEvent]:
        return reversed(self.events)

    def __len__(self) -> int:
        return len(self.events)

    def add_event(self, event: CaseEvent) -> None:
        self.events.append(event)

    def project(self, condition: Callable[[CaseEvent], bool] = None,
                projection: Callable[[CaseEvent], Any] = None, attr_filter: set[str] = None,
                case_id_redefinition: Callable[[Case], str] = None) -> Case:
        projection = projection if projection else lambda ce: ce  # lambda ce: ce.activity
        condition = condition if condition else lambda ce: True  # lambda ce: ce.lifecycle == 'complete'
        projected_attrs = {k: self.attributes[k] for k in attr_filter if
                           k in self.attributes} if attr_filter is not None else self.attributes
        mapped_case_id = case_id_redefinition(self) if case_id_redefinition is not None else self.case_id
        return BaseCase(mapped_case_id, [projection(event) for event in self.events if condition(event)],
                        **projected_attrs)

    def filter(self, condition: Callable[[CaseEvent], bool]) -> Case:
        return BaseCase(self.case_id, [event for event in self.events if condition(event)], **self.attributes)

    def __str__(self) -> str:
        return f'Case(id={self.case_id}, attrs={self.attributes}: ' + ','.join(map(str, self.events)) + ')'

    def __repr__(self) -> str:
        return str(self)

    def get_latest_event_attr_value(self, attr_name: str) -> Any:
        for e in reversed(self):
            if attr_name in e.attributes:
                return e.attributes[attr_name]


class ChildCase(Case):

    def __init__(self, case_id: str, parent_case: Case, **own_case_attributes):
        super(ChildCase, self).__init__(case_id, **own_case_attributes)
        self.parent = parent_case

    def __str__(self) -> str:
        return f'ChildCase(id={self.case_id}, attrs={self.attributes}, parent={self.parent})'

    def __repr__(self):
        return str(self)

    def project(self, condition: Callable[[CaseEvent], bool] = None,
                projection: Callable[[CaseEvent], Any] = None, attr_filter: set[str] = None,
                case_id_redefinition: Callable[[Case], str] = None) -> Case:
        projected_attrs = {k: self.attributes[k] for k in attr_filter if
                           k in self.attributes} if attr_filter is not None else self.attributes
        mapped_case_id = case_id_redefinition(self) if case_id_redefinition is not None else self.case_id
        return ChildCase(mapped_case_id, self.parent.project(condition, projection), **projected_attrs)

    def filter(self, condition: Callable[[CaseEvent], bool]) -> Case:
        return ChildCase(self.case_id, self.parent.filter(condition), **self.attributes)

    def add_event(self, event: CaseEvent) -> None:
        self.parent.add_event(event)

    def get_latest_event_attr_value(self, attr_name: str) -> Any:
        return self.parent.get_latest_event_attr_value(attr_name)

    def __getitem__(self, index: int) -> CaseEvent:
        return self.parent.__getitem__(index)

    def index(self, x: Any, start: int = ..., end: int = ...) -> int:
        return self.parent.index(x, start, end)

    def count(self, x: Any) -> int:
        return self.parent.count(x)

    def __contains__(self, x: object) -> bool:
        return x in self.parent

    def __iter__(self) -> Iterator[CaseEvent]:
        return iter(self.parent)

    def __reversed__(self) -> Iterator[CaseEvent]:
        return reversed(self.parent)

    def __len__(self) -> int:
        return len(self.parent)


def create_case(case_id, initial_events=None, **case_attributes) -> Case:
    return BaseCase(case_id, initial_events, **case_attributes)


def create_child(parent: Case, sub_id: str, copy_parent_attrs=False, **kwargs) -> ChildCase:
    reserved_keys = {'parent_case', 'sub_id'}
    initial_attrs = {k: v for k, v in kwargs.items() if k not in reserved_keys}
    if copy_parent_attrs:
        initial_attrs |= {k: v for k, v in parent.attributes.items() if k not in reserved_keys}
    return ChildCase(parent.case_id + '.' + sub_id, parent_case=parent, sub_id=sub_id, **initial_attrs)
