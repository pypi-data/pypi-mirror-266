from __future__ import annotations

import random
from abc import abstractmethod
from datetime import datetime, timedelta, time
from typing import List, Tuple, Optional, Dict, Any, Callable
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import scipy.stats

import qprsim.model.model_parameters as params
import qprsim.model.oc_model_parameters as ocpa
from qprsim.utils import time_utils
from qprsim.core.case import AttributeLevel
from qprsim.shared.base_classes import FrozenDict
from qprsim.shared.enums import ResourceProperty, ResourceState, Weekdays

if TYPE_CHECKING:
    import qprsim.core.case as sc
    import qprsim.core.object_def as obd
    from qprsim.model import conceptual_models as cm


class FixedRelative(params.QueueingDiscipline, ocpa.OCQueueingDiscipline):

    def __init__(self, relative_index) -> None:
        super().__init__()
        self.relative_index = relative_index

    def select(self, queue: List[Tuple[datetime, sc.Case | obd.Carrier]]) -> int:
        return int(self.relative_index * (len(queue) - 1))

    def __str__(self) -> str:
        return f'FixedRelativeQueueing(rel_index={self.relative_index})'


class RandomQueueing(params.QueueingDiscipline, ocpa.OCQueueingDiscipline):

    def select(self, queue: List[Tuple[datetime, sc.Case | obd.Carrier]]) -> int:
        return random.randint(0, len(queue) - 1)

    def __str__(self) -> str:
        return f'Random'


Fifo = FixedRelative(0)
Fifo.__str__ = lambda self: 'Fifo'
Lifo = FixedRelative(1)
Lifo.__str__ = lambda self: 'Lifo'
Random = RandomQueueing()


class StaticAttributeGenerator(params.AttributeGenerator):

    def __init__(self, static_attribute_dict: dict[str, Any] = None, **kwargs) -> None:
        super(StaticAttributeGenerator, self).__init__()
        if static_attribute_dict is None:
            static_attribute_dict = {}
        static_attribute_dict.update(kwargs)
        self.static_attribute_dict = FrozenDict(static_attribute_dict)

    def generate(self, *args, **kwargs) -> dict[str, Any]:
        return {k: (v() if isinstance(v, Callable) else v) for k, v in self.static_attribute_dict.items()}

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.static_attribute_dict == o.static_attribute_dict

    def __hash__(self) -> int:
        return hash(self.static_attribute_dict)

    def __str__(self) -> str:
        return f'StaticEventAttributeGenerator({self.static_attribute_dict})'


class AttributeGeneratorEnsemble(params.AttributeGenerator):

    def __init__(self, ensemble: dict[str, params.AttributeGenerator] = None, **kwargs) -> None:
        super(AttributeGeneratorEnsemble, self).__init__()
        if ensemble is None:
            ensemble = {}
        ensemble.update(kwargs)
        self.ensemble = ensemble

    @abstractmethod
    def _choose_generator(self, *args, **kwargs) -> params.AttributeGenerator | None: ...

    def generate(self, *args, **kwargs) -> dict[str, Any]:
        generator = self._choose_generator(*args, **kwargs)
        return generator.generate(*args, **kwargs) if generator is not None else {}


class LambdaAttributeGenerator(params.AttributeGenerator):

    def __init__(self, lambd: Callable[..., dict[str, Any] | tuple[str, Any]]) -> None:
        super().__init__()
        self.lambd = lambd

    def generate(self, *args, **kwargs) -> dict[str, Any]:
        res = self.lambd(*args, **kwargs)
        if not isinstance(res, dict):
            return {res[0]: res[1]} if isinstance(res, tuple) else {}
        else:
            return res

    def __str__(self) -> str:
        return f'LambdaAttributeGenerator({self.lambd})'


class StochasticAttributeGenerator(AttributeGeneratorEnsemble):

    def __init__(self, probabilities: dict[str, float] = None, *args, **kwargs) -> None:
        super(StochasticAttributeGenerator, self).__init__(*args, **kwargs)
        if probabilities is None:
            probabilities = {k: 1 / len(self.ensemble) for k in self.ensemble}
        assert self.ensemble.keys() == probabilities.keys()
        assert sum(probabilities.values()) >= 1.0
        p = []
        choices = []
        for k, prob in probabilities.items():
            p.append(prob)
            choices.append(k)
        self.p = tuple(p)
        self.choices = tuple(choices)

    @classmethod
    def from_lists(cls, probabilities: list[float],
                   generators: list[params.AttributeGenerator]) -> StochasticAttributeGenerator:
        return cls({str(i): p for i, p in enumerate(probabilities)}, {str(i): g for i, g in enumerate(generators)})

    @classmethod
    def single_attribute(cls, attr_name: str, value_probabilities: dict[str, float]):
        return cls(value_probabilities, {v: StaticAttributeGenerator({attr_name: v}) for v in value_probabilities})

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and super().__eq__(o) and self.choices == o.choices and self.p == o.p

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.choices, self.p))

    def __str__(self) -> str:
        return f'StochasticEventAttributeGenerator(p={self.p}, choices={self.choices})'

    def _choose_generator(self, *args, **kwargs) -> params.AttributeGenerator | None:
        return self.ensemble[np.random.choice(self.choices, p=self.p)]


class ActivityAttributeGenerator(AttributeGeneratorEnsemble, params.EventAttributeGenerator):

    def generate(self, case: sc.Case, *args, **kwargs) -> dict[str, Any]:
        return super().generate(case=case, *args, **kwargs)

    def _choose_generator(self, lifecycle: str = None, *args, **kwargs) -> params.EventAttributeGenerator | None:
        return self.ensemble[lifecycle] if lifecycle in self.ensemble else None


class AttributeGeneratorUnion(params.AttributeGenerator):

    def __init__(self, *generators) -> None:
        super(AttributeGeneratorUnion, self).__init__()
        self.gens = generators

    def generate(self, *args, **kwargs) -> dict[str, Any]:
        result = {}
        for g in self.gens:
            result.update(g.generate(*args, **kwargs))
        return result


class DistSampler(params.ProcessingTimeSampler, params.DelaySampler, params.InterArrivalSampler, ocpa.OCProcessingTimeSampler):

    def __init__(self, distribution, dist_kwargs, unit='m') -> None:
        super().__init__()
        self.unit = unit
        self.dist_kw_args = FrozenDict(dist_kwargs)
        self.distribution = distribution
        self.dist = distribution(**dist_kwargs)

    def sample(self, *args, **kwargs) -> timedelta:
        val = self.dist.rvs()
        return pd.Timedelta(max(int(val), 1), unit=self.unit)

    def __eq__(self, o: object) -> bool:
        return isinstance(o,
                          self.__class__) and self.distribution == o.distribution and self.dist_kw_args == o.dist_kw_args and self.unit == o.unit

    def __hash__(self) -> int:
        return hash((self.distribution, self.dist_kw_args, self.unit))

    def __str__(self) -> str:
        return f'DistSampler({self.distribution.name}({self.dist_kw_args}) {self.unit})'


def ExpSampler(inter, unit='m'):
    return DistSampler(scipy.stats.expon, {'scale': inter}, unit=unit)


def NormSampler(mu, scale: float = 1, unit='m'):
    return DistSampler(scipy.stats.norm, {'loc': mu, 'scale': scale}, unit=unit)


def LogNormSampler(mu, unit='m'):
    return DistSampler(scipy.stats.lognorm, {'scale': np.exp(mu)}, unit=unit)


def fitted_expon(values, unit='m'):
    fit = scipy.stats.expon.fit(values)
    return DistSampler(scipy.stats.expon, {'loc': fit[0], 'scale': fit[1]}, unit=unit)


class EmpiricalSampler(params.ProcessingTimeSampler, params.DelaySampler, params.InterArrivalSampler, ocpa.OCProcessingTimeSampler):

    def __init__(self, percentiles_df: pd.DataFrame, use_linear_combination=True, k=None) -> None:
        super().__init__()
        self.use_linear_combination = use_linear_combination
        if k is not None:
            percentiles_df = EmpiricalSampler.discretize(percentiles_df, k=k)
        self.percentiles = tuple(percentiles_df.reset_index(drop=True).values)
        self.k = len(percentiles_df)

    def sample(self, *args, **kwargs):
        m = np.random.rand()
        m_k = m * (self.k - 1)
        if self.use_linear_combination:
            lower_i = int(np.floor(m_k))
            upper_i = int(np.ceil(m_k))
            return pd.Timedelta(
                self.percentiles[lower_i] * (m_k - lower_i) + self.percentiles[upper_i] * (upper_i - m_k))
        else:
            return pd.Timedelta(self.percentiles[int(np.rint(m_k))])

    @staticmethod
    def discretize(data_df, k=10):
        return data_df.quantile([i / k for i in range(k + 1)])

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) \
            and self.use_linear_combination == o.use_linear_combination \
            and self.percentiles == o.percentiles and self.k == o.k

    def __hash__(self) -> int:
        return hash((self.use_linear_combination, self.percentiles, self.k))

    def __str__(self) -> str:
        return f'EmpiricalSampler(percentiles={list(self.percentiles)}, linear_comb={self.use_linear_combination})'


class StaticSampler(params.ProcessingTimeSampler, params.DelaySampler, params.InterArrivalSampler, ocpa.OCProcessingTimeSampler):

    def __init__(self, value: timedelta) -> None:
        super().__init__()
        self.value = value

    def sample(self, *args, **kwargs) -> timedelta:
        return self.value

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.value == o.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return f'StaticSampler({self.value})'


ZeroSampler = StaticSampler(timedelta(seconds=0))
ZeroSampler.__str__ = lambda self: 'ZeroSampler'
EpsilonSampler = StaticSampler(timedelta(seconds=1))
EpsilonSampler.__str__ = lambda self: 'EpsilonSampler'


class ConstantPerformance(params.ResourcePerformance):

    def __init__(self, value: float) -> None:
        super().__init__()
        # assert 0 <= value <= 1
        self.value = value

    def performance(self, utilization: float):
        return self.value

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.value == o.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return f'ConstantPerformance({self.value})'


class ConstantPeakPerformance(ConstantPerformance):

    def __init__(self) -> None:
        super().__init__(1.0)

    def __str__(self) -> str:
        return 'ConstantPeakPerformance'


PeakPerformance = ConstantPeakPerformance()


class LinearYerkesDodson(params.ResourcePerformance):
    """
    badly linearized yerkes-dodson parabola
    """

    def __init__(self, peak) -> None:
        super().__init__()
        assert 0 <= peak <= 1
        self.peak = peak

    def performance(self, arousal):
        if arousal <= self.peak:
            return (self.peak - arousal) / self.peak
        else:
            return (arousal - self.peak) / (1 - self.peak)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.peak == o.peak

    def __hash__(self):
        return hash(self.peak)

    def __str__(self):
        return f'LinearYerkesDodson(peak={self.peak})'


class ResourceDependentPTSampler(params.ProcessingTimeSampler, ocpa.OCProcessingTimeSampler):

    def __init__(self, base_sampler: params.ProcessingTimeSampler, resource_skills: Dict[str, float] = None,
                 use_resource_performance: bool = False) -> None:
        super().__init__()
        self.base_sampler = base_sampler
        if resource_skills is None:
            resource_skills = FrozenDict()
        # assert all(0 <= s <= 1 for s in resource_skills.values())
        self.resource_skills = resource_skills
        self.use_resource_performance = use_resource_performance
        self.lookup = lambda r: 1 / self.resource_skills.get(r.label, 1)
        if use_resource_performance:
            def look(r: cm.ResourceModel):
                skill_factor = 1 / self.resource_skills.get(r.label, 1)
                performance_factor = 1
                performance_calculator = r.data.peek_at_property(ResourceProperty.Performance)
                if performance_calculator is not None:
                    performance_factor = performance_calculator.performance(
                        r.data.peek_at_state(ResourceState.CurrentlyAssigned) / r.data.peek_at_property(
                            ResourceProperty.Capacity))
                return skill_factor * performance_factor

            self.lookup = look

    def sample(self, case: sc.Case, resource: cm.ResourceModel) -> timedelta:
        base = self.base_sampler.sample()
        lookup = self.lookup(resource)
        return base * lookup

    def __eq__(self, o: object) -> bool:
        return isinstance(o,
                          self.__class__) and self.base_sampler == o.base_sampler and self.resource_skills == o.resource_skills and self.use_resource_performance == o.use_resource_performance

    def __hash__(self) -> int:
        return hash((self.base_sampler, self.resource_skills, self.use_resource_performance))

    def __str__(self) -> str:
        return f'ResourceDependentPTSampler(base_sampler={self.base_sampler}, skills={self.resource_skills}, use_resource_performance={self.use_resource_performance})'


class StochasticClassifier(params.CaseClassifier, ocpa.CarrierClassifier):

    def __init__(self, probabilities) -> None:
        super().__init__(len(probabilities))
        self.probabilities = probabilities

    def classify_override(self, case: Any) -> int:
        return np.random.choice(self.number_of_classes, p=self.probabilities)

    def __eq__(self, o: object) -> bool:
        return isinstance(o,
                          self.__class__) and self.number_of_classes == o.number_of_classes and self.probabilities == o.probabilities

    def __hash__(self) -> int:
        return hash((self.number_of_classes, self.probabilities))

    def __str__(self) -> str:
        return f'StochasticClassifier({list(self.probabilities)})'


class LambdaClassifier(params.CaseClassifier):
    def __init__(self, lambd: Callable[[sc.Case], int], class_count=2) -> None:
        super().__init__(class_count)
        self.lambd = lambd

    @classmethod
    def binary(cls, lambd: Callable[[sc.Case], bool], id_if_true=0):
        return cls(lambda case: id_if_true if lambd(case) else 1 - id_if_true, class_count=2)

    def classify_override(self, case: sc.Case) -> int:
        return self.lambd(case)

    def __eq__(self, o: object) -> bool:
        return isinstance(o,
                          self.__class__) and self.lambd == o.lambd

    def __hash__(self) -> int:
        return hash(self.lambd)

    def __str__(self) -> str:
        return f'LambdaClassifier({self.lambd})'


class AttributeBasedClassifier(LambdaClassifier):

    def __init__(self, attr_name: str, attr_lambda: Callable[[Any], int],
                 attr_level: AttributeLevel = AttributeLevel.Case, class_count=2) -> None:
        self.attr_name = attr_name
        self.attr_level = attr_level
        if attr_level == AttributeLevel.Event:
            self.attr_getter = lambda c: c.get_latest_event_attr_value(self.attr_name)
        elif attr_level == AttributeLevel.Case:
            self.attr_getter = lambda c: c.attributes.get(self.attr_name)
        self.attr_decider = attr_lambda
        super().__init__(lambda case: self.attr_decider(case.attributes.get(self.attr_name)), class_count)

    @classmethod
    def fixed_values(cls, attr_name: str, attr_values: list[Any],
                     attr_level: AttributeLevel = AttributeLevel.Case) -> AttributeBasedClassifier:
        attr_values = list(attr_values)
        return cls(attr_name, attr_values.index, attr_level=attr_level, class_count=len(attr_values))

    def __eq__(self, o: object) -> bool:
        return isinstance(o,
                          self.__class__) and self.attr_name == o.attr_name and self.attr_decider == o.attr_decider and self.attr_level == o.attr_level

    def __hash__(self) -> int:
        return hash((self.attr_name, self.attr_decider, self.attr_level))

    def __str__(self) -> str:
        return f'AttributeBasedClassifier({self.attr_name} ({self.attr_level}), {self.attr_decider})'


class IntervalAttributeClassifier(params.CaseClassifier):

    def __init__(self, attr_name: str, attr_intervals: dict[int, tuple[float, float]],
                 attr_level: AttributeLevel = AttributeLevel.Case, right_open=True) -> None:
        super().__init__(len(attr_intervals))
        self.attr_name = attr_name
        if attr_level == AttributeLevel.Event:
            self.attr_getter = lambda c: c.get_latest_event_attr_value(self.attr_name)
        elif attr_level == AttributeLevel.Case:
            self.attr_getter = lambda c: c.attributes.get(self.attr_name)
        self.attr_intervals = attr_intervals
        self.lookup_list = sorted(((k, v) for k, v in attr_intervals.items()), key=lambda t: t[1][0])
        self.right_open = right_open
        if right_open:
            self.interval_check = lambda l, r, v: l <= v < r
            self.default = self.lookup_list[0][0]
        else:
            self.interval_check = lambda l, r, v: l < v <= r
            self.default = self.lookup_list[-1][0]

    def __eq__(self, o: object) -> bool:
        return isinstance(o,
                          self.__class__) and self.attr_name == o.attr_name and self.lookup_list == o.lookup_list

    def __hash__(self) -> int:
        return hash((self.attr_name, self.lookup_list))

    def __str__(self) -> str:
        return f'AttributeClassifier({self.attr_name}, {self.lookup_list})'

    def classify_override(self, case: sc.Case) -> int:
        target = self.attr_getter(case)
        for t in self.lookup_list:
            l, r = t[1]
            if self.interval_check(l, r, target):
                return t[0]
        return self.default


class AlwaysInBusinessHours(params.BusinessHours):

    def average_availability(self) -> float:
        return 1.0

    def is_dynamic(self) -> bool:
        return False

    def in_business(self, current_time: datetime) -> bool:
        return True

    def next_change(self, current_time: datetime) -> Optional[datetime]:
        return None

    def __str__(self) -> str:
        return 'AlwaysInBusiness'


AlwaysInBusiness = AlwaysInBusinessHours()


class NeverInBusinessHours(params.BusinessHours):

    def average_availability(self) -> float:
        return 0.0

    def is_dynamic(self) -> bool:
        return False

    def in_business(self, current_time: datetime) -> bool:
        return False

    def next_change(self, current_time: datetime) -> Optional[datetime]:
        return None

    def __str__(self) -> str:
        return 'NeverInBusiness'


NeverInBusiness = NeverInBusinessHours()


class WorkweekBusinessHours(params.BusinessHours):

    def __init__(self, daily_business_hours: Dict[Weekdays, Tuple[datetime.time, datetime.time]]) -> None:
        self.bh = FrozenDict(daily_business_hours)
        assert len(self.bh) > 0  # at least one business day, leads to (recursion) stack overflow otherwise

    @classmethod
    def fixed_time(cls, timeslot: tuple[datetime.time, datetime.time],
                   weekdays: set[Weekdays]) -> WorkweekBusinessHours:
        return cls({w: timeslot for w in weekdays})

    def average_availability(self) -> float:
        agg = pd.Timedelta(0)
        for day, (start, end) in self.bh.items():
            hours_on_day = time_utils.duration_between_times(start, end)
            agg += hours_on_day
        return agg / pd.Timedelta(days=7)

    def is_dynamic(self) -> bool:
        return True

    def in_business(self, current_time: datetime) -> bool:
        day = Weekdays(current_time.weekday())
        if day in self.bh:
            start, end = self.bh[day]
            return start <= current_time.time() < end
        return False

    def _next_change_recursive(self, current_time: datetime, start_day, looped_once=False):
        day = Weekdays(current_time.weekday())
        if day in self.bh:
            start, end = self.bh[day]
            start_dt, end_dt = time_utils.set_time(current_time, start), time_utils.set_time(
                current_time, end)
            if current_time < start_dt:
                return start_dt
            elif current_time < end_dt:
                return end_dt
        next_day = time_utils.next_day(current_time)
        if Weekdays(next_day.weekday()) is not start_day:
            return self._next_change_recursive(next_day, start_day, looped_once=False)
        elif not looped_once:
            return self._next_change_recursive(next_day, start_day, looped_once=True)
        else:
            print(current_time, next_day, start_day, looped_once)
            print(current_time.weekday(), Weekdays(current_time.weekday()))
            print(next_day.weekday(), Weekdays(next_day.weekday()))
            print(self.bh)

    def next_change(self, current_time: datetime):
        return self._next_change_recursive(current_time, Weekdays(current_time.weekday()))

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.bh == o.bh

    def __hash__(self) -> int:
        return hash(self.bh)

    def __str__(self) -> str:
        return f'WorkweekBusinessHours({str(self.bh)})'


StandardWorkweek = WorkweekBusinessHours.fixed_time((time(hour=9), time(hour=17)), time_utils.Workweek)


class ExtendedBusinessHours(params.BusinessHours):

    def __init__(self, daily_business_hours: dict[Weekdays, list[tuple[datetime.time, datetime.time]]]) -> None:
        self.bh = FrozenDict(
            {w: tuple(slots) for w, slots in daily_business_hours.items()})
        assert len(self.bh) > 0  # at least one business day, leads to (recursion) stack overflow otherwise

    @classmethod
    def fixed_times(cls, timeslots: list[tuple[datetime.time, datetime.time]],
                    weekdays: set[Weekdays]) -> ExtendedBusinessHours:
        return cls({w: timeslots for w in weekdays})

    def average_availability(self) -> float:
        agg = pd.Timedelta(0)
        for day, slots in self.bh.items():
            for start, end in slots:
                hours_on_day = time_utils.duration_between_times(start, end)
                agg += hours_on_day
        return agg / pd.Timedelta(days=7)

    def is_dynamic(self) -> bool:
        return True

    def in_business(self, current_time: datetime) -> bool:
        day = Weekdays(current_time.weekday())
        if day in self.bh:
            for start, end in self.bh[day]:
                if start <= current_time.time() < end:
                    return True
        return False

    def _next_change_recursive(self, current_time: datetime, start_day, looped_once=False):
        day = Weekdays(current_time.weekday())
        if day in self.bh:
            slots = self.bh[day]
            for start, end in slots:
                start_dt, end_dt = time_utils.set_time(current_time,
                                                                    start), time_utils.set_time(
                    current_time, end)
                if current_time < start_dt:
                    return start_dt
                elif current_time < end_dt:
                    return end_dt
        next_day = time_utils.next_day(current_time)
        if Weekdays(next_day.weekday()) is not start_day:
            return self._next_change_recursive(next_day, start_day, looped_once=False)
        elif not looped_once:
            return self._next_change_recursive(next_day, start_day, looped_once=True)
        else:
            print(current_time, next_day, start_day, looped_once)
            print(current_time.weekday(), Weekdays(current_time.weekday()))
            print(next_day.weekday(), Weekdays(next_day.weekday()))
            print(self.bh)

    def next_change(self, current_time: datetime):
        return self._next_change_recursive(current_time, Weekdays(current_time.weekday()))

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.bh == o.bh

    def __hash__(self) -> int:
        return hash(self.bh)

    def __str__(self) -> str:
        return f'WorkweekBusinessHours({str(self.bh)})'
