from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

from LOGS.Entities.CustomFieldEnums import CustomFieldPropertyFilters, CustomFieldTypes
from LOGS.Entity.EntityRequestParameter import EntityRequestParameter
from LOGS.Interfaces.INamedEntity import INamedEntityRequest
from LOGS.Interfaces.IOwnedEntity import IOwnedEntityRequest
from LOGS.Interfaces.IPaginationRequest import IPaginationRequest


class CustomFieldOrder(Enum):
    ID_ASC = "ID_ASC"
    ID_DESC = "ID_DESC"
    NAME_ASC = "NAME_ASC"
    NAME_DESC = "NAME_DESC"
    TYPE_ASC = "TYPE_ASC"
    TYPE_DESC = "TYPE_DESC"
    WIDGET_ASC = "WIDGET_ASC"
    WIDGET_DESC = "WIDGET_DESC"
    OWNER_ASC = "OWNER_ASC"
    OWNER_DESC = "OWNER_DESC"
    CREATED_ON_ASC = "CREATED_ON_ASC"
    CREATED_ON_DESC = "CREATED_ON_DESC"


@dataclass
class CustomFieldRequestParameter(
    EntityRequestParameter[CustomFieldOrder],
    IPaginationRequest,
    IOwnedEntityRequest,
    INamedEntityRequest,
):
    name: Optional[str] = None
    ownerIds: Optional[List[int]] = None
    creationDateFrom: Optional[datetime] = None
    creationDateTo: Optional[datetime] = None
    widgets: Optional[List[CustomFieldTypes]] = None
    properties: Optional[List[CustomFieldPropertyFilters]] = None
