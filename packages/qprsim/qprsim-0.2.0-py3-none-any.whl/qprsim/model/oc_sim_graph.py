from __future__ import annotations

import logging
from abc import abstractmethod, ABC
from collections import defaultdict
from dataclasses import dataclass
from typing import Generic, TypeVar
from typing import TYPE_CHECKING

from . import oc_graph_models as gm
from .sim_graph import WithPartner, WithLabel

if TYPE_CHECKING:
    import qprsim.core.object_def as obd


##############################################################################
# Structural Node Definitions
##############################################################################

class SimulationNode:

    def __init__(self, **kwargs) -> None:
        super(SimulationNode, self).__init__(**kwargs)

    @abstractmethod
    def accept(self, carrier: obd.Carrier): ...


class LinearNode(SimulationNode, ABC):

    def __init__(self, successor: SimulationNode = None, **kwargs) -> None:
        super(LinearNode, self).__init__(**kwargs)
        self.successor = successor

    @property
    def successor(self):
        return self._successor

    @successor.setter
    def successor(self, value):
        self._successor = value

    def forward(self, carrier: obd.Carrier):
        self.successor.accept(carrier)


class SplittingNode(SimulationNode):

    def __init__(self, successors: list[SimulationNode] = None, **kwargs):
        super(SplittingNode, self).__init__(**kwargs)
        if successors is not None:
            self.successors = successors
        else:
            self.successors = []

    @property
    def successors(self) -> list[SimulationNode]:
        return self._successors

    @successors.setter
    def successors(self, value: list[SimulationNode]):
        self._successors = value

    @property
    def successor_count(self) -> int:
        return len(self.successors)

    def accept(self, carrier: obd.Carrier):
        pass

    def forward_to(self, idx: int, carrier: obd.Carrier):
        self.successors[idx].accept(carrier)


class JoiningNode(LinearNode, ABC):
    pass


class TauNode(LinearNode):

    def accept(self, carrier: obd.Carrier):
        self.forward(carrier)


class XorJoin(JoiningNode, WithPartner, TauNode):
    pass


class AndSplit(SplittingNode, WithPartner):

    def accept(self, carrier: obd.Carrier):
        for successor in self.successors:
            successor.accept(carrier)


class AndJoin(JoiningNode, WithPartner):

    def __init__(self, parallel_splits: int, **kwargs) -> None:
        super(AndJoin, self).__init__(**kwargs)
        self.parallel_splits = parallel_splits
        self.arrival_counts: dict[obd.Carrier, int] = defaultdict(int)

    def accept(self, carrier: obd.Carrier):
        self.arrival_counts[carrier] += 1
        if self.arrival_counts[carrier] >= self.parallel_splits:
            del self.arrival_counts[carrier]
            self.forward(carrier)


##############################################################################
# MODEL HAVERS: Abstract Definitions
##############################################################################

ModelType = TypeVar('ModelType', bound=gm.OCSimulationNodeModel)


class WithModel(Generic[ModelType]):

    def __init__(self, model: ModelType = None, **kwargs) -> None:
        super(WithModel, self).__init__(**kwargs)
        self.__model: ModelType = model

    @property
    def model(self) -> ModelType:
        return self.__model

    @model.setter
    def model(self, value: ModelType):
        assert value is not None
        self.__model = value

    def submit_to_model(self, carrier: obd.Carrier):
        self.model.accept(carrier)

    @abstractmethod
    def accept_from_model(self, carrier: obd.Carrier, **kwargs): ...


class SinkNodeWithModel(SimulationNode, WithModel[ModelType]):
    def accept(self, carrier: obd.Carrier):
        self.submit_to_model(carrier)

    def accept_from_model(self, carrier: obd.Carrier, **kwargs): ...


class LinearNodeWithModel(LinearNode, WithModel[ModelType]):

    def __init__(self, **kwargs) -> None:
        super(LinearNodeWithModel, self).__init__(**kwargs)

    def accept(self, carrier: obd.Carrier):
        self.submit_to_model(carrier)

    def accept_from_model(self, carrier: obd.Carrier, **kwargs):
        self.forward(carrier)


class SplittingNodeWithModel(SplittingNode, WithModel[ModelType]):

    def __init__(self, **kwargs) -> None:
        super(SplittingNodeWithModel, self).__init__(**kwargs)

    def accept(self, carrier: obd.Carrier):
        self.submit_to_model(carrier)

    def accept_from_model(self, carrier: obd.Carrier, successor_id: int = 0, **kwargs):
        self.forward_to(successor_id, carrier)


##############################################################################
# MODEL HAVERS: Implementations
##############################################################################


class DecisionNode(SplittingNodeWithModel[gm.OCDecisionModel]):
    pass


class XorSplit(DecisionNode, WithPartner):
    pass


class ActivityNode(LinearNodeWithModel[gm.OCActivityModel], WithLabel):
    pass


class BirthplaceNode(LinearNodeWithModel[gm.OCBirthplaceModel], WithLabel):
    pass


class GraveyardNode(SinkNodeWithModel[gm.OCGraveyardModel], WithLabel):
    pass


class OCSplit(WithPartner, SplittingNodeWithModel[gm.OCSplitModel]):

    def accept(self, carrier: obd.Carrier):
        self.partner.premonition(carrier)
        super().accept(carrier)


class OCJoin(WithPartner, LinearNodeWithModel[gm.OCSyncModel]):

    def premonition(self, carrier: obd.Carrier):
        self.model.set_expectation(carrier)


class OCTransformerNode(LinearNodeWithModel[gm.OCCarrierGeneratorModel]):
    pass


##############################################################################
# FUTURE WORK
##############################################################################

# TODO future work
# class TransformationNode(SplittingNodeWithModel[gm.OCTransformerModel]):
#    pass


############


@dataclass(unsafe_hash=True)
class OCSimulationGraph:
    birthplaces: dict[str, BirthplaceNode]
    graveyards: dict[str, GraveyardNode]
    activity_map: dict[str, ActivityNode]
    aux_model_haver_map: dict[str, WithModel]
