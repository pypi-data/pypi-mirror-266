from ..oc_model_configuration import MappingConfig, ResourceConfig, CarrierGeneratorConfig, OCActivityConfig, DecisionConfig, SplitConfig, ObjectBirthplaceConfig, OCArrivalProcessConfig, OCModelConfiguration
from .. import parameter_implementations as pi
from .. import oc_parameter_implementations as ocpi
from ..oc_modeling import GraphBuilder, ModelBuilder, split_of, join_of
from ..oc_model_configuration import OCActivityProperty, OCObjectBirthplaceProperty
from qprsim.shared.enums import ResourceProperty
from qprsim.core import object_def as obd
from qprsim.core.oc_events import attribute_initialization_event