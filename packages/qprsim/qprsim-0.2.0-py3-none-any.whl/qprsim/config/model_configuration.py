from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Set, Type, TYPE_CHECKING, Any, ClassVar

import numpy

from qprsim.model import graph_models as gm
from qprsim.model.model_parameters import InterArrivalSampler, BusinessHours, QueueingDiscipline, \
    ProcessingTimeSampler, \
    DelaySampler, ResourcePerformance, CaseClassifier, EventAttributeGenerator, AttributeGenerator
from qprsim.shared.base_classes import auto_str, FrozenDict
from qprsim.utils.time_utils import make_timezone_aware

from qprsim.shared.enums import ActivityProperty, ResourceProperty

if TYPE_CHECKING:
    pass


@auto_str
@dataclass(unsafe_hash=True)
class ArrivalProcessConfig:
    first_arrival: datetime
    inter_arrivals: InterArrivalSampler
    business_hours: BusinessHours = None
    last_arrival: datetime = None
    attribute_generator: AttributeGenerator = None

    def __init__(self, first_arrival: datetime, inter_arrivals: InterArrivalSampler,
                 business_hours: BusinessHours = None, last_arrival: datetime = None,
                 attribute_generator: AttributeGenerator = None) -> None:
        self.first_arrival = make_timezone_aware(first_arrival)
        self.inter_arrivals = inter_arrivals
        self.business_hours = business_hours
        self.last_arrival = make_timezone_aware(last_arrival) if last_arrival is not None else None
        self.attribute_generator = attribute_generator


@auto_str
@dataclass(unsafe_hash=True)
class ActivityConfig:
    queueing_discipline: QueueingDiscipline
    processing_time_sampler: ProcessingTimeSampler
    business_hours: BusinessHours = None
    delay_sampler: DelaySampler = None
    attribute_generator: EventAttributeGenerator = None
    property_dict: FrozenDict[ActivityProperty, Any] = None

    def __init__(self, queueing_discipline: QueueingDiscipline, processing_time_sampler: ProcessingTimeSampler,
                 business_hours: BusinessHours = None, delay_sampler: DelaySampler = None,
                 attribute_generator: EventAttributeGenerator = None,
                 property_dict: dict[ActivityProperty, Any] = None) -> None:
        self.queueing_discipline = queueing_discipline
        self.processing_time_sampler = processing_time_sampler
        self.delay_sampler = delay_sampler
        self.business_hours = business_hours
        self.attribute_generator = attribute_generator
        self.property_dict = FrozenDict(
            property_dict) if property_dict is not None else None


@auto_str
@dataclass(unsafe_hash=True)
class ResourceConfig:
    capacity: int
    business_hours: BusinessHours = None
    performance: ResourcePerformance = None
    property_dict: FrozenDict[ResourceProperty, Any] = None

    def __init__(self, capacity: int, business_hours: BusinessHours = None,
                 performance: ResourcePerformance = None,
                 property_dict: dict[ResourceProperty, Any] = None) -> None:
        self.business_hours = business_hours
        props = {}
        if property_dict is not None:
            props.update(property_dict)
        props[ResourceProperty.Capacity] = capacity
        if performance is not None:
            props[ResourceProperty.Performance] = performance
        self.capacity = capacity
        self.performance = performance
        self.property_dict = FrozenDict(props)


InfiniteResourceConfig = ResourceConfig(numpy.inf)


@auto_str
@dataclass(unsafe_hash=True)
class ModelHaverConfig:
    model_class: ClassVar[Type[gm.SimulationNodeModel]]
    requires_unsafe_access: ClassVar[bool] = False
    model_parameters: dict[str, Any]

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.model_parameters = kwargs

    def instantiate_model(self, **more_kwargs):
        kwargs = self.model_parameters
        return self.model_class(**kwargs, **more_kwargs)


class DecisionConfig(ModelHaverConfig):
    model_class = gm.DecisionModel

    def __init__(self, classifier: CaseClassifier, **kwargs) -> None:
        super().__init__(classifier=classifier, **kwargs)


class DelayConfig(ModelHaverConfig):
    model_class = gm.DelayModel
    requires_unsafe_access = True

    def __init__(self, delay_sampler: DelaySampler, **kwargs) -> None:
        super().__init__(delay_sampler=delay_sampler, **kwargs)


def arbitraryMHC(model_class_def: Type[gm.SimulationNodeModel], requires_unsafe_access=False,
                 **kwargs) -> ModelHaverConfig:
    a = requires_unsafe_access

    class ArbMhc(ModelHaverConfig):
        model_class = model_class_def
        requires_unsafe_access = a

    return ArbMhc(**kwargs)


@auto_str
@dataclass(unsafe_hash=True)
class MappingConfig:
    assignable_resources: dict[str, set[str]]
    propensities: dict[str, dict[str, float]] = None

    def __init__(self, assignable_resources: dict[str, set[str]],
                 propensities: dict[str, dict[str, float]] = None) -> None:
        self.assignable_resources = assignable_resources
        if propensities is None:
            propensities = {}
            for a, rs in assignable_resources.items():
                propensities[a] = {}
                for r in rs:
                    propensities[a][r] = 1
        self.propensities = propensities


@dataclass(unsafe_hash=True)
class GenericModelConfiguration:
    arrivals: dict[str, ArrivalProcessConfig]
    activities: dict[str, ActivityConfig]
    resources: dict[str, ResourceConfig]
    aux_model_configs: dict[str, ModelHaverConfig]
    mapping: MappingConfig

    def __str__(self) -> str:
        return 'Arrivals:' + ('\n' if len(self.arrivals) > 0 else ' n/a') \
            + '\n'.join(str(l) + ': ' + str(ar) for l, ar in self.arrivals.items()) + '\n' \
            + 'Activities:' + ('\n' if len(self.activities) > 0 else ' n/a') \
            + '\n'.join(str(a) + ': ' + str(ac) for a, ac in self.activities.items()) + '\n' \
            + 'Resources:' + ('\n' if len(self.resources) > 0 else ' n/a') \
            + '\n'.join(str(r) + ': ' + str(rc) for r, rc in self.resources.items()) + '\n' \
            + 'Auxiliary Models:' + ('\n' if len(self.aux_model_configs) > 0 else ' n/a') \
            + '\n'.join(str(a) + ': ' + str(aux) for a, aux in self.aux_model_configs.items()) + '\n' \
            + str(self.mapping)
