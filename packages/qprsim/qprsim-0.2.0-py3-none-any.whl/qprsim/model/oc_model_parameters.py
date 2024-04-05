from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Any, Callable
from typing import TYPE_CHECKING

from .model_parameters import AttributeGenerator, verify, nonnegative_timedelta

if TYPE_CHECKING:
    import qprsim.core.object_def as obd
    import qprsim.model.conceptual_models as cm


class OCEventAttributeGenerator(AttributeGenerator):
    @abstractmethod
    def generate(self, carrier: obd.Carrier, **kwargs) -> dict[str, Any]: ...


class OCObjectAttributeGenerator(AttributeGenerator):

    @abstractmethod
    def generate(self, obj: obd.Object, **kwargs) -> dict[str, Any]: ...


class OCCarrierAttributeGenerator:

    @abstractmethod
    def generate(self, carrier: obd.Carrier, **kwargs) -> dict[obd.Object, dict[str, Any]]: ...


class OCEventObjectQualifier:
    @abstractmethod
    def qualify(self, carrier: obd.Carrier, **kwargs) -> dict[str, set[obd.Object]]: ...


class OCQueueingDiscipline:

    def select(self, queue: list[tuple[datetime, obd.Carrier]]) -> int: ...


class OCProcessingTimeSampler:

    @verify(nonnegative_timedelta)
    @abstractmethod
    def sample(self, carrier: obd.Carrier, resource: cm.ResourceProvider) -> timedelta: ...


class CarrierClassifier:

    def __init__(self, number_of_classes: int) -> None:
        self.__number_of_classes = number_of_classes

    @property
    def number_of_classes(self) -> int:
        return self.__number_of_classes

    def classify_override(self, carrier: obd.Carrier) -> int: ...

    def classify(self, carrier: obd.Carrier) -> int:
        classification = self.classify_override(carrier)
        assert 0 <= classification < self.number_of_classes
        return classification


class CarrierSplitter:

    @abstractmethod
    def split_up(self, carrier: obd.Carrier) -> dict[obd.Carrier, int]: ...


class CarrierGenerator:

    def create_carrier(self, object_id_source: Callable[[obd.ObjectType], obd.ObjectId], **context_information) -> \
            tuple[
                obd.Carrier, obd.QualifiedO2ORelations]: ...


ObjectSetCreator = CarrierGenerator


class ObjectCreator(ObjectSetCreator):

    def __init__(self, object_type: obd.ObjectType) -> None:
        self.__object_type = object_type

    @property
    def object_type(self):
        return self.__object_type

    def create_object(self, object_id: obd.ObjectId, **context_information) -> obd.Object:
        return obd.Object(object_id, self.object_type)

    def generate_initial_o2o_relations(self, obj: obd.Object, **context_information) -> obd.QualifiedO2ORelations:
        return {}

    def create_carrier(self, object_id_source: Callable[[obd.ObjectType], obd.ObjectId], **context_information) -> \
            tuple[
                obd.Carrier, obd.QualifiedO2ORelations]:
        o = self.create_object(object_id_source(self.object_type), **context_information)
        o2o = self.generate_initial_o2o_relations(o, **context_information)
        return obd.Carrier(o), o2o
