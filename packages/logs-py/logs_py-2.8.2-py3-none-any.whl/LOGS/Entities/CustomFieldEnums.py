from enum import Enum


class CustomFieldTypes(Enum):
    Text = "Text"
    TextArea = "TextArea"
    Number = "Number"
    EnumDropdown = "EnumDropdown"
    Date = "Date"
    Toggle = "Toggle"


class CustomFieldDataTypes(Enum):
    String = "String"
    Date = "Date"
    Number = "Number"
    Boolean = "Boolean"
    DateTime = "DateTime"


class CustomFieldPropertyFilters(Enum):
    DefaultValue = "DefaultValue"
    IsReadOnly = "IsReadOnly"
    IsRequired = "IsRequired"
    ValidationRegexp = "ValidationRegexp"
