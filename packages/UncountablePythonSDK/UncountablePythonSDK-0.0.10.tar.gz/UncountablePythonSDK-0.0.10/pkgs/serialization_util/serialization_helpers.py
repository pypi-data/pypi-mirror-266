import datetime
import enum
from decimal import Decimal
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Mapping,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from pkgs.argument_parser import camel_to_snake_case, snake_to_camel_case
from pkgs.serialization import (
    MISSING_SENTRY,
    MissingSentryType,
    MissingType,
    OpaqueKey,
    get_serial_class_data,
)

from ._get_type_for_serialization import SerializationType, get_serialization_type

# Inlined types which otherwise would import from types/base.py
JsonScalar = Union[str, float, bool, Decimal, None, datetime.datetime, datetime.date]
if TYPE_CHECKING:
    JsonValue = Union[JsonScalar, Mapping[str, "JsonValue"], Sequence["JsonValue"]]
else:
    JsonValue = Union[JsonScalar, dict[str, Any], list[Any]]


def key_convert_to_camelcase(o: Any) -> Any:
    if isinstance(o, OpaqueKey):
        return o
    if isinstance(o, enum.Enum):
        return o.value
    if isinstance(o, str):
        return snake_to_camel_case(o)
    return o


def _convert_dict(d: Any) -> Any:
    return {
        key_convert_to_camelcase(k): convert_to_camelcase(v)
        for k, v in d.items()
        if v != MISSING_SENTRY
    }


def _serialize_dict(d: Any) -> dict[str, Any]:
    return {k: serialize(v) for k, v in d.items() if v != MISSING_SENTRY}


def _convert_dataclass(d: Any) -> Any:
    dct = type(d)
    scd = get_serial_class_data(dct)

    def key_convert(key: Any) -> Any:
        if scd.has_unconverted_key(key):
            return key
        return key_convert_to_camelcase(key)

    def value_convert(key: Any, value: Any) -> Any:
        if value is None:
            return None
        if scd.has_to_string_value(key):
            # Limit to types we know we need to support to avoid surprises
            # Generics, like List/Dict would need to be per-value stringified
            assert isinstance(value, (Decimal, int))
            return str(value)
        if scd.has_unconverted_value(key):
            return value
        return convert_to_camelcase(value)

    return {
        key_convert(k): value_convert(k, v)
        for k, v in d.__dict__.items()
        if v != MISSING_SENTRY
    }


_SERIALIZATION_FUNCS_STANDARD = {
    SerializationType.ENUM: lambda x: str(x.value),
    SerializationType.DATE: lambda x: x.isoformat(),
    SerializationType.TIMEDELTA: lambda x: x.total_seconds(),
    SerializationType.UNKNOWN: lambda x: x,
}

_CONVERSION_SERIALIZATION_FUNCS = {
    **_SERIALIZATION_FUNCS_STANDARD,
    SerializationType.NAMED_TUPLE: lambda x: _convert_dict(x._asdict()),
    SerializationType.ITERABLE: lambda x: [convert_to_camelcase(v) for v in x],
    SerializationType.DICT: _convert_dict,
    SerializationType.DATACLASS: _convert_dataclass,
}


def convert_to_camelcase(obj: Any) -> Any:
    """@DEPRECATED prefer serialize_for_api"""
    return serialize_for_api(obj)


def serialize_for_api(obj: Any) -> Any:
    """
    Serialize to a parsed-JSON format suitably encoded for API output.

    Use the CachedParser.parse_api to parse this data.
    """
    serialization_type = get_serialization_type(type(obj))  # type: ignore
    return _CONVERSION_SERIALIZATION_FUNCS[serialization_type](obj)


_SERIALIZATION_FUNCS_DICT: dict[
    SerializationType, Callable[[Any], dict[str, JsonValue]]
] = {
    SerializationType.DICT: _serialize_dict,
    SerializationType.DATACLASS: lambda x: _serialize_dict(x.__dict__),
}


_SERIALIZATION_FUNCS: dict[SerializationType, Callable[[Any], JsonValue]] = {
    **_SERIALIZATION_FUNCS_STANDARD,
    **_SERIALIZATION_FUNCS_DICT,
    SerializationType.NAMED_TUPLE: lambda x: _serialize_dict(x._asdict()),
    SerializationType.ITERABLE: lambda x: [serialize(v) for v in x],
}


def serialize(obj: Any) -> Any:
    """@DEPRECATED: prefer serialize_for_storage"""
    return serialize_for_storage(obj)


def serialize_for_storage(obj: Any) -> JsonValue:
    """
    Convert a value into the pseudo-JSON form for
    storage in the DB, file, or other non-API use.

    Use the CachedParser.parse_storage to parse this data.
    """
    serialization_type = get_serialization_type(type(obj))  # type: ignore
    return _SERIALIZATION_FUNCS[serialization_type](obj)


def serialize_for_storage_dict(obj: Any) -> dict[str, JsonValue]:
    """
    Same as serialize for storage but guarantees outer object is a dictionary
    """
    serialization_type = get_serialization_type(type(obj))  # type: ignore
    return _SERIALIZATION_FUNCS_DICT[serialization_type](obj)


def key_convert_to_snake_case(o: Any) -> Any:
    if isinstance(o, OpaqueKey):
        return o
    if isinstance(o, str):
        return camel_to_snake_case(o)
    return o


def convert_dict_to_snake_case(data: Any) -> Any:
    return {
        key_convert_to_snake_case(k): convert_dict_to_snake_case(v)
        if isinstance(v, dict)
        else v
        for k, v in data.items()
        if v != MISSING_SENTRY
    }


T = TypeVar("T")


def resolve_missing_to_none(val: MissingType[T]) -> Optional[T]:
    return val if not isinstance(val, MissingSentryType) else None
