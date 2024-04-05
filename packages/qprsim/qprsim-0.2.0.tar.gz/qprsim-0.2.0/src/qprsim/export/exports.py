from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Iterable, Callable

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.util import xes_constants
from pm4py.write import write_xes, write_pnml

if TYPE_CHECKING:
    import qprsim.execution
    import qprsim.core.case


def save_log(log: EventLog, filename: str = 'log.xes', **kwargs):
    write_xes(log, filename, **kwargs)


def save_simulated_log(simulator: qprsim.execution.Simulator, filename: str = None):
    save_log(simulator.create_log(),
             filename=f'simulated_log_{datetime.datetime.now()}.xes' if filename is None else filename)


def save_petrinet(net, im, fm, filename: str = 'net.apnml'):
    write_pnml(net, im, fm, file_path=filename)


def create_log(cases: Iterable[qprsim.core.case.Case], case_id_map: Callable[[int, str], str] = None, log_name='simulated log') -> EventLog:
    log = EventLog()
    log.attributes[xes_constants.DEFAULT_NAME_KEY] = log_name

    for i, case in enumerate(cases):

        trace = Trace()
        trace.attributes[xes_constants.DEFAULT_TRACEID_KEY] = case.case_id if case_id_map is None else case_id_map(i,
                                                                                                                   case.case_id)
        for k, v in case.attributes.items():
            trace.attributes[k] = v

        for case_event in case:
            event = Event()

            event[xes_constants.DEFAULT_NAME_KEY] = case_event.activity
            event[xes_constants.DEFAULT_TIMESTAMP_KEY] = case_event.timestamp
            event[xes_constants.DEFAULT_RESOURCE_KEY] = case_event.resource
            event[xes_constants.DEFAULT_TRANSITION_KEY] = case_event.lifecycle
            for k, v in case_event.attributes.items():
                event[k] = v

            trace.append(event)

        log.append(trace)

    return log


