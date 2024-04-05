import pandas as pd
from pm4py.objects.ocel import constants
from pm4py.objects.ocel.obj import OCEL

from qprsim.core.object_def import Object
from qprsim.execution.oc_simulation import OCSimulationContext


def export(simulation_context: OCSimulationContext, only_finalized_objects=False) -> OCEL:
    event_list = []
    e2o_relations_list = []
    event_attributes = set()
    collected_events = simulation_context.event_manager.collected_events
    for e in collected_events:
        # pd.DataFrame({self.event_id_column: [], self.event_activity: [], self.event_timestamp: []})
        event_list.append([e.event_id, e.activity_type, e.time])
        for a in e.attributes.keys():
            event_attributes.add(a)
        # relations = pd.DataFrame(
        #    {self.event_id_column: [], self.event_activity: [], self.event_timestamp: [], self.object_id_column: [],
        #     self.object_type_column: []})
        for qualifier, os in e.objects.items():
            os: set[Object]
            for o in os:
                e2o_relations_list.append([e.event_id, e.activity_type, e.time, qualifier, o.object_id, o.object_type])

    object_list = []
    changes_list = []
    object_attributes = set()
    # TODO in case of finalized_only, the events can still refer to non-included objects - they should be filtered
    objects_to_export = simulation_context.object_manager.retired_objects if only_finalized_objects else simulation_context.object_manager.object_map.objects
    for o in objects_to_export:
        # objects = pd.DataFrame({self.object_id_column: [], self.object_type_column: []})
        object_list.append([o.object_id, o.object_type])
        for a in o.attributes:
            object_attributes.add(a)
        for ae in o.attribute_events:
            time = ae.time
            for k, v in ae.new_values.items():
                # object_changes = pd.DataFrame(
                #    {self.object_id_column: [], self.object_type_column: [], self.event_timestamp: [],
                #     self.changed_field: []})
                changes_list.append([o.object_id, o.object_type, time, k, v])

    o2o_list = []
    for qualifier, os in simulation_context.object_manager.object_map.qualified_o2o.items():
        # o2o = pd.DataFrame({self.object_id_column: [], self.object_id_column + "_2": [], self.qualifier: []})
        for o_1, o_2 in os:
            o2o_list.append([o_1.object_id, o_2.object_id, qualifier])

    events = pd.DataFrame(event_list, columns=[constants.DEFAULT_EVENT_ID, constants.DEFAULT_EVENT_ACTIVITY,
                                               constants.DEFAULT_EVENT_TIMESTAMP])
    relations = pd.DataFrame(e2o_relations_list, columns=[constants.DEFAULT_EVENT_ID, constants.DEFAULT_EVENT_ACTIVITY,
                                                          constants.DEFAULT_EVENT_TIMESTAMP,
                                                          constants.DEFAULT_QUALIFIER, constants.DEFAULT_OBJECT_ID,
                                                          constants.DEFAULT_OBJECT_TYPE])
    objects = pd.DataFrame(object_list, columns=[constants.DEFAULT_OBJECT_ID, constants.DEFAULT_OBJECT_TYPE])
    o2o = pd.DataFrame(o2o_list, columns=[constants.DEFAULT_OBJECT_ID, constants.DEFAULT_OBJECT_ID + "_2",
                                          constants.DEFAULT_QUALIFIER])
    changes = pd.DataFrame(changes_list, columns=[constants.DEFAULT_OBJECT_ID, constants.DEFAULT_OBJECT_TYPE,
                                                  constants.DEFAULT_EVENT_TIMESTAMP, constants.DEFAULT_CHNGD_FIELD,
                                                  'new_value'])

    events = events.assign(**{a: None for a in event_attributes}).set_index(constants.DEFAULT_EVENT_ID, drop=False)
    objects = objects.assign(**{a: None for a in object_attributes}).set_index(constants.DEFAULT_OBJECT_ID, drop=False)

    # this is adversarially slow code
    for e in collected_events:
        for a, v in e.attributes.items():
            events.loc[e.event_id, a] = v

    for o in objects_to_export:
        for a, v in o.attributes.items():
            objects.loc[o.object_id, a] = v

    return OCEL(events, objects, relations, o2o=o2o, object_changes=changes)
