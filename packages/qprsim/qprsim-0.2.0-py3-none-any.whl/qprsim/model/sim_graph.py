from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import Generic, TypeVar
from typing import TYPE_CHECKING

from qprsim.shared.base_classes import permuted
from qprsim.shared.shared_traits import WithLabel
from . import graph_models as gm

if TYPE_CHECKING:
    import qprsim.core.case as sc
    import model_parameters as params


class SimulationNode:

    def __init__(self, **kwargs) -> None:
        super(SimulationNode, self).__init__(**kwargs)

    @abstractmethod
    def accept(self, case: sc.Case): ...


class WithPartner:

    def __init__(self, partner=None, **kwargs) -> None:
        super(WithPartner, self).__init__(**kwargs)
        self.partner = partner


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

    def forward(self, case: sc.Case):
        self.successor.accept(case)


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

    def accept(self, case: sc.Case):
        pass

    def forward_to(self, idx: int, case: sc.Case):
        self.successors[idx].accept(case)


class TauNode(LinearNode):

    def accept(self, case: sc.Case):
        self.forward(case)


class AndSplit(SplittingNode, WithPartner):

    def accept(self, case: sc.Case):
        for successor in permuted(self.successors):
            successor.accept(case)


class JoiningNode(LinearNode, ABC):
    pass


class AndJoin(JoiningNode, WithPartner):

    def __init__(self, parallel_splits: int, **kwargs) -> None:
        super(AndJoin, self).__init__(**kwargs)
        self.parallel_splits = parallel_splits
        self.arrival_counts: dict[sc.Case, int] = defaultdict(int)

    def accept(self, case: sc.Case):
        self.arrival_counts[case] += 1
        if self.arrival_counts[case] >= self.parallel_splits:
            del self.arrival_counts[case]
            self.forward(case)


class XorJoin(JoiningNode, TauNode):
    pass


##############################################################################
# MODEL HAVERS
##############################################################################

ModelType = TypeVar('ModelType', bound=gm.SimulationNodeModel)


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

    def submit_to_model(self, case: sc.Case):
        self.model.accept(case)

    @abstractmethod
    def accept_from_model(self, case: sc.Case, **kwargs): ...


class SinkNodeWithModel(SimulationNode, WithModel[ModelType]):
    def accept(self, case: sc.Case):
        self.submit_to_model(case)

    def accept_from_model(self, case: sc.Case, **kwargs): ...


class LinearNodeWithModel(LinearNode, WithModel[ModelType]):

    def __init__(self, **kwargs) -> None:
        super(LinearNodeWithModel, self).__init__(**kwargs)

    def accept(self, case: sc.Case):
        self.submit_to_model(case)

    def accept_from_model(self, case: sc.Case, **kwargs):
        self.forward(case)


class SplittingNodeWithModel(SplittingNode, WithModel[ModelType]):

    def __init__(self, **kwargs) -> None:
        super(SplittingNodeWithModel, self).__init__(**kwargs)

    def accept(self, case: sc.Case):
        self.submit_to_model(case)

    def accept_from_model(self, case: sc.Case, successor_id: int = 0, **kwargs):
        self.forward_to(successor_id, case)


class DecisionNode(SplittingNodeWithModel[gm.DecisionModel]):
    pass


class XorSplit(DecisionNode, WithPartner):
    pass


class DelayNode(LinearNodeWithModel[gm.DelayModel]):
    pass


class ActivityNode(LinearNodeWithModel[gm.ActivityModel], WithLabel):
    pass


class ArrivalNode(LinearNodeWithModel[gm.ArrivalModel], WithLabel):
    pass


class TerminalNode(SinkNodeWithModel[gm.TerminalModel], WithLabel):
    pass


class SynchronizationNode(SplittingNodeWithModel[gm.SyncModel]):
    pass


class TransformationNode(SplittingNodeWithModel[gm.CaseTransformerModel]):
    pass


####################################################################
# Superfluous
####################################################################
class OrJoin(JoiningNode):

    def __init__(self, **kwargs) -> None:
        super(OrJoin, self).__init__(**kwargs)
        self.arrival_counts: dict[sc.Case, int] = defaultdict(int)
        self.expected_arrivals = {}

    def set_expectation(self, case: sc.Case, expected_arrivals: int):
        self.expected_arrivals[case] = expected_arrivals

    def accept(self, case: sc.Case):
        self.arrival_counts[case] += 1
        if self.arrival_counts[case] >= self.expected_arrivals[case]:
            del self.arrival_counts[case]
            del self.expected_arrivals[case]
            self.forward(case)


class DecisionNodeOld(SplittingNode):

    def __init__(self, classifier: params.CaseClassifier = None, **kwargs):
        super(DecisionNodeOld, self).__init__(**kwargs)
        self.classifier = classifier

    @property
    def classifier(self) -> params.CaseClassifier:
        return self._classifier

    @classifier.setter
    def classifier(self, value: params.CaseClassifier):
        self._classifier = value


class MultiDecisionNode(SplittingNode):

    def __init__(self, classifier: params.MultiDecisionClassifier = None, **kwargs):
        super(MultiDecisionNode, self).__init__(**kwargs)
        self.classifier = classifier

    @property
    def classifier(self) -> params.MultiDecisionClassifier:
        return self._classifier

    @classifier.setter
    def classifier(self, value: params.MultiDecisionClassifier):
        self._classifier = value


class XorSplitOld(DecisionNodeOld, WithPartner):

    def __init__(self, classifier: params.CaseClassifier = None, **kwargs):
        super().__init__(classifier, **kwargs)

    def accept(self, case: sc.Case):
        self.forward_to(self.classifier.classify(case), case)


class OrSplit(MultiDecisionNode, WithPartner):

    def __init__(self, multi_classifier: params.MultiDecisionClassifier = None, **kwargs):
        super().__init__(multi_classifier, **kwargs)

    def accept(self, case: sc.Case):
        for i in self.classifier.classify(case):
            self.forward_to(i, case)


####################################################################
####################################################################

@dataclass(unsafe_hash=True)
class GenericSimulationGraph:
    arrivals: dict[str, ArrivalNode]
    terminals: dict[str, TerminalNode]
    activity_map: dict[str, ActivityNode]
    aux_model_haver_map: dict[str, WithModel]
