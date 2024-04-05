from __future__ import annotations

import graphviz
from pm4py.visualization.petri_net import visualizer as petri_visualizer


def visualize_petrinet(petrinet_model):
    return petri_visualizer.apply(petrinet_model.net, petrinet_model.im, petrinet_model.fm)


def save_petrinet(gviz, filename):
    gc = gviz.copy()
    gc.attr('graph', {'rankdir': 'TB'})
    return petri_visualizer.save(gc, filename)


def view(gg: graphviz.Digraph):
    return gg


def view_horizontal(gg: graphviz.Digraph):
    gc = gg.copy()
    gc.attr('graph', {'rankdir': 'LR'})
    return gc


def save(gg: graphviz.Digraph, filename):
    gg.render(filename, format='pdf')


def save_horizontal(gg: graphviz.Digraph, filename):
    gc = gg.copy()
    gc.attr('graph', {'rankdir': 'LR'})
    return gc.render(filename, format='pdf')
