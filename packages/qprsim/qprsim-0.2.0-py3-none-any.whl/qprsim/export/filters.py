from __future__ import annotations

from collections.abc import Iterable, Collection, Mapping
from typing import Union, Callable

from qprsim.core import case as sc
from ..shared.enums import AvailableLifecycles


def apply_ev_filters(cases: Iterable[sc.Case], *filters: Callable[[sc.CaseEvent], bool]) -> Iterable[sc.Case]:
    return (c.filter(lambda e: all(f(e) for f in filters)) for c in cases)


def apply_ev_transforms(cases: Iterable[sc.Case], *trans: Callable[[sc.CaseEvent], sc.CaseEvent]) -> Iterable[sc.Case]:
    for t in trans:
        cases = [c.project(projection=t) for c in cases]
    return cases


def apply_case_filters(cases: Iterable[sc.Case], *filters: Callable[[sc.Case], bool]) -> Iterable[sc.Case]:
    return (c for c in cases if all(f(c) for f in filters))


def apply_case_transforms(cases: Iterable[sc.Case], event_filter: Callable[[sc.CaseEvent], bool],
                          event_projection: Callable[[sc.CaseEvent], sc.CaseEvent], attribute_filter: set[str] = None,
                          case_id_redefinition: Callable[[sc.Case], str] = None) -> Iterable[sc.Case]:
    return (c.project(condition=event_filter, projection=event_projection, attr_filter=attribute_filter,
                      case_id_redefinition=case_id_redefinition) for c in cases)


def chain_modifications(cases: Iterable[sc.Case], ev_filters: Collection[Callable[[sc.CaseEvent], bool]] = (),
                        case_filters: Collection[Callable[[sc.Case], bool]] = (),
                        ev_transforms: Collection[Callable[[sc.CaseEvent], sc.CaseEvent]] = ()) -> Iterable[sc.Case]:
    return apply_ev_transforms(apply_case_filters(apply_ev_filters(cases, *ev_filters), *case_filters), *ev_transforms)


def make_lifecycle_filter(allowed_lifecycles: dict[str, AvailableLifecycles] | AvailableLifecycles) -> Callable[
    [sc.CaseEvent], bool]:
    from qprsim.shared.enums import AvailableLifecycles
    lifecycle_filter = None
    if isinstance(allowed_lifecycles, dict):
        def lifecycle_filter(e):
            return e.activity in allowed_lifecycles and e.lifecycle in allowed_lifecycles[e.activity].vals
    elif isinstance(allowed_lifecycles, AvailableLifecycles):
        def lifecycle_filter(e):
            return e.lifecycle in allowed_lifecycles.vals
    return lifecycle_filter


def make_agg_filter_and_projection(case: sc.Case, event_agg_cond: Callable[[sc.CaseEvent], bool], agg_group_attr: str,
                                   agg_attrs: Collection[str] | Mapping[str, str]) -> (
        Callable[[sc.CaseEvent], bool], Callable[[sc.CaseEvent], sc.CaseEvent]):
    vals = {ce.attributes.get(agg_group_attr) for ce in case if event_agg_cond(ce)}
    sames = [[ce for ce in case if event_agg_cond(ce) and ce.attributes.get(agg_group_attr) == val] for val in vals]
    if agg_attrs:
        if not isinstance(agg_attrs, Mapping):
            agg_attrs = {k: k for k in agg_attrs}
        aggd = {agg_attr: [tuple(e.attributes.get(agg_attr) for e in l) for l in sames] for agg_attr in agg_attrs}
    lasts = [l[-1] for l in sames]
    not_lasts = [l[:-1] for l in sames]

    def is_not_not_last_of(e: sc.CaseEvent) -> bool:
        return not any(e in l for l in not_lasts)

    def trans_last_of(e: sc.CaseEvent) -> sc.CaseEvent:
        if agg_attrs and e in lasts:
            kw = {k: v for k, v in e.attributes.items() if k not in agg_attrs}
            kw.update({agg_attr_rename: aggd[agg_attr][lasts.index(e)] for agg_attr, agg_attr_rename in
                       agg_attrs.items()})
            return e.map(attributes=kw)
        else:
            return e

    return is_not_not_last_of, trans_last_of
