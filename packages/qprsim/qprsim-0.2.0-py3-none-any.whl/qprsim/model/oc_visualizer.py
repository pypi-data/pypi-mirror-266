from __future__ import annotations

import graphviz
import pydotplus

from .oc_sim_graph import OCSimulationGraph, BirthplaceNode, GraveyardNode, AndSplit, AndJoin, XorSplit, \
    OCSplit, OCJoin, OCTransformerNode, XorJoin, ActivityNode, TauNode, LinearNode, SplittingNode


def visualize_sim_graph(graph: OCSimulationGraph, extended_node_labels=False,
                        extended_edge_labels=False):
    gg = graphviz.Digraph()
    # g = pydotplus.Dot() alternative

    reverse_label_map = {v: k for k, v in graph.aux_model_haver_map.items()}

    seen = set()
    node_map = {}
    name_map = {}
    count = 0
    for arrival in graph.birthplaces.values():
        todo = [arrival]
        todo_edges = []

        while len(todo) > 0:
            current = todo.pop()
            if current in seen:
                continue
            seen.add(current)

            node = None
            name = None
            if isinstance(current, BirthplaceNode):
                name = current.label
                node = pydotplus.Node(name=name)
                gg.node(name)
            elif isinstance(current, GraveyardNode):
                name = current.label
                node = pydotplus.Node(name=name)
                gg.node(name=name)
            elif isinstance(current, AndSplit):
                name = 'AndSplit' + str(count)
                node = pydotplus.Node(name=name, shape='diamond', label='+')
                gg.node(name=name, shape='diamond', label='+')
            elif isinstance(current, AndJoin):
                name = 'AndJoin' + str(count)
                node = pydotplus.Node(name=name, shape='diamond', label='+')
                gg.node(name=name, shape='diamond', label='+')
            elif isinstance(current, XorSplit | OCSplit | OCTransformerNode):
                type_name = type(current).__name__
                shape = 'diamond'
                label = 'n/a'
                if isinstance(current, XorSplit):
                    label = 'X'
                elif isinstance(current, OCSplit):
                    label = 'S'
                elif isinstance(current, OCTransformerNode):
                    label = 'T'
                if extended_node_labels:
                    specific_label = reverse_label_map[current]
                    label = f'{label} ({specific_label})'
                name = f'{type_name} {count}'
                node = pydotplus.Node(name=name, shape=shape, label=label)
                gg.node(name=name, shape=shape, label=label)
            elif isinstance(current, OCJoin):
                name = 'OCJoin' + str(count)
                node = pydotplus.Node(name=name, shape='diamond', label='J')
                gg.node(name=name, shape='diamond', label='J')
            elif isinstance(current, XorJoin):
                name = 'XorJoin' + str(count)
                node = pydotplus.Node(name=name, shape='diamond', label='X')
                gg.node(name=name, shape='diamond', label='X')
            elif isinstance(current, ActivityNode):
                name = current.label
                if ':' in name:
                    name = str.replace(name, ':', 'colon')
                node = pydotplus.Node(name=name, shape='box', style='rounded', label=name)
                gg.node(name=name, shape='box', style='rounded', label=name)
            elif isinstance(current, TauNode):
                name = 'tau' + str(count)
                node = pydotplus.Node(name=name, shape='box', label='tau', color='black')
                gg.node(name=name, shape='box', label='tau', fillcolor='gray', style='filled')
            else:
                print(type(current))
                print(current)
                print(name, node)
            assert node is not None
            assert current not in node_map
            count += 1
            node_map[current] = node
            name_map[current] = name
            # g.add_node(node)

            if isinstance(current, LinearNode):
                edge_args = {}
                succ = current.successor
                if succ is None:
                    print(name, current, 'has a None successor')
                if succ not in seen:
                    todo.append(succ)
                todo_edges.append((current, succ, edge_args))
            elif isinstance(current, SplittingNode):
                for i, succ in enumerate(current.successors):
                    edge_args = {}
                    if succ is None:
                        print(name, current, 'has a None successor')
                    if succ not in seen:
                        todo.append(succ)
                    if extended_edge_labels:
                        edge_args.update({'label': str(i)})
                    todo_edges.append((current, succ, edge_args))

        for n1, n2, kwargs in todo_edges:
            # e = pydotplus.Edge(node_map[n1], node_map[n2])
            # g.add_edge(e)
            gg.edge(name_map[n1], name_map[n2], **kwargs)

    return gg
