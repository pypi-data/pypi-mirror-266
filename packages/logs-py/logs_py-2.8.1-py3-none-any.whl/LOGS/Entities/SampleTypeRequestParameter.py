from dataclasses import dataclass

from LOGS.Entities.CustomSchemaParameter import CustomSchemaOrder, CustomSchemaParameter


@dataclass
class SampleTypeRequestParameter(CustomSchemaParameter[CustomSchemaOrder]):
    pass
