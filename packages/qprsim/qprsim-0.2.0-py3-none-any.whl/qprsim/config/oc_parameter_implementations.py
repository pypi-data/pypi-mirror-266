from typing import Callable, Any

import qprsim.model.oc_model_parameters as ocpa
from qprsim.core import object_def as obd


class TypeBasedObjectQualifier(ocpa.OCEventObjectQualifier):

    def qualify(self, carrier: obd.Carrier, **kwargs) -> dict[obd.ObjectType, set[obd.Object]]:
        return carrier.derive_type_map()


DefaultObjectQualifier = TypeBasedObjectQualifier()


class EmptyObjectCreator(ocpa.ObjectCreator):

    def create_object(self, object_id, **context_information) -> obd.Object:
        return obd.Object(object_id, self.object_type)


class LambdaObjectCreator(ocpa.ObjectCreator):

    def __init__(self, object_type: obd.ObjectType,
                 obj_lamb: Callable[[obd.ObjectId, ...], obd.Object],
                 o2o_lamb: Callable[[obd.Object, ...], obd.QualifiedO2ORelations] = None) -> None:
        super().__init__(object_type)
        self.obj_lamb = obj_lamb
        self.o2o_lamb = o2o_lamb if o2o_lamb is not None else lambda: {}

    def create_object(self, object_id: obd.ObjectId, **context_information) -> obd.Object:
        return self.obj_lamb(object_id, **context_information)

    def generate_initial_o2o_relations(self, obj: obd.Object, **context_information) -> obd.QualifiedO2ORelations:
        return self.o2o_lamb(obj, **context_information)


class CompositeObjectSetCreator(ocpa.ObjectSetCreator):

    def __init__(self, *carrier_generators: ocpa.ObjectSetCreator) -> None:
        super().__init__()
        self.carrier_generators: tuple[ocpa.ObjectSetCreator] = carrier_generators

    def create_carrier(self, **context_information) -> tuple[obd.Carrier, obd.QualifiedO2ORelations]:
        cs = set()
        o2os = {}
        for g in self.carrier_generators:
            c, o2o = g.create_carrier(**context_information)
            for o in c:
                cs.add(o)
            o2os.update(o2o)

        super_carrier = obd.Carrier(*cs)
        return super_carrier, o2os


class TypeBasedSplitter(ocpa.CarrierSplitter):

    def __init__(self, directions: dict[obd.ObjectType, int], split_into_singletons=False) -> None:
        super().__init__()
        self.split_into_singletons = split_into_singletons
        self.directions = directions

    def split_up(self, carrier: obd.Carrier) -> dict[obd.Carrier, int]:
        if self.split_into_singletons:
            return {obd.Carrier(o): self.directions[t] for t, os in carrier.derive_type_map().items() for o in os}
        else:
            return {obd.Carrier(*os): self.directions[t] for t, os in carrier.derive_type_map().items()}


##############################################################################
# Lambda Lovers
##############################################################################

class LambdaObjectSetCreator(ocpa.ObjectSetCreator):

    def __init__(self, lamb: Callable[[Callable[[obd.ObjectType], obd.ObjectId], ...], tuple[
        obd.Carrier, obd.QualifiedO2ORelations]]) -> None:
        super().__init__()
        self.lamb = lamb

    def create_carrier(self, object_id_source: Callable[[obd.ObjectType], obd.ObjectId], **context_information) -> \
            tuple[
                obd.Carrier, obd.QualifiedO2ORelations]:
        return self.lamb(object_id_source, **context_information)


class LambdaCarrierAttributeGenerator(ocpa.OCCarrierAttributeGenerator):

    def __init__(self, lamb: Callable[[obd.Carrier, ...], dict[obd.Object, dict[str, Any]]]) -> None:
        super().__init__()
        self.lamb = lamb

    def generate(self, carrier: obd.Carrier, **kwargs):
        return self.lamb(carrier, **kwargs)


class LambdaEventAttributeGenerator(ocpa.OCEventAttributeGenerator):

    def __init__(self, lamb: Callable[[obd.Carrier, ...], dict[str, Any]]) -> None:
        super().__init__()
        self.lamb = lamb

    def generate(self, carrier: obd.Carrier, **kwargs):
        return self.lamb(carrier, **kwargs)


class LambdaObjectAttributeGenerator(ocpa.OCObjectAttributeGenerator):

    def __init__(self, lamb: Callable[[obd.Object, ...], dict[str, Any]]) -> None:
        super().__init__()
        self.lamb = lamb

    def generate(self, obj: obd.Object, **kwargs):
        return self.lamb(obj, **kwargs)


# TODO add as annotation
def lift(gen: ocpa.OCObjectAttributeGenerator) -> ocpa.OCCarrierAttributeGenerator:
    class Lifted(ocpa.OCCarrierAttributeGenerator):

        def generate(self, carrier: obd.Carrier, **kwargs) -> dict[obd.Object, dict[str, Any]]:
            o = carrier.as_singleton()
            attrs = gen.generate(o, **kwargs)
            return {o: attrs}

    return Lifted()


def lift_to_singleton_carriers(func: Callable[[obd.Object, ...], dict[str, Any]]) -> Callable[
    [obd.Carrier, ...], dict[obd.Object, dict[str, Any]]]:
    def lifted(carrier: obd.Carrier, **kwargs):
        o = carrier.as_singleton()
        attrs = func(o, **kwargs)
        return {o: attrs}

    return lifted
