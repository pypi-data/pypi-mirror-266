import datetime
from datetime import timedelta, datetime
from typing import Tuple, Iterator, Union, Iterable

from qprsim.config import impls
from qprsim.config import ArrivalProcessConfig, ActivityConfig, ResourceConfig, MappingConfig, \
    GenericModelConfiguration, ModelHaverConfig
from qprsim.model.sim_graph import ArrivalNode, TerminalNode, ActivityNode, XorSplit, XorJoin, AndSplit, AndJoin, \
    LinearNode, SplittingNode, TauNode, GenericSimulationGraph, WithModel

splitting_node_suffix = '_split'
joining_node_suffix = '_join'

default_arrival_label = 'arrival'
default_terminal_label = 'terminal'


def base_of(label):
    return label.rsplit('_', 1)[0]


def split_of(label):
    return label + splitting_node_suffix


def join_of(label):
    return label + joining_node_suffix


def gen_suffixed(label):
    return split_of(label), join_of(label)


def ensure_tuple(label):
    if isinstance(label, str):
        return label, label
    else:
        return label


class GraphBuilder:

    def __init__(self, initial_graph: GenericSimulationGraph = None, use_defaults=False, skip_asserts=False) -> None:
        self.use_defaults = use_defaults
        self.skip_asserts = skip_asserts
        self.node_map = {}
        self.aliases = {}
        self.arrival_nodes = {}
        self.terminal_nodes = {}
        self.activity_nodes = {}
        self.aux_model_havers = {}

        self.decision_id = 1
        self.concurrency_id = 1
        self.tau_id = 1

    def add_node(self, label, node, connect_to_arrival: bool | str | list = False,
                 connect_to_terminal: bool | str | list = False) -> str:
        assert label not in self.node_map
        self.node_map[label] = node

        if isinstance(node, ActivityNode):
            self.activity_nodes[label] = node
        elif isinstance(node, ArrivalNode):
            self.arrival_nodes[label] = node
        elif isinstance(node, TerminalNode):
            self.terminal_nodes[label] = node
        elif isinstance(node, WithModel):
            self.aux_model_havers[label] = node

        if connect_to_arrival:
            if isinstance(connect_to_arrival, bool) and self.use_defaults:
                connect_to_arrival = default_arrival_label
            self.connect_to_arrival(label, arrival_labels=connect_to_arrival)
        if connect_to_terminal:
            if isinstance(connect_to_terminal, bool) and self.use_defaults:
                connect_to_terminal = default_terminal_label
            self.connect_to_terminal(label, terminal_labels=connect_to_terminal)
        return label

    def add_activity(self, label: str, **kwargs) -> str:
        return self.add_node(label, ActivityNode(label=label), **kwargs)

    def add_activities(self, *labels) -> Iterator[str]:
        for label in labels:
            yield self.add_activity(label)

    def add_arrival(self, label: str = default_arrival_label, **kwargs) -> str:
        return self.add_node(label, ArrivalNode(label=label), **kwargs)

    def add_terminal(self, label: str = default_terminal_label, **kwargs) -> str:
        return self.add_node(label, TerminalNode(label=label), **kwargs)

    def add_aux_node(self, label: str, node: WithModel, **kwargs):
        assert label not in self.aux_model_havers
        return self.add_node(label, node, **kwargs)

    def add_decision(self, label: str = None, connect_to_arrival=False, connect_to_terminal=False) -> str:
        assert label not in self.aliases
        if label is None:
            label = f'xor{self.decision_id}'
            self.decision_id += 1
        split_label, join_label = gen_suffixed(label)
        split = XorSplit()
        join = XorJoin()
        split.partner = join
        join.partner = split
        self.add_node(split_label, split, connect_to_arrival=connect_to_arrival)
        self.add_node(join_label, join, connect_to_terminal=connect_to_terminal)
        self.aliases[label] = (split_label, join_label)
        return label

    def add_concurrency(self, label=None, number_of_splits=2, connect_to_arrival=False,
                        connect_to_terminal=False) -> str:
        assert label not in self.aliases
        if label is None:
            label = f'and{self.concurrency_id}'
            self.concurrency_id += 1
        split_label, join_label = gen_suffixed(label)
        split = AndSplit()
        join = AndJoin(number_of_splits)
        split.partner = join
        join.partner = split
        self.add_node(split_label, split, connect_to_arrival=connect_to_arrival)
        self.add_node(join_label, join, connect_to_terminal=connect_to_terminal)
        self.aliases[label] = (split_label, join_label)
        return label

    def add_tau(self, label: str = None, **kwargs) -> str:
        if label is None:
            label = f'tau_{self.tau_id}'
            self.tau_id += 1
        self.add_node(label, TauNode(), **kwargs)
        return label

    def get_aliased_label(self, label: str, select_split=True, select_join=False):
        node_label = label
        if label in self.aliases:
            (s, j) = self.aliases[label]
            if select_split and select_join:
                node_label = s, j
            else:
                node_label = s if select_split else j
        return node_label

    def get_corresponding_node(self, label: str, select_split=True, select_join=False):
        node_label = self.get_aliased_label(label, select_split, select_join)
        if isinstance(node_label, tuple):
            return self.node_map.get(node_label[0]), self.node_map.get(node_label[1])
        else:
            return self.node_map.get(node_label)

    def connect_as_loop(self, loop_decision: str, do: str | tuple[str, str], escape: str = None,
                        *redos: list[str | tuple[str, str]]):

        split, join = self.get_aliased_label(loop_decision, select_split=True, select_join=True)
        do = ensure_tuple(do)
        redos = [ensure_tuple(redo) for redo in redos]
        self.connect(join, do[0])
        self.connect(do[1], split)
        if escape is not None:
            self.connect(split, escape)
        if len(redos) > 0:
            self.connect(split, [redo[0] for redo in redos])
            self.connect([redo[1] for redo in redos], join)
        else:
            self.connect(split, join)

    def connect_between_split_join(self, alias: str, betweens: list[str | tuple[str, str]],
                                   add_direct_at_idx: int = None):
        split, join = self.get_aliased_label(alias, select_split=True, select_join=True)
        options = [ensure_tuple(o) for o in betweens]
        if add_direct_at_idx is not None:
            self.connect(split, join)
        self.connect(split, [o[0] for o in options])
        self.connect([o[1] for o in options], join)

    def connect_as_decision(self, decision: str, options: list[str | tuple[str, str]],
                            add_skip_at_idx: int = None):
        self.connect_between_split_join(decision, options, add_direct_at_idx=add_skip_at_idx)

    def connect_as_concurrency(self, concurrency: str, options: list[str | tuple[str, str]],
                               add_direct_at_idx: int = None):
        self.connect_between_split_join(concurrency, options, add_direct_at_idx=add_direct_at_idx)

    def connect(self, from_labels: str | list[str], to_labels: str | list[str]):
        if isinstance(from_labels, str):
            from_labels = [from_labels]
        if isinstance(to_labels, str):
            to_labels = [to_labels]
        for f_l in from_labels:
            f_n = self.get_corresponding_node(f_l, select_split=False, select_join=True)
            if isinstance(f_n, SplittingNode):
                if f_n.successors is None:
                    f_n.successors = []
                for t_n in to_labels:
                    f_n.successors.append(self.get_corresponding_node(t_n, select_split=True))
            elif isinstance(f_n, LinearNode):
                f_n.successor = self.get_corresponding_node(to_labels[0], select_split=True)

    def connect_to_arrival(self, labels: str | list[str],
                           arrival_labels: str | list[str] = default_arrival_label):
        self.connect(arrival_labels, labels)

    def connect_to_terminal(self, labels: str | list[str],
                            terminal_labels: str | list[str] = default_terminal_label):
        self.connect(labels, terminal_labels)

    def _create_alias_relabeling(self):
        res = {}
        for l, (s, j) in self.aliases.items():
            if s in self.aux_model_havers:
                res[s] = l
            elif j in self.aux_model_havers:
                res[j] = l
        return res

    def relabel_aux_model_havers(self, renaming_map, relabel_aliases=True):
        renaming_map = {} if renaming_map is None else dict(renaming_map)
        if relabel_aliases:
            renaming_map.update(self._create_alias_relabeling())
        for k, v in renaming_map.items():
            self.aux_model_havers[v] = self.aux_model_havers[k]
            del self.aux_model_havers[k]

    def build(self, renaming_map: dict[str, str] = None, rename_aliases=True) -> GenericSimulationGraph:
        self.relabel_aux_model_havers(renaming_map, rename_aliases)
        self.fix_and_joins()
        gsg = GenericSimulationGraph(self.arrival_nodes, self.terminal_nodes, self.activity_nodes,
                                     self.aux_model_havers)
        if not self.skip_asserts:
            graph_assertions(gsg)
        return gsg

    def fix_and_joins(self):
        for lab, n in self.node_map.items():
            if isinstance(n, AndJoin):
                actual_splits = len(n.partner.successors)
                if n.parallel_splits != actual_splits:
                    print(f'fixed specified number of splits of {lab}')
                    n.parallel_splits = actual_splits


def config_assertions(graph: GenericSimulationGraph,
                      config: GenericModelConfiguration):
    assert graph.activity_map.keys() <= config.activities.keys()
    assert graph.aux_model_haver_map.keys() <= config.aux_model_configs.keys()
    assert graph.arrivals.keys() <= config.arrivals.keys()


class ModelBuilder(GraphBuilder):

    def __init__(self, initial_graph: GenericSimulationGraph = None, initial_config: GenericModelConfiguration = None,
                 use_defaults=False, skip_asserts=False) -> None:
        self.arrival_configs: dict[str, ArrivalProcessConfig] = {}
        self.activity_configs: dict[str, ActivityConfig] = {}
        self.resource_configs: dict[str, ResourceConfig] = {}
        self.aux_configs: dict[str, ModelHaverConfig] = {}
        self.working_resources: set[str] = set()
        self.working_assignments: dict[str, set[str]] = {}
        self.working_propensities: dict[str, dict[str, float]] = {}
        super(ModelBuilder, self).__init__(initial_graph, use_defaults=use_defaults, skip_asserts=skip_asserts)

        if initial_config is not None:
            self.initialize_with_config(initial_config)

    def initialize_with_config(self, config: GenericModelConfiguration):
        self.arrival_configs = dict(config.arrivals)
        self.activity_configs = dict(config.activities)
        self.resource_configs = dict(config.resources)
        self.aux_configs = dict(config.aux_model_configs)
        self.working_assignments = dict(config.mapping.assignable_resources)
        self.working_propensities = dict(config.mapping.propensities)

    def fill_defaults(self):
        for arr in self.arrival_nodes:
            if arr not in self.arrival_configs:
                self.set_arrival_config(arr, ModelBuilder.default_arrival_config())
        for act in self.activity_nodes:
            if act not in self.activity_configs:
                self.set_activity_config(act, ModelBuilder.default_activity_config())
        for r in self.working_resources:
            if r not in self.resource_configs:
                self.set_resource_config(r, ModelBuilder.default_resource_config())

    @staticmethod
    def default_arrival_config():
        return ArrivalProcessConfig(datetime(2023, 3, 23, 12, 0),
                                    impls.StaticSampler(timedelta(hours=1)))

    @staticmethod
    def default_activity_config():
        return ActivityConfig(impls.Fifo, impls.StaticSampler(timedelta(hours=1)))

    @staticmethod
    def default_resource_config():
        return ResourceConfig(1)

    def set_activity_config(self, label: str, config: ActivityConfig):
        assert label not in self.activity_configs
        if config is None and self.use_defaults:
            config = ModelBuilder.default_activity_config()
        if config is not None:
            self.activity_configs[label] = config

    def add_activity(self, label: str, config: ActivityConfig = None, assignable_resources: Iterable[str] = None,
                     resource_propensities: dict[str, float] = None,
                     connect_to_arrival=False, connect_to_terminal=False,
                     **kwargs) -> str:
        super().add_activity(label, connect_to_arrival=connect_to_arrival, connect_to_terminal=connect_to_terminal,
                             **kwargs)
        self.set_activity_config(label, config)
        self.update_working_mapping(label, assignable_resources, resource_propensities)
        return label

    def add_activities(self, *labels) -> Iterator[str]:
        for label in labels:
            yield self.add_activity(label)

    def set_default_arrival_config(self, config: ArrivalProcessConfig) -> None:
        self.arrival_configs[default_arrival_label] = config

    def set_arrival_config(self, label: str, config: ArrivalProcessConfig) -> None:
        assert label not in self.arrival_configs
        if config is None and self.use_defaults:
            config = ModelBuilder.default_arrival_config()
        if config is not None:
            self.arrival_configs[label] = config

    def set_arrival_configs(self, configs: dict[str, ArrivalProcessConfig]) -> None:
        self.arrival_configs = configs

    def add_arrival(self, label: str = default_arrival_label, config: ArrivalProcessConfig = None, **kwargs) -> str:
        super().add_arrival(label, **kwargs)
        self.set_arrival_config(label, config)
        return label

    def set_assignments(self, config: Union[MappingConfig, dict[str, set[str]]]):
        if isinstance(config, MappingConfig):
            self.working_assignments = config.assignable_resources
            self.working_propensities = config.propensities
        else:
            self.working_assignments = config

    def set_assignment_propensities(self, config: Union[MappingConfig, dict[str, dict[str, float]]]):
        if isinstance(config, MappingConfig):
            self.working_assignments = config.assignable_resources
            self.working_propensities = config.propensities
        else:
            self.working_propensities = config

    def set_aux_config(self, label: str, config: ModelHaverConfig):
        if config is not None:
            self.aux_configs[label] = config

    def add_decision(self, label: str = None, config: ModelHaverConfig = None, **kwargs) -> str:
        label = super().add_decision(label, **kwargs)
        s, j = self.aliases[label]
        self.set_aux_config(s, config)
        return label

    def add_aux_node(self, label: str, node: WithModel, config: ModelHaverConfig = None, **kwargs) -> str:
        assert label not in self.aux_model_havers
        super().add_aux_node(label, node, **kwargs)
        self.set_aux_config(label, config)
        return label

    def set_resource_config(self, label: str, config):
        if config is not None:
            self.resource_configs[label] = config

    def add_resource(self, label: str, config: ResourceConfig = None, assignable_activities=None) -> str:
        assert label not in self.working_resources and label not in self.resource_configs
        self.working_resources.add(label)
        if config is None and self.use_defaults:
            config = ModelBuilder.default_resource_config()
        self.set_resource_config(label, config)
        if assignable_activities is not None:
            if isinstance(assignable_activities, str):
                assignable_activities = [assignable_activities]
            if isinstance(assignable_activities, Iterable):
                for a in assignable_activities:
                    if a not in self.activity_configs:
                        self.add_activity(a)
                    self.update_working_mapping(a, [label])
        return label

    def set_config(self, label: str, config, auto_select_alias=True):
        if label in self.arrival_nodes:
            self.set_arrival_config(label, config)
        elif label in self.activity_nodes:
            self.set_activity_config(label, config)
        elif label in self.aux_model_havers:
            self.set_aux_config(label, config)
        elif label in self.aliases and auto_select_alias:
            s, j = self.aliases[label]
            if s in self.aux_model_havers:
                self.set_aux_config(s, config)
            elif j in self.aux_model_havers:
                self.set_aux_config(j, config)
        elif label in self.working_resources or label in self.resource_configs:
            self.set_resource_config(label, config)

    def relabel_aux_model_havers(self, renaming_map=None, relabel_aliases=True):
        renaming_map = {} if renaming_map is None else dict(renaming_map)
        if relabel_aliases:
            renaming_map.update(self._create_alias_relabeling())
        super().relabel_aux_model_havers(renaming_map, relabel_aliases=False)
        for k, v in renaming_map.items():
            self.aux_configs[v] = self.aux_configs[k]
            del self.aux_configs[k]

    def update_working_mapping(self, label: str, assignable_resources: Iterable[str],
                               resource_propensities: dict[str, float] = None):
        if assignable_resources is not None:
            if isinstance(assignable_resources, str):
                assignable_resources = [assignable_resources]
            if isinstance(assignable_resources, Iterable):
                for r in assignable_resources:
                    if label not in self.working_assignments:
                        self.working_assignments[label] = set()
                    self.working_assignments[label].add(r)
        if resource_propensities is not None:
            for r, p in resource_propensities.items():
                if label not in self.working_propensities:
                    self.working_propensities[label] = dict()
                self.working_propensities[label][r] = p

    def _complete_propensities(self):
        for a, rs in self.working_assignments.items():
            if a not in self.working_propensities:
                self.working_propensities[a] = {}
            for r in rs:
                if r not in self.working_propensities[a]:
                    self.working_propensities[a][r] = 1

    def __create_mapping_config(self):
        self._complete_propensities()
        assert all(r in self.working_propensities[a] for a, rs in self.working_assignments.items() for r in rs)
        return MappingConfig(self.working_assignments, self.working_propensities)

    def build(self, renaming_map=None, rename_aliases=True) -> Tuple[GenericSimulationGraph, GenericModelConfiguration]:
        graph = super().build(renaming_map, rename_aliases)
        config = GenericModelConfiguration(self.arrival_configs, self.activity_configs, self.resource_configs,
                                           self.aux_configs, self.__create_mapping_config())
        if not self.skip_asserts:
            config_assertions(graph, config)
        return graph, config


def iterate_graph_nodes(graph: GenericSimulationGraph):
    seen = set()

    for arr in graph.arrivals.values():
        todo = [arr]

        while len(todo) > 0:
            current = todo.pop()

            if current in seen:
                continue

            seen.add(current)
            yield current

            if isinstance(current, LinearNode):
                succ = current.successor
                if succ not in seen:
                    todo.append(succ)
            elif isinstance(current, SplittingNode):
                for succ in current.successors:
                    if succ not in seen:
                        todo.append(succ)


def graph_assertions(graph: GenericSimulationGraph):
    nodes = []
    if isinstance(graph, GenericSimulationGraph):
        assert len(graph.arrivals) > 0
        assert len(graph.terminals) > 0
        nodes = iterate_graph_nodes(graph)
    for node in nodes:
        if isinstance(node, LinearNode):
            assert node.successor is not None, f'{node} has no successor'
        elif isinstance(node, SplittingNode):
            assert node.successors is not None, f'{node} has no successors'
