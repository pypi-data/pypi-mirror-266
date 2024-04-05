from typing import Optional

from LOGS.Auxiliary.Decorators import Endpoint
from LOGS.Entities.CustomSchema import CustomSchema
from LOGS.Entity.SerializeableContent import SerializeableClass
from LOGS.LOGSConnection import LOGSConnection


class SampleTypeStats(SerializeableClass):
    samples: Optional[int] = None


@Endpoint("sample_types")
class SampleType(CustomSchema):
    _stats: Optional[SampleTypeStats]

    def __init__(
        self,
        ref=None,
        id: Optional[str] = None,
        connection: Optional[LOGSConnection] = None,
        name: str = "",
    ):
        self._stats = None

        super().__init__(ref, id, connection, name)

    @property
    def stats(self) -> Optional[SampleTypeStats]:
        return self._stats

    @stats.setter
    def stats(self, value):
        self._stats = self.checkAndConvertNullable(value, SampleTypeStats, "stats")
