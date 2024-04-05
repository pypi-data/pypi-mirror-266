from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, TYPE_CHECKING, Optional

import numpy as np

from qprsim.config import parameter_implementations as pi
from qprsim.core import event_system as ev_sys, oc_managers, oc_schedulers, managers
from qprsim.model import oc_sim_graph as sgraph, conceptual_models as cm, \
    oc_graph_models as gm, oc_model_data as ocmd, model_data as mdata
from qprsim.model.oc_model_traits import WithEventManager, WithObjectManager
from qprsim.shared.base_classes import auto_str
from qprsim.shared.enums import OCExecutionParameters
from qprsim.utils import time_utils, utils

if TYPE_CHECKING:
    import qprsim.core.object_def as obd
    from qprsim.model.model_parameters import BusinessHours

    from qprsim.config.model_configuration import ResourceConfig, ModelHaverConfig
    from qprsim.config.oc_model_configuration import ObjectBirthplaceConfig, OCArrivalProcessConfig, OCActivityConfig, \
        OCModelConfiguration


def default_execution_parameters():
    execution_parameters = {OCExecutionParameters.EventsToGenerate: 1000,
                            OCExecutionParameters.GenerationCutoffDate: None,
                            OCExecutionParameters.SimStartDate: None,
                            OCExecutionParameters.SimCutoffDate: None,
                            OCExecutionParameters.RealtimeLimit: timedelta(seconds=30)}
    return execution_parameters


@auto_str
class OCSimulationContext(WithEventManager, WithObjectManager):

    def __init__(self, event_manager: oc_managers.EventManager, object_manager: oc_managers.ObjectManager):
        super().__init__(event_manager=event_manager, object_manager=object_manager)

    @property
    def generated_objects_count(self):
        return sum(self.object_manager.object_counts.values())

    @property
    def finalized_objects_count(self):
        return len(self.object_manager.retired_objects)

    @property
    def generated_events_count(self):
        return len(self.event_manager.collected_events)

    def are_active_cases_remaining(self):
        return len(self.object_manager.active_objects) > 0


@dataclass
class Schedulables:
    birthplaces: dict[str, gm.OCBirthplaceModel]
    activity_datas: dict[str, ocmd.OCActivityData]
    resource_datas: dict[str, mdata.ResourceData]


class SchedulingManager:

    def __init__(self, event_queue: ev_sys.EventQueue, schedulables: Schedulables,
                 simulation_context: OCSimulationContext,
                 execution_parameters: dict[OCExecutionParameters, Any]) -> None:
        self.event_queue: ev_sys.EventQueue = event_queue
        self.birthplaces = schedulables.birthplaces
        self.arrival_processes: dict[str, tuple[OCArrivalProcessConfig, oc_schedulers.OCArrivalProcessScheduler]] = {}
        self.activity_datas: dict[str, ocmd.OCActivityData] = schedulables.activity_datas
        self.resource_datas: dict[str, mdata.ResourceData] = schedulables.resource_datas
        self.simulation_context = simulation_context
        self.execution_parameters = execution_parameters

        self._client_scheduler_map: dict[ev_sys.Updatable, ev_sys.BusinessHoursScheduler] = {}
        self._bh_schedulers: dict[BusinessHours, ev_sys.BusinessHoursScheduler] = {}
        self._unstarted_schedulers: list[tuple[int, ev_sys.BusinessHoursScheduler]] = []

    def _schedule_business_hours(self, client: ev_sys.Updatable,
                                 business_hours: BusinessHours = pi.AlwaysInBusiness, priority: int = 1,
                                 when: datetime = None) -> ev_sys.BusinessHoursScheduler:
        if business_hours is None:
            business_hours = pi.AlwaysInBusiness
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

    def add_arrival_process(self, arrival_label: str, arrival_config: OCArrivalProcessConfig):
        limit = self.execution_parameters.get(OCExecutionParameters.ObjectsToGenerate, np.Inf)

        def external_termination_check():
            return self.simulation_context.generated_objects_count >= limit

        date_limit = None
        gen_stop_date = self.execution_parameters.get(OCExecutionParameters.GenerationCutoffDate, None)
        if gen_stop_date is not None:
            date_limit = time_utils.make_timezone_aware(gen_stop_date)
        if arrival_config.last_arrival is not None:
            last_arrival = time_utils.make_timezone_aware(arrival_config.last_arrival)
            if date_limit is not None:
                date_limit = min(last_arrival, date_limit)
            else:
                date_limit = last_arrival

        arrival_process = oc_schedulers.ScheduledOCArrivalProcessScheduler(self.event_queue,
                                                                           arrival_config.inter_arrivals,
                                                                           creation_count_limit=arrival_config.max_arrivals,
                                                                           date_limit=date_limit,
                                                                           label=arrival_label,
                                                                           external_termination_check=external_termination_check,
                                                                           strict=True)

        for target in arrival_config.targets:
            arrival_process.add_client(self.birthplaces[target])
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

    def set_activity_business_hours(self, activity: str, business_hours: BusinessHours):
        self._schedule_business_hours(self.activity_datas[activity], business_hours)

    def set_resource_business_hours(self, resource: str, business_hours: BusinessHours):
        self._schedule_business_hours(self.resource_datas[resource], business_hours)

    def start(self):
        self.start_schedulers()

    def perform_hot_change(self, change: Callable[..., None]):
        self.cleanup_schedulers()
        change()
        self.start_schedulers()


@dataclass(unsafe_hash=True)
class OCSimulationModel:
    graph: sgraph.OCSimulationGraph
    event_queue: ev_sys.EventQueue
    scheduling_manager: SchedulingManager
    activity_manager: managers.ActivityManager
    resource_manager: managers.ResourceManager
    simulation_context: OCSimulationContext
    execution_parameters: dict[OCExecutionParameters, Any]


class Simulator:
    time_check_interval = 10

    def __init__(self, simulation_model: OCSimulationModel) -> None:
        self.simulation_model = simulation_model
        self.scheduling_manager = simulation_model.scheduling_manager
        self.event_queue = simulation_model.event_queue
        self.exp = simulation_model.execution_parameters

        # self._collected_cases_iterable = (c for c in simulation_model.simulation_context.completed_cases)

        self.termination_checks = []

        self.dirty: bool = False
        self.simulation_start: Optional[datetime] = None
        self.simulation_end: Optional[datetime] = None
        self.iteration: int = 0

    def setup(self):
        self.dirty = True
        self.simulation_start = time_utils.now()
        self.iteration = 0

        self.termination_checks = [(lambda: self.event_queue.empty(), 'Terminated due to event queue being empty.')]

        if self.exp.get(OCExecutionParameters.EventsToGenerate) is not None:
            event_limit = self.exp[OCExecutionParameters.EventsToGenerate]

            def events_to_sim():
                return self.simulation_model.simulation_context.generated_events_count >= event_limit

            self.termination_checks.append((events_to_sim, 'Terminated due to EventsToGenerate being reached.'))

        if self.exp.get(OCExecutionParameters.ObjectToBeFinalized) is not None:
            object_limit = self.exp[OCExecutionParameters.ObjectToBeFinalized]

            def objects_to_sim():
                return self.simulation_model.simulation_context.finalized_objects_count >= object_limit

            self.termination_checks.append((objects_to_sim, 'Terminated due to ObjectToBeFinalized being reached.'))

        if self.exp.get(OCExecutionParameters.SimCutoffDate) is not None:
            sim_limit = time_utils.make_timezone_aware(self.exp[OCExecutionParameters.SimCutoffDate])

            def sim_cutoff_date():
                return self.event_queue.global_time > sim_limit

            self.termination_checks.append(
                (sim_cutoff_date, 'Terminated due to simulation stopping date being reached.'))

        if self.exp.get(OCExecutionParameters.RealtimeLimit) is not None:
            rl_limit = time_utils.add(self.simulation_start, self.exp[OCExecutionParameters.RealtimeLimit])

            def realtime_cutoff_date():
                return self.iteration % self.time_check_interval == 0 and rl_limit < time_utils.now()

            self.termination_checks.append(
                (realtime_cutoff_date, 'Terminated due to execution time limit being reached.'))

        if self.exp.get(OCExecutionParameters.GenerationCutoffDate) is not None:
            cutoff_date = time_utils.make_timezone_aware(self.exp[OCExecutionParameters.GenerationCutoffDate])

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
    def logged_events(self) -> list[obd.ObjectEvent]:
        return self.simulation_model.simulation_context.event_manager.collected_events

    @property
    def finalized_objects(self) -> set[obd.Object]:
        return self.simulation_model.simulation_context.object_manager.retired_objects

    @property
    def all_objects(self) -> set[obd.Object]:
        return self.simulation_model.simulation_context.object_manager.object_map.objects

    @property
    def duration(self) -> timedelta:
        return self.simulation_end - self.simulation_start

    def create_log(self, only_finalized_objects=False):
        from qprsim.utils import ocel_exporting
        return ocel_exporting.export(self.simulation_model.simulation_context, only_finalized_objects=only_finalized_objects)


def simulate(configured_simulation_model: OCSimulationModel, create_log_file=True,
             simulation_log_filename=None) -> Simulator:
    simulator = Simulator(configured_simulation_model)
    if create_log_file and simulation_log_filename is None:
        simulation_log_filename = f'{time_utils.filenameable_timestamp()}.log'
    simulator.run(simulation_log_filename=simulation_log_filename)
    return simulator


def configure_activity(event_queue: ev_sys.EventQueue, activity_manager: managers.ActivityManager,
                       event_manager: oc_managers.EventManager,
                       activity_node: sgraph.ActivityNode, activity_configuration: OCActivityConfig):
    a_model = gm.OCActivityModel(node=activity_node, event_queue=event_queue, activity_manager=activity_manager,
                                 event_manager=event_manager)
    a_data = ocmd.OCActivityData(a_model)
    a_data.properties.update(activity_configuration.property_dict)
    # assert sim.enums.ActivityProperty.vals <= a_data.properties.keys()  # make sure everything is configured
    a_model.data = a_data
    activity_node.model = a_model
    return a_model


def configure_birthplace(birthplace_node: sgraph.BirthplaceNode, birthplace_config: ObjectBirthplaceConfig,
                         simulation_context: OCSimulationContext, object_manager: oc_managers.ObjectManager):
    b_model = gm.OCBirthplaceModel(node=birthplace_node, simulation_context=simulation_context,
                                   object_manager=object_manager)
    b_data = ocmd.OCObjectBirthplaceData()
    b_data.properties.update(birthplace_config.property_dict)
    b_model.data = b_data
    birthplace_node.model = b_model
    return b_model


def configure_resource(event_queue: ev_sys.EventQueue, rm: managers.ResourceManager, resource_label: str,
                       resource_config: ResourceConfig):
    resource = cm.ResourceModel(resource_label, event_queue=event_queue, resource_manager=rm)
    r_data = mdata.ResourceData(resource)
    r_data.properties.update(resource_config.property_dict)
    # assert sim.enums.ResourceProperty.vals <= r_data.properties.keys()  # make sure everything is configured
    resource.data = r_data
    return resource


def configure_aux(node: sgraph.WithModel, cfg: ModelHaverConfig, **kwargs):
    model = cfg.instantiate_model(node=node, **kwargs)
    node.model = model
    return model


def create_simulation_model(simulation_graph: sgraph.OCSimulationGraph,
                            model_configuration: OCModelConfiguration,
                            execution_parameters: dict[OCExecutionParameters, Any] = None) -> OCSimulationModel:
    assert simulation_graph.activity_map.keys() <= model_configuration.activities.keys()
    if execution_parameters is None:
        execution_parameters = default_execution_parameters()

    ev_manager = oc_managers.EventManager()
    obj_manager = oc_managers.ObjectManager()
    context = OCSimulationContext(event_manager=ev_manager, object_manager=obj_manager)

    event_queue = ev_sys.EventQueue()
    earliest = min(ac.first_arrival for ac in model_configuration.processes.values())
    earliest = time_utils.make_timezone_aware(earliest)
    start_datetime_override = execution_parameters.get(OCExecutionParameters.SimStartDate)
    if start_datetime_override is not None:
        earliest = max(earliest, time_utils.make_timezone_aware(start_datetime_override))
    event_queue.global_time = earliest

    rm = managers.ResourceManager(event_queue)
    am = managers.ActivityManager(event_queue)
    am.resource_manager = rm
    rm.activity_manager = am

    birthplace_nodes = simulation_graph.birthplaces
    for birthplace_label, node in birthplace_nodes.items():
        configure_birthplace(node, model_configuration.birthplaces[birthplace_label], simulation_context=context,
                             object_manager=obj_manager)
    for graveyard_label, node in simulation_graph.graveyards.items():
        node.model = gm.OCGraveyardModel(node=node, label=graveyard_label, simulation_context=context,
                                         object_manager=obj_manager)

    for label, node in simulation_graph.aux_model_haver_map.items():
        cfg = model_configuration.aux_model_configs[label]
        if cfg.requires_unsafe_access:
            configure_aux(node, cfg, event_queue=event_queue, activitiy_manager=am,
                          resource_manager=rm, simulation_context=context, object_manager=obj_manager,
                          event_manager=ev_manager)
        else:
            configure_aux(node, cfg)

    activity_nodes = simulation_graph.activity_map
    for activity_label, node in activity_nodes.items():
        configure_activity(event_queue, am, ev_manager, node,
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
    arc = managers.ActivityResourceCorrespondence(ar_mapping, ar_propensities)

    rm.ar_correspondence = arc
    am.ar_correspondence = arc

    birthplace_models = {birthplace_label: birthplace_node.model for birthplace_label, birthplace_node in
                         birthplace_nodes.items()}
    activity_datas = {activity_label: activity_node.model.data for activity_label, activity_node in
                      activity_nodes.items()}
    resource_datas = {resource_label: resource_model.data for resource_label, resource_model in resources.items()}

    scheduling_manager = SchedulingManager(event_queue,
                                           Schedulables(birthplace_models, activity_datas, resource_datas),
                                           context, execution_parameters)

    for arrival_label, arrival_config in model_configuration.processes.items():
        scheduling_manager.add_arrival_process(arrival_label, arrival_config)
    for activity_label, activity_configuration in model_configuration.activities.items():
        scheduling_manager.set_activity_business_hours(activity_label, activity_configuration.business_hours)
    for resource_label, resource_config in model_configuration.resources.items():
        scheduling_manager.set_resource_business_hours(resource_label, resource_config.business_hours)

    return OCSimulationModel(graph=simulation_graph, event_queue=event_queue, scheduling_manager=scheduling_manager,
                             activity_manager=am, resource_manager=rm, simulation_context=context,
                             execution_parameters=execution_parameters)
