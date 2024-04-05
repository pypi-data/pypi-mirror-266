from enum import Enum, IntEnum
from typing import TypeVar


class ValueSetEnum(Enum):
    vals: set

    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = value
        if not hasattr(cls, 'vals'):
            cls.vals = set()
        cls.vals.add(value)
        return obj

    @classmethod
    def cast(cls, value):
        if isinstance(value, cls):
            return value
        elif value in cls.vals:
            return cls(value)

    @classmethod
    def can_cast(cls, value):
        return isinstance(value, cls) or value in cls.vals

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.value == o.value


class PropertyEnum(ValueSetEnum):
    pass


class StateEnum(ValueSetEnum):
    pass


class ActivityProperty(PropertyEnum):
    QueueingDiscipline = 'queueing_discipline'
    ProcessingTimeSampler = 'processing_time_sampler'
    DelaySampler = 'delay_sampler'
    EventAttributeGenerator = 'event_attribute_generator'
    MaxQueueLength = 'max_queue_length'
    DiscardIfNotInBusiness = 'discard_if_not_in_business'
    ExternalDiscardingHandler = 'external_discarding_handler'
    ExternalProcessingHandler = 'external_processing_handler'


class OCActivityProperty(PropertyEnum):
    QueueingDiscipline = 'queueing_discipline'
    ProcessingTimeSampler = 'processing_time_sampler'
    ObjectQualifier = 'event_object_qualifier'
    EventAttributeGenerator = 'event_attribute_generator'
    CarrierAttributeGenerator = 'carrier_attribute_generator'
    EventType = 'event_type'


class ActivityState(StateEnum):
    InBusiness = 'in_business'
    QueueLength = 'queue_length'


class ResourceProperty(PropertyEnum):
    Capacity = 'capacity'
    Performance = 'performance'
    Cooldown = 'cooldown'


class ResourceState(StateEnum):
    InBusiness = 'in_business'
    CurrentlyAssigned = 'currently_assigned'
    OnCooldown = 'on_cooldown'
    Disabled = 'disabled'


class OCObjectBirthplaceProperty(PropertyEnum):
    ObjectType = 'object_type'
    ObjectCreator = 'object_creator'
    CreationLimit = 'creation_limit'

class OCObjectBirthplaceState(StateEnum):
    CreationCount = 'creation_count'


PropertyEnumType = TypeVar('PropertyEnumType', bound=PropertyEnum)
StateEnumType = TypeVar('StateEnumType', bound=StateEnum)


class Lifecycle(ValueSetEnum):
    Enabled = 'enabled'
    Scheduled = 'scheduled'
    Started = 'started'
    Completed = 'completed'


class AvailableLifecycles(Enum):
    CompleteOnly = {'complete'}
    StartComplete = {'start', 'complete'}
    ScheduleStartComplete = {'schedule', 'start', 'complete'}

    def __new__(cls, *args, **kwargs):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, included_lifecycles):
        self.vals = included_lifecycles

    def __eq__(self, o: object) -> bool:
        return isinstance(o, self.__class__) and self.value == o.value


class ExecutionParameters(Enum):
    CasesToGenerate = 'cases'
    GenerationCutoffDate = 'creation_cutoff'
    CasesToSim = 'sim_cases'
    SimStartDate = 'sim_start'
    SimCutoffDate = 'sim_cutoff'
    RealtimeLimit = 'realtime_limit'


class OCExecutionParameters(Enum):
    ObjectsToGenerate = 'objects'
    EventsToGenerate = 'events'
    ObjectToBeFinalized = 'finalized_objects'
    GenerationCutoffDate = 'creation_cutoff'
    SimStartDate = 'sim_start'
    SimCutoffDate = 'sim_cutoff'
    RealtimeLimit = 'realtime_limit'


class Weekdays(IntEnum):
    Monday = 0
    Tuesday = 1
    Wednesday = 2
    Thursday = 3
    Friday = 4
    Saturday = 5
    Sunday = 6
