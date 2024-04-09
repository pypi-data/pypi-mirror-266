from LOGS.Auxiliary.Decorators import Endpoint
from LOGS.Entities.SampleType import SampleType
from LOGS.Entities.SampleTypeRequestParameter import SampleTypeRequestParameter
from LOGS.Entity.EntityIterator import EntityIterator


@Endpoint("sample_types")
class SampleTypes(EntityIterator[SampleType, SampleTypeRequestParameter]):
    """LOGS connected SampleTypes iterator"""

    _generatorType = SampleType
    _parameterType = SampleTypeRequestParameter
