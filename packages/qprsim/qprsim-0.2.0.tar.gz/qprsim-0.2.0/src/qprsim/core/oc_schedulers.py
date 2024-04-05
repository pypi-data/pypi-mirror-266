import logging
from typing import Callable

import qprsim.config.model_configuration as params
from .event_system import Event, Scheduler, EventQueue, Updatable, BusinessHourEvent
from .oc_events import *
from qprsim.utils import time_utils


class OCArrivalProcessScheduler(Scheduler):

    def __init__(self, event_queue: EventQueue, inter_arrival_sampler: params.InterArrivalSampler, label: str = None,  creation_count_limit=None, date_limit=None,
                 external_termination_check: Callable[..., bool] = None,
                 **kwargs) -> None:
        super(OCArrivalProcessScheduler, self).__init__(event_queue=event_queue, **kwargs)
        self.date_limit = date_limit
        self.count_limit = creation_count_limit
        self.external_termination_check = external_termination_check
        self.label = label if label else 'process_0'
        self.inter_arrival_sampler = inter_arrival_sampler
        self.actual_arrival_counter = 0
        self.arrival_scheduled_counter = 0
        self.next_scheduled_arrival = None

    def initial_event(self) -> Event:
        return self.next_event(self.event_queue.global_time)  # possibly incorrect assumption

    def should_terminate(self) -> bool:
        return super(OCArrivalProcessScheduler, self).should_terminate() or (
                self.date_limit is not None and self.event_queue.global_time >= self.date_limit) or (
                self.external_termination_check is not None and self.external_termination_check())

    def create_case_id(self):
        source = self.label
        idx = self.actual_arrival_counter
        return f'{source}_{idx}'

    def next_event(self, next_time: datetime) -> Event:
        proposed_case_id = self.create_case_id()
        arrival_event = ObjectArrivalEvent(self.label, self.actual_arrival_counter, self.arrival_scheduled_counter,
                                           proposed_case_id, next_time)
        self.arrival_scheduled_counter += 1
        return arrival_event

    def _update_state(self, event: UpdateEvent) -> None:
        super()._update_state(event)
        self.actual_arrival_counter += 1

    def next_time(self, current_time: datetime) -> datetime:
        delta = self.inter_arrival_sampler.sample(current_time)
        time = time_utils.add(current_time, delta)
        logging.info(f'arrival process {self.label} sampled iat {current_time}, {delta}, {time}')
        self.next_scheduled_arrival = time
        return time


class ScheduledOCArrivalProcessScheduler(OCArrivalProcessScheduler, Updatable):

    def __init__(self, *args, **kwargs) -> None:
        super(ScheduledOCArrivalProcessScheduler, self).__init__(*args, **kwargs)
        self.scheduler: Scheduler = kwargs.get('scheduler')
        self.pause()

    def stop(self) -> None:
        super(ScheduledOCArrivalProcessScheduler, self).stop()
        if self.scheduler is not None:
            self.scheduler.remove_client(self)

    def unpause(self) -> None:
        self._paused = False
        if self.next_scheduled_arrival is None or self.next_scheduled_arrival < self.event_queue.global_time:
            self.start()

    def discard_event(self, event: Event) -> None:
        logging.info(f'arrival process {self.label} discarded {event}')

    def receive_event(self, event: BusinessHourEvent):
        logging.info(f'arrival process {self.label} {"un" if event.new_value else ""}paused')
        if event.new_value:
            self.unpause()
        else:
            self.pause()
