"""Jsonschema types."""
# pylint: disable=C0103

from dataclasses import dataclass
from functools import partial
from typing import (Any, Collection, Dict, List, Literal, Mapping, Protocol,
                    TypeVar)

__all__ = (
    "JSONSchemaObject",
    "JSONSchemaType",
    "Boolean",
    "String",
    "Number",
    "Integer",
    "Array",
    "Object",
    "AnyOf",
    "OneOf",
    "AllOf",
    "Not",
    "GUID",
    "Date",
    "DateTime",
    "Null",
    "Const",
    "Nullable",
    "Enum",
)

_T = TypeVar("_T")
_StringFormat = Literal[
    "JSONSchemaType",
    "date-time",
    "time",
    "date",
    "email",
    "idn-email",
    "hostname",
    "idn-hostname",
    "ipv4",
    "ipv6",
    "uri",
    "uri-reference",
    "iri",
    "iri-reference",
    "regex",
]


class JSONSchemaType(Protocol):
    """Json schema object interface."""

    def get_jsonschema(self) -> Dict[str, Any]: ...


def _serialize_schema_value(value: Any, /) -> Any:
    if isinstance(value, Mapping):
        return _serialize_schema_keys(value)
    if isinstance(value, (list, tuple)):
        return [_serialize_schema_value(sub_value) for sub_value in value]
    if hasattr(value, "get_jsonschema"):
        return value.get_jsonschema()
    return value


def _serialize_schema_keys(obj: Mapping) -> Dict[str, Any]:
    return {
        key: _serialize_schema_value(value)
        for key, value in obj.items()
        if not key.startswith("_") and value is not None and value is not ...
    }


@dataclass
class JSONSchemaObject:
    """Generic schema object."""

    title: str = None
    description: str = None
    examples: List = None
    default: Any = ...

    def get_jsonschema(self) -> Dict[str, Any]:
        return _serialize_schema_keys(vars(self))


@dataclass
class Enum:
    """Enum value alias."""

    enum: List
    title: str = None
    description: str = None
    examples: List = None
    default: Any = ...

    def get_jsonschema(self) -> Dict[str, Any]:
        return _serialize_schema_keys(vars(self))


@dataclass
class Const:
    """Constant value.

    See `constants <https://json-schema.org/understanding-json-schema/reference/const#constant-values>`_

    """
    const: Any
    title: str = None
    description: str = None

    def get_jsonschema(self) -> Dict[str, Any]:
        return _serialize_schema_keys(vars(self))


@dataclass
class Boolean:
    """Boolean type.

    See `boolean type <https://json-schema.org/understanding-json-schema/reference/boolean>`_
    """

    title: str = None
    description: str = None
    default: bool = ...

    def get_jsonschema(self) -> Dict[str, Any]:
        data = _serialize_schema_keys(vars(self))
        data["type"] = "boolean"
        return data


@dataclass
class String:
    """String type.

    See `string type <https://json-schema.org/understanding-json-schema/reference/string>`_
    """

    minLength: int = None
    maxLength: int = None
    pattern: str = None  #: regex validation pattern
    format: _StringFormat = None  #: string format
    title: str = None
    description: str = None
    examples: List = None
    enum: List[str] = None
    default: str = ...

    def get_jsonschema(self) -> Dict[str, Any]:
        data = _serialize_schema_keys(vars(self))
        data["type"] = "string"
        return data


DateTime = partial(String, format="date-time")
Date = partial(String, format="date")
GUID = partial(String, format="uuid")
Null = partial(Enum, enum=[None])


@dataclass
class Number:
    """Numeric data type.

    See `numeric type <https://json-schema.org/understanding-json-schema/reference/numeric#number>`_
    """

    multipleOf: float = None
    minimum: float = None
    maximum: float = None
    exclusiveMinimum: float = None
    exclusiveMaximum: float = None
    title: str = None
    description: str = None
    examples: List = None
    enum: List[float] = None
    default: float = ...

    def get_jsonschema(self) -> Dict[str, Any]:
        data = _serialize_schema_keys(vars(self))
        data["type"] = "number"
        return data


@dataclass
class Integer:
    """Integer type.

    See `integer type <https://json-schema.org/understanding-json-schema/reference/numeric#integer>`_
    """

    multipleOf: int = None
    minimum: int = None
    maximum: int = None
    exclusiveMinimum: int = None
    exclusiveMaximum: int = None
    title: str = None
    description: str = None
    examples: List = None
    enum: List[int] = None
    default: int = ...

    def get_jsonschema(self) -> Dict[str, Any]:
        data = _serialize_schema_keys(vars(self))
        data["type"] = "integer"
        return data


@dataclass
class Array:
    """Array type.

    See `array type <https://json-schema.org/understanding-json-schema/reference/array>`_
    """

    items: JSONSchemaType = None  #: item type for a strict typed array
    prefixItems: Collection[JSONSchemaType] = None  #: a List of fixed object positions for a tuple type
    contains: JSONSchemaType = None  #: must contain this type of object
    additionalItems: bool = None  #: allow additional items
    uniqueItems: bool = None  #: specify an array as a set type
    minItems: int = None
    maxItems: int = None
    title: str = None
    description: str = None
    examples: List = None
    enum: List[List] = None
    default: List = ...

    def get_jsonschema(self) -> Dict[str, Any]:
        data = _serialize_schema_keys(vars(self))
        data["type"] = "array"
        return data


@dataclass
class Object:
    """Object type (Dictionary).

    See `object type <https://json-schema.org/understanding-json-schema/reference/object>`_
    """

    properties: Dict[str, JSONSchemaType] = None
    patternProperties: Dict[str, JSONSchemaType] = None
    additionalProperties: bool = None
    minProperties: int = None
    maxProperties: int = None
    required: List[str] = None
    title: str = None
    description: str = None
    examples: List = None
    enum: List[Dict] = None
    default: Dict = ...

    def get_jsonschema(self) -> Dict[str, Any]:
        data = _serialize_schema_keys(vars(self))
        data["type"] = "object"
        return data


@dataclass
class AnyOf:
    """Any of the included schemas must be valid.

    See `anyOf keyword <https://json-schema.org/understanding-json-schema/reference/combining#anyOf>`_
    """

    items: Collection[JSONSchemaType]

    def get_jsonschema(self) -> Dict[str, Any]:
        return {"anyOf": [item.get_jsonschema() for item in self.items]}


@dataclass
class OneOf:
    """Only one of the included schemas must be valid.

    See `oneOf keyword <https://json-schema.org/understanding-json-schema/reference/combining#oneOf>`_
    """

    items: Collection[JSONSchemaType]

    def get_jsonschema(self) -> Dict[str, Any]:
        return {"oneOf": [item.get_jsonschema() for item in self.items]}


@dataclass
class AllOf:
    """All the included schemas must be valid.

    See `allOf keyword <https://json-schema.org/understanding-json-schema/reference/combining#allOf>`_
    """

    items: Collection[JSONSchemaType]

    def get_jsonschema(self) -> Dict[str, Any]:
        return {"allOf": [item.get_jsonschema() for item in self.items]}


@dataclass
class Not:
    """Revert the condition of the schema.

    See `Not keyword <https://json-schema.org/understanding-json-schema/reference/combining#allOf>`_
    """

    item: JSONSchemaType

    def get_jsonschema(self) -> Dict[str, Any]:
        return {"not": self.item.get_jsonschema()}


@dataclass
class Nullable:
    """Nullable value alias."""

    item: JSONSchemaType

    def get_jsonschema(self) -> Dict[str, Any]:
        return {"oneOf": [self.item.get_jsonschema(), Null()]}
