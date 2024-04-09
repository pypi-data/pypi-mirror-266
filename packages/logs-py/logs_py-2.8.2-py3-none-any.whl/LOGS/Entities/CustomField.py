from datetime import datetime
from typing import List, Optional

from regex import Regex

from LOGS.Auxiliary.Decorators import Endpoint
from LOGS.Entities.CustomFieldEnums import CustomFieldDataTypes, CustomFieldTypes
from LOGS.Entity.EntityWithStrId import EntityWithStrId
from LOGS.Interfaces.INamedEntity import INamedEntity
from LOGS.Interfaces.IOwnedEntity import IOwnedEntity
from LOGS.LOGSConnection import LOGSConnection


@Endpoint("custom_fields")
class CustomField(
    EntityWithStrId,
    IOwnedEntity,
    INamedEntity,
):
    _createdAt: Optional[datetime]
    _widget: Optional[CustomFieldTypes] = CustomFieldTypes.Text
    _type: Optional[CustomFieldDataTypes] = CustomFieldDataTypes.String
    _description: Optional[str]
    _defaultValue: Optional[str]
    _isReadOnly: Optional[bool]
    _isRequired: Optional[bool]
    _isMulti: Optional[bool]
    _validationRegexp: Optional[str]
    _validationMessage: Optional[str]
    _enumOptions: Optional[List[str]]

    _alphanumeric = Regex(r"[^a-zA-Z0-9_]")

    def __init__(
        self,
        ref=None,
        id: Optional[str] = None,
        connection: Optional[LOGSConnection] = None,
        name: str = "",
    ):
        self._name = name
        if id is None:
            id = self._idFromName(name)
        self._createdAt = None
        self._widget = None
        self._type = None
        self._description = None
        self._defaultValue = None
        self._isReadOnly = None
        self._isRequired = None
        self._isMulti = None
        self._validationRegexp = None
        self._validationMessage = None
        self._enumOptions = None

        if ref != None and isinstance(ref, (str, int, float)):
            ref = {"text": str(ref)}

        super().__init__(connection=connection, id=id, ref=ref)

    def fromDict(self, ref, formatDict=None) -> None:
        if isinstance(ref, dict) and "type" in ref and isinstance(ref["type"], int):
            del ref["type"]
        if isinstance(ref, dict) and "widget" in ref and isinstance(ref["widget"], int):
            del ref["widget"]

        super().fromDict(ref=ref, formatDict=formatDict)

    @classmethod
    def _idFromName(cls, name):
        return cls._alphanumeric.sub("_", name).lower()

    @property
    def createdAt(self) -> Optional[datetime]:
        return self._createdAt

    @createdAt.setter
    def createdAt(self, value):
        self._createdAt = self.checkAndConvertNullable(value, datetime, "createdAt")

    @property
    def widget(self) -> Optional[CustomFieldTypes]:
        return self._widget

    @widget.setter
    def widget(self, value):
        self._widget = self.checkAndConvertNullable(value, CustomFieldTypes, "widget")

    @property
    def type(self) -> Optional[CustomFieldDataTypes]:
        return self._type

    @type.setter
    def type(self, value):
        self._type = self.checkAndConvertNullable(value, CustomFieldDataTypes, "type")

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value):
        self._description = self.checkAndConvertNullable(value, str, "description")

    @property
    def defaultValue(self) -> Optional[str]:
        return self._defaultValue

    @defaultValue.setter
    def defaultValue(self, value):
        self._defaultValue = self.checkAndConvertNullable(value, str, "defaultValue")

    @property
    def isReadOnly(self) -> Optional[bool]:
        return self._isReadOnly

    @isReadOnly.setter
    def isReadOnly(self, value):
        self._isReadOnly = self.checkAndConvertNullable(value, bool, "isReadOnly")

    @property
    def isRequired(self) -> Optional[bool]:
        return self._isRequired

    @isRequired.setter
    def isRequired(self, value):
        self._isRequired = self.checkAndConvertNullable(value, bool, "isRequired")

    @property
    def isMulti(self) -> Optional[bool]:
        return self._isMulti

    @isMulti.setter
    def isMulti(self, value):
        self._isMulti = self.checkAndConvertNullable(value, bool, "isMulti")

    @property
    def validationRegexp(self) -> Optional[str]:
        return self._validationRegexp

    @validationRegexp.setter
    def validationRegexp(self, value):
        self._validationRegexp = self.checkAndConvertNullable(
            value, str, "validationRegexp"
        )

    @property
    def validationMessage(self) -> Optional[str]:
        return self._validationMessage

    @validationMessage.setter
    def validationMessage(self, value):
        self._validationMessage = self.checkAndConvertNullable(
            value, str, "validationMessage"
        )

    @property
    def enumOptions(self) -> Optional[List[str]]:
        return self._enumOptions

    @enumOptions.setter
    def enumOptions(self, value):
        self._enumOptions = self.checkListAndConvertNullable(value, str, "enumOptions")

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value):
        self._name = self.checkAndConvert(value, str, "name", allowNone=True)
        if self.id is None or self.id == "":
            self.id = self._idFromName(self._name)
