from __future__ import annotations

import itertools
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Any, List, Union, Tuple, Callable, TYPE_CHECKING, Sequence, Iterable

import numpy as np

from qprsim import config
from qprsim.config import impls
from qprsim.core import event_system as ev_sys, managers as smanagers
from qprsim.model import sim_graph as sgraph, model_parameters as params, conceptual_models as cm, graph_models as gm, model_data as mdata
from qprsim.shared.enums import AvailableLifecycles, ExecutionParameters, ActivityProperty, ResourceProperty
from qprsim.utils import time_utils, utils

if TYPE_CHECKING:
    import qprsim.core.case as sc


def default_execution_parameters():
    execution_parameters = {ExecutionParameters.CasesToGenerate: 1000,
                            ExecutionParameters.GenerationCutoffDate: None,
                            ExecutionParameters.SimStartDate: None,
                            ExecutionParameters.SimCutoffDate: None,
                            ExecutionParameters.RealtimeLimit: timedelta(seconds=30)}
    return execution_parameters


class SimulationContext:

    def __init__(self):
        self._started_cases_count = 0
        self._completed_cases_count = 0
        self._aborted_cases_count = 0
        self._active_cases = {}
        self.case_collections = {}

    def register_case_collection(self, label: str, case_collection: Sequence[sc.Case]):
        self.case_collections[label] = case_collection

    def register_case_creation(self, case: sc.Case, source=None):
        self._started_cases_count += 1
        self._active_cases[case.case_id] = case

    def register_case_completion(self, case: sc.Case, sink=None):
        self._completed_cases_count += 1
        del self._active_cases[case.case_id]

    def register_case_abortion(self, case: sc.Case, context=None):
        self._aborted_cases_count += 1
        del self._active_cases[case.case_id]

    def are_active_cases_remaining(self) -> bool:
        return self.started_cases_count > self.completed_cases_count + self.aborted_cases_count

    @property
    def remaining_active_cases(self) -> Iterable[sc.Case]:
        return self._active_cases.values()

    @property
    def started_cases_count(self) -> int:
        return self._started_cases_count

    @property
    def completed_cases_count(self) -> int:
        return self._completed_cases_count

    @property
    def aborted_cases_count(self) -> int:
        return self._aborted_cases_count

    @property
    def completed_cases(self) -> Iterable[sc.Case]:
        return itertools.chain(*self.case_collections.values())


@dataclass
class Schedulables:
    arrival_models: Dict[str, gm.ArrivalModel]
    activity_datas: Dict[str, mdata.ActivityData]
    resource_datas: Dict[str, mdata.ResourceData]


class SchedulingManager:

    def __init__(self, event_queue: ev_sys.EventQueue, schedulables: Schedulables,
                 simulation_context: SimulationContext,
                 execution_parameters: Dict[ExecutionParameters, Any]) -> None:
        self.event_queue: ev_sys.EventQueue = event_queue
        self.arrival_models = schedulables.arrival_models
        self.arrival_processes: Dict[str, Tuple[config.ArrivalProcessConfig, ev_sys.ArrivalProcessScheduler]] = {}
        self.activity_datas: Dict[str, mdata.ActivityData] = schedulables.activity_datas
        self.resource_datas: Dict[str, mdata.ResourceData] = schedulables.resource_datas
        self.simulation_context = simulation_context
        self.execution_parameters = execution_parameters

        self._client_scheduler_map: Dict[ev_sys.Updatable, ev_sys.BusinessHoursScheduler] = {}
        self._bh_schedulers: Dict[params.BusinessHours, ev_sys.BusinessHoursScheduler] = {}
        self._unstarted_schedulers: List[Tuple[int, ev_sys.BusinessHoursScheduler]] = []

    def _schedule_business_hours(self, client: ev_sys.Updatable,
                                 business_hours: params.BusinessHours = impls.AlwaysInBusiness, priority: int = 1,
                                 when: datetime = None) -> ev_sys.BusinessHoursScheduler:
        if business_hours is None:
            business_hours = impls.AlwaysInBusiness
        if client in self._client_scheduler_map:
            #  duplicated in the case of arrival process as it removes itself from its scheduler
            self._client_scheduler_map[client].remove_client(client)
        scheduler: ev_sys.BusinessHoursScheduler
        if business_hours not in self._bh_schedulers:
            scheduler = ev_sys.BusinessHoursScheduler(self.event_queue, business_hours, intended_start=when)
            self._unstarted_schedulers.append((priority, scheduler))
            self._bh_schedulers[business_hours] = scheduler
        else:
            scheduler = self._bh_schedulers[business_hours]
        scheduler.add_client(client)
        self._client_scheduler_map[client] = scheduler
        return scheduler

    def start_schedulers(self):
        # start according to the highest priority
        for _, scheduler in sorted(self._unstarted_schedulers, key=lambda t: t[0], reverse=True):
            scheduler.start()
        self._unstarted_schedulers.clear()

    def cleanup_schedulers(self):
        to_remove = set()
        for bh, scheduler in self._bh_schedulers.items():
            if not scheduler.has_clients:
                scheduler.force_terminate()
            if scheduler.has_terminated:
                to_remove.add(bh)
        for bh in to_remove:
            del self._bh_schedulers[bh]

    def add_arrival_process(self, arrival_label: str, arrival_config: config.ArrivalProcessConfig):
        limit = self.execution_parameters.get(ExecutionParameters.CasesToGenerate, np.Inf)

        def external_termination_check():
            return self.simulation_context.started_cases_count >= limit

        date_limit = None
        gen_stop_date = self.execution_parameters.get(ExecutionParameters.GenerationCutoffDate, None)
        if gen_stop_date is not None:
            date_limit = time_utils.make_timezone_aware(gen_stop_date)
        if arrival_config.last_arrival is not None:
            last_arrival = time_utils.make_timezone_aware(arrival_config.last_arrival)
            if date_limit is not None:
                date_limit = min(last_arrival, date_limit)
            else:
                date_limit = last_arrival

        arrival_process = ev_sys.ScheduledArrivalProcessScheduler(self.event_queue, arrival_config.inter_arrivals,
                                                                  current_creation_count=self.simulation_context.started_cases_count,
                                                                  creation_count_limit=self.execution_parameters.get(
                                                                      ExecutionParameters.CasesToGenerate),
                                                                  date_limit=date_limit,
                                                                  label=arrival_label,
                                                                  attribute_generator=arrival_config.attribute_generator,
                                                                  external_termination_check=external_termination_check,
                                                                  strict=True)

        arrival_process.add_client(self.arrival_models[arrival_label])
        arrival_process_scheduler = self._schedule_business_hours(arrival_process, arrival_config.business_hours,
                                                                  priority=2, when=arrival_config.first_arrival)
        arrival_process.scheduler = arrival_process_scheduler
        self.arrival_processes[arrival_label] = (arrival_config, arrival_process)

    def remove_arrival_process(self, arrival_label: str = None):
        if arrival_label is None:  # last added arrival process
            arrival_config, arrival_process = self.arrival_processes.popitem()[1]
        else:
            arrival_config, arrival_process = self.arrival_processes[arrival_label]
            del self.arrival_processes[arrival_label]
        arrival_process.force_terminate()

    def set_activity_business_hours(self, activity: str, business_hours: params.BusinessHours):
        self._schedule_business_hours(self.activity_datas[activity], business_hours)

    def set_resource_business_hours(self, resource: str, business_hours: params.BusinessHours):
        self._schedule_business_hours(self.resource_datas[resource], business_hours)

    def start(self):
        self.start_schedulers()

    def perform_hot_change(self, change: Callable[..., None]):
        self.cleanup_schedulers()
        change()
        self.start_schedulers()


@dataclass(unsafe_hash=True)
class SimulationModel:
    graph: sgraph.GenericSimulationGraph
    event_queue: ev_sys.EventQueue
    scheduling_manager: SchedulingManager
    activity_manager: smanagers.ActivityManager
    resource_manager: smanagers.ResourceManager
    simulation_context: SimulationContext
    execution_parameters: dict[ExecutionParameters, Any]


class Simulator:
    time_check_interval = 10

    def __init__(self, simulation_model: SimulationModel) -> None:
        self.simulation_model = simulation_model
        self.scheduling_manager = simulation_model.scheduling_manager
        self.event_queue = simulation_model.event_queue
        self.exp = simulation_model.execution_parameters
        self._collected_cases_iterable = (c for c in simulation_model.simulation_context.completed_cases)
        self.termination_checks = []

        self.dirty: bool = False
        self.simulation_start: datetime | None = None
        self.simulation_end: datetime | None = None
        self.iteration: int = 0
        self._generated_cases: list | None = None

    def setup(self):
        self.dirty = True
        self.simulation_start = time_utils.now()
        self.iteration = 0

        self.termination_checks = [(lambda: self.event_queue.empty(), 'Terminated due to event queue being empty.')]

        if self.exp.get(ExecutionParameters.CasesToSim) is not None:
            case_limit = self.exp[ExecutionParameters.CasesToSim]

            def cases_to_sim():
                return self.simulation_model.simulation_context.completed_cases_count >= case_limit

            self.termination_checks.append((cases_to_sim, 'Terminated due to CasesToSim being reached.'))

        if self.exp.get(ExecutionParameters.SimCutoffDate) is not None:
            sim_limit = time_utils.make_timezone_aware(self.exp[ExecutionParameters.SimCutoffDate])

            def sim_cutoff_date():
                return self.event_queue.global_time > sim_limit

            self.termination_checks.append(
                (sim_cutoff_date, 'Terminated due to simulation stopping date being reached.'))

        if self.exp.get(ExecutionParameters.RealtimeLimit) is not None:
            rl_limit = time_utils.add(self.simulation_start, self.exp[ExecutionParameters.RealtimeLimit])

            def realtime_cutoff_date():
                return self.iteration % self.time_check_interval == 0 and rl_limit < time_utils.now()

            self.termination_checks.append(
                (realtime_cutoff_date, 'Terminated due to execution time limit being reached.'))

        if self.exp.get(ExecutionParameters.GenerationCutoffDate) is not None:
            cutoff_date = time_utils.make_timezone_aware(self.exp[ExecutionParameters.GenerationCutoffDate])

            def generation_date_cutoff():
                return self.event_queue.global_time > cutoff_date and not self.simulation_model.simulation_context.are_active_cases_remaining()

            self.termination_checks.append((generation_date_cutoff,
                                            'Terminated due to GenerationCutoffDate being reached along with no remaining active cases.'))

    def run(self, simulation_log_filename=None):
        assert not self.dirty

        self.setup()

        if simulation_log_filename is not None:
            utils.ensure_path_exists(simulation_log_filename)
            logging.basicConfig(
                filename=simulation_log_filename,
                filemode='w', level=logging.INFO, force=True)
            logging.info(f'Started Simulation @{self.simulation_start} with the following execution parameters')
            logging.info(str(self.exp))

        self.scheduling_manager.start()

        while all(not c() for c, desc in self.termination_checks):
            self.event_queue.step()
            self.iteration += 1

        for c, desc in self.termination_checks:
            if c():
                logging.info(desc)

        self.simulation_end = time_utils.now()

    @property
    def generated_cases(self) -> list[sc.Case]:
        if self._generated_cases is None:
            self._generated_cases = [c for c in self._collected_cases_iterable]
        return self._generated_cases

    @property
    def duration(self) -> timedelta:
        return self.simulation_end - self.simulation_start

    def create_log(self, allowed_lifecycles: Union[Dict[str, AvailableLifecycles], AvailableLifecycles] = None, custom_filter: Callable[[sc.CaseEvent], bool] = None):
        from qprsim.utils import exporting
        filter_method = None
        lifecycle_filter = None

        if allowed_lifecycles is not None:
            if isinstance(allowed_lifecycles, dict):
                def lifecycle_filter(e):
                    return e.activity in allowed_lifecycles and e.lifecycle in allowed_lifecycles[e.activity].vals
            elif isinstance(allowed_lifecycles, AvailableLifecycles):
                def lifecycle_filter(e):
                    return e.lifecycle in allowed_lifecycles.vals

        if lifecycle_filter is not None and custom_filter is not None:
            filter_method = lambda e: lifecycle_filter(e) and custom_filter(e)
        elif lifecycle_filter is not None:
            filter_method = lifecycle_filter
        elif custom_filter is not None:
            filter_method = custom_filter

        iterable = (c.filter(filter_method) for c in
                    self.generated_cases) if filter_method is not None else self.generated_cases

        return exporting.create_log(iterable)


def simulate(configured_simulation_model: SimulationModel, create_log_file=True,
             simulation_log_filename=None) -> Simulator:
    simulator = Simulator(configured_simulation_model)
    if create_log_file and simulation_log_filename is None:
        simulation_log_filename = f'{time_utils.filenameable_timestamp()}.log'
    simulator.run(simulation_log_filename=simulation_log_filename)
    return simulator


def configure_activity(event_queue: ev_sys.EventQueue, activity_manager: smanagers.ActivityManager,
                       activity_node: sgraph.ActivityNode, activity_configuration: config.ActivityConfig):
    a_model = gm.ActivityModel(activity_node, event_queue, activity_manager=activity_manager)
    a_data = mdata.ActivityData(a_model)
    if activity_configuration.property_dict is not None:
        a_data.properties.update(activity_configuration.property_dict)
    a_data.properties[ActivityProperty.QueueingDiscipline] = activity_configuration.queueing_discipline
    a_data.properties[
        ActivityProperty.ProcessingTimeSampler] = activity_configuration.processing_time_sampler
    if activity_configuration.delay_sampler is not None:
        a_data.properties[ActivityProperty.DelaySampler] = activity_configuration.delay_sampler
    if activity_configuration.attribute_generator is not None:
        a_data.properties[
            ActivityProperty.EventAttributeGenerator] = activity_configuration.attribute_generator
    # assert sim.enums.ActivityProperty.vals <= a_data.properties.keys()  # make sure everything is configured
    a_model.data = a_data
    activity_node.model = a_model
    return a_model


def configure_resource(event_queue: ev_sys.EventQueue, rm: smanagers.ResourceManager, resource_label: str,
                       resource_config: config.ResourceConfig):
    resource = cm.ResourceModel(resource_label, event_queue, resource_manager=rm)
    r_data = mdata.ResourceData(resource)
    if resource_config.property_dict is not None:
        r_data.properties.update(resource_config.property_dict)
    r_data.properties[ResourceProperty.Capacity] = resource_config.capacity
    if resource_config.performance is not None:
        r_data.properties[ResourceProperty.Performance] = resource_config.performance
    # assert sim.enums.ResourceProperty.vals <= r_data.properties.keys()  # make sure everything is configured
    resource.data = r_data
    return resource


def configure_aux(node: sgraph.WithModel, cfg: config.ModelHaverConfig, **kwargs):
    model = cfg.instantiate_model(node=node, **kwargs)
    node.model = model
    return model


def create_simulation_model(simulation_graph: sgraph.GenericSimulationGraph,
                            model_configuration: config.GenericModelConfiguration,
                            execution_parameters: dict[ExecutionParameters, Any] = None) -> SimulationModel:
    assert simulation_graph.activity_map.keys() <= model_configuration.activities.keys()
    if execution_parameters is None:
        execution_parameters = default_execution_parameters()

    context = SimulationContext()

    arrival_nodes = simulation_graph.arrivals
    for arrival_label, node in arrival_nodes.items():
        node.model = gm.ArrivalModel(node=node, simulation_context=context)
    for terminal_label, node in simulation_graph.terminals.items():
        node.model = gm.TerminalModel(node=node, label=terminal_label, simulation_context=context)

    event_queue = ev_sys.EventQueue()

    earliest = min(ac.first_arrival for ac in model_configuration.arrivals.values())
    earliest = time_utils.make_timezone_aware(earliest)
    start_datetime_override = execution_parameters.get(ExecutionParameters.SimStartDate)
    if start_datetime_override is not None:
        earliest = max(earliest, time_utils.make_timezone_aware(start_datetime_override))
    event_queue.global_time = earliest

    rm = smanagers.ResourceManager(event_queue)
    am = smanagers.ActivityManager(event_queue)
    am.resource_manager = rm
    rm.activity_manager = am

    for label, node in simulation_graph.aux_model_haver_map.items():
        cfg = model_configuration.aux_model_configs[label]
        if cfg.requires_unsafe_access:
            configure_aux(node, cfg, event_queue=event_queue, activitiy_manager=am,
                          resource_manager=rm, simulation_context=context)
        else:
            configure_aux(node, cfg)

    activity_nodes = simulation_graph.activity_map
    for activity_label, node in activity_nodes.items():
        configure_activity(event_queue, am, node,
                           model_configuration.activities[activity_label])

    resources = {}
    for resource_label, resource_config in model_configuration.resources.items():
        resources[resource_label] = configure_resource(event_queue, rm, resource_label, resource_config)

    ar_mapping = {activity_nodes[activity_label].model: {resources[resource_label] for resource_label in
                                                         assignable_resources} for activity_label, assignable_resources
                  in
                  model_configuration.mapping.assignable_resources.items()}
    ar_propensities = None
    if model_configuration.mapping.propensities is not None:
        ar_propensities = {activity_nodes[activity_label].model: {resources[resource_label]: p for resource_label, p in
                                                                  resource_propensities.items()} for
                           activity_label, resource_propensities in model_configuration.mapping.propensities.items()}
    arc = smanagers.ActivityResourceCorrespondence(ar_mapping, ar_propensities)

    rm.ar_correspondence = arc
    am.ar_correspondence = arc

    arrival_models = {arrival_label: arrival_node.model for arrival_label, arrival_node in arrival_nodes.items()}
    activity_datas = {activity_label: activity_node.model.data for activity_label, activity_node in
                      activity_nodes.items()}
    resource_datas = {resource_label: resource_model.data for resource_label, resource_model in resources.items()}

    scheduling_manager = SchedulingManager(event_queue,
                                           Schedulables(arrival_models, activity_datas, resource_datas),
                                           context, execution_parameters)

    for arrival_label, arrival_config in model_configuration.arrivals.items():
        scheduling_manager.add_arrival_process(arrival_label, arrival_config)
    for activity_label, activity_configuration in model_configuration.activities.items():
        scheduling_manager.set_activity_business_hours(activity_label, activity_configuration.business_hours)
    for resource_label, resource_config in model_configuration.resources.items():
        scheduling_manager.set_resource_business_hours(resource_label, resource_config.business_hours)

    return SimulationModel(graph=simulation_graph, event_queue=event_queue, scheduling_manager=scheduling_manager,
                           activity_manager=am, resource_manager=rm, simulation_context=context,
                           execution_parameters=execution_parameters)
