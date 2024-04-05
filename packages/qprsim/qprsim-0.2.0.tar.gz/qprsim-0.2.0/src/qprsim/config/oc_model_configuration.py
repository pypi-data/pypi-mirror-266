from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Collection, TYPE_CHECKING

import numpy as np

import qprsim.model.oc_graph_models as gm
from qprsim.model.model_parameters import InterArrivalSampler, BusinessHours
from qprsim.model.oc_model_parameters import OCEventAttributeGenerator, OCCarrierAttributeGenerator, \
    OCEventObjectQualifier, OCQueueingDiscipline, OCProcessingTimeSampler
from qprsim.shared.base_classes import auto_str, FrozenDict
from qprsim.shared.enums import OCActivityProperty, OCObjectBirthplaceProperty
from qprsim.utils.time_utils import make_timezone_aware
from .model_configuration import ModelHaverConfig, MappingConfig, ResourceConfig

if TYPE_CHECKING:
    import qprsim.model.oc_model_parameters as ocpa
    import qprsim.core.object_def as obd


class DecisionConfig(ModelHaverConfig):
    model_class = gm.OCDecisionModel

    def __init__(self, classifier: ocpa.CarrierClassifier, **kwargs) -> None:
        super().__init__(classifier=classifier, **kwargs)


class SplitConfig(ModelHaverConfig):
    model_class = gm.OCSplitModel

    def __init__(self, splitter: ocpa.CarrierSplitter, **kwargs) -> None:
        super().__init__(splitter=splitter, **kwargs)


class DummyConfig(ModelHaverConfig):
    pass


class JoinConfig(DummyConfig):
    model_class = gm.OCSyncModel


class CarrierGeneratorConfig(ModelHaverConfig):
    model_class = gm.OCCarrierGeneratorModel
    requires_unsafe_access = True

    def __init__(self, carrier_generator: ocpa.CarrierGenerator, **kwargs) -> None:
        super().__init__(carrier_generator=carrier_generator, **kwargs)


@auto_str
@dataclass(unsafe_hash=True)
class OCArrivalProcessConfig:
    first_arrival: datetime
    inter_arrivals: InterArrivalSampler
    targets: frozenset[str]
    business_hours: BusinessHours = None
    last_arrival: datetime = None
    max_arrivals: int = None

    def __init__(self, first_arrival: datetime, inter_arrivals: InterArrivalSampler, targets: Collection[str],
                 business_hours: BusinessHours = None, last_arrival: datetime = None, max_arrivals: int = None) -> None:
        self.first_arrival = make_timezone_aware(first_arrival)
        self.inter_arrivals = inter_arrivals
        self.targets = frozenset(targets)
        self.business_hours = business_hours
        self.last_arrival = make_timezone_aware(last_arrival) if last_arrival is not None else None
        self.max_arrivals = max_arrivals


@auto_str
@dataclass(unsafe_hash=True)
class ObjectBirthplaceConfig:
    # TODO create generalization of this
    property_dict: FrozenDict[OCObjectBirthplaceProperty, Any]

    def __init__(self, object_type: obd.ObjectType, object_creator: ocpa.ObjectCreator,
                 creation_limit=np.inf) -> None:
        super().__init__()
        self.property_dict = FrozenDict({OCObjectBirthplaceProperty.ObjectType: object_type,
                                         OCObjectBirthplaceProperty.ObjectCreator: object_creator,
                                         OCObjectBirthplaceProperty.CreationLimit: creation_limit})


@auto_str
@dataclass(unsafe_hash=True)
class OCActivityConfig:
    business_hours: BusinessHours = None
    property_dict: FrozenDict[OCActivityProperty, Any] = None

    def __init__(self, processing_time_sampler: OCProcessingTimeSampler = None,
                 queueing_discipline: OCQueueingDiscipline = None,
                 business_hours: BusinessHours = None, object_qualifier: OCEventObjectQualifier = None,
                 attribute_generator: OCEventAttributeGenerator = None,
                 carrier_attribute_generator: OCCarrierAttributeGenerator = None,
                 property_dict: dict[OCActivityProperty, Any] = None) -> None:
        self.business_hours = business_hours
        props = property_dict if property_dict is not None else {}
        if queueing_discipline is not None:
            props[OCActivityProperty.QueueingDiscipline] = queueing_discipline
        if processing_time_sampler is not None:
            props[OCActivityProperty.ProcessingTimeSampler] = processing_time_sampler
        if object_qualifier is not None:
            props[OCActivityProperty.ObjectQualifier] = object_qualifier
        if attribute_generator is not None:
            props[OCActivityProperty.EventAttributeGenerator] = attribute_generator
        if carrier_attribute_generator is not None:
            props[OCActivityProperty.CarrierAttributeGenerator] = carrier_attribute_generator
        self.property_dict = FrozenDict(props)


@dataclass(unsafe_hash=True)
class OCModelConfiguration:
    processes: dict[str, OCArrivalProcessConfig]
    birthplaces: dict[str, ObjectBirthplaceConfig]
    activities: dict[str, OCActivityConfig]
    resources: dict[str, ResourceConfig]
    aux_model_configs: dict[str, ModelHaverConfig]
    mapping: MappingConfig

    def __str__(self) -> str:
        return 'Arrivals:' + ('\n' if len(self.processes) > 0 else ' n/a') \
            + '\n'.join(str(l) + ': ' + str(ar) for l, ar in self.processes.items()) + '\n' \
            + 'Birthplaces:' + ('\n' if len(self.birthplaces) > 0 else ' n/a') \
            + '\n'.join(str(a) + ': ' + str(bc) for a, bc in self.birthplaces.items()) + '\n' \
            + 'Activities:' + ('\n' if len(self.activities) > 0 else ' n/a') \
            + '\n'.join(str(a) + ': ' + str(ac) for a, ac in self.activities.items()) + '\n' \
            + 'Resources:' + ('\n' if len(self.resources) > 0 else ' n/a') \
            + '\n'.join(str(r) + ': ' + str(rc) for r, rc in self.resources.items()) + '\n' \
            + 'Auxiliary Models:' + ('\n' if len(self.aux_model_configs) > 0 else ' n/a') \
            + '\n'.join(str(a) + ': ' + str(aux) for a, aux in self.aux_model_configs.items()) + '\n' \
            + str(self.mapping)
