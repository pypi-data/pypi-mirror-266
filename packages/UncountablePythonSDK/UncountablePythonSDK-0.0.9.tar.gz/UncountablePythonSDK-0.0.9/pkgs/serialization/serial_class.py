from __future__ import annotations

import dataclasses
from typing import Any, Callable, Optional, TypeVar, cast

from pkgs.strenum_compat import StrEnum

_ClassT = TypeVar("_ClassT")


@dataclasses.dataclass
class _SerialClassData:
    unconverted_keys: set[str] = dataclasses.field(default_factory=set)
    unconverted_values: set[str] = dataclasses.field(default_factory=set)
    to_string_values: set[str] = dataclasses.field(default_factory=set)
    parse_require: set[str] = dataclasses.field(default_factory=set)


def serial_class(
    *,
    unconverted_keys: Optional[set[str]] = None,
    unconverted_values: Optional[set[str]] = None,
    to_string_values: Optional[set[str]] = None,
    parse_require: Optional[set[str]] = None,
) -> Callable[[_ClassT], _ClassT]:
    """
    An additional decorator to a dataclass that specifies serialization options.

    @param unconverted_keys
        The keys of these items will not be case converted (they will be
        left as-is)
    @param unconverted_values
        The values of these items (referred to by field name) will not undergo
        conversion beyond normal json serialization. They should generally
        contain only json compatible types, otherwise the resulting format is
        undefined.
    @param to_string_values
        For the values of these items (referred to by field name) to be strings.
        This is only useful for types where the string conversion makes sense,
        such as Decimal or int.
    @param parse_require
        This field is always required while parsing, even if it has a default in the definition.
        This allows supporting literal type defaults for Python instantiation, but
        requiring them for the API input.
    """

    def decorate(orig_class: _ClassT) -> _ClassT:
        cast(Any, orig_class).__unc_serial_data = _SerialClassData(
            unconverted_keys=unconverted_keys or set(),
            unconverted_values=unconverted_values or set(),
            to_string_values=to_string_values or set(),
            parse_require=parse_require or set(),
        )
        return orig_class

    return decorate


class SerialClassDataInspector:
    bases: list[SerialClassDataInspector]

    def __init__(
        self, bases: list[SerialClassDataInspector], current: _SerialClassData
    ) -> None:
        self.bases = bases
        self.current = current

    def has_unconverted_key(self, key: str) -> bool:
        if key in self.current.unconverted_keys:
            return True
        for base in self.bases:
            if base.has_unconverted_key(key):
                return True
        return False

    def has_unconverted_value(self, key: str) -> bool:
        if key in self.current.unconverted_values:
            return True
        for base in self.bases:
            if base.has_unconverted_value(key):
                return True
        return False

    def has_to_string_value(self, key: str) -> bool:
        if key in self.current.to_string_values:
            return True
        for base in self.bases:
            if base.has_to_string_value(key):
                return True
        return False

    def has_parse_require(self, key: str) -> bool:
        if key in self.current.parse_require:
            return True
        for base in self.bases:
            if base.has_parse_require(key):
                return True
        return False


def get_serial_class_data(type_class: type[Any]) -> SerialClassDataInspector:
    bases = (
        [get_serial_class_data(base) for base in type_class.__bases__]
        if type_class.__bases__ is not None
        else []
    )
    return SerialClassDataInspector(
        bases,
        cast(_SerialClassData, type_class.__unc_serial_data)
        if hasattr(type_class, "__unc_serial_data")
        else _SerialClassData(),
    )


@dataclasses.dataclass(kw_only=True)
class _SerialStringEnumData:
    labels: dict[str, str] = dataclasses.field(default_factory=dict)
    deprecated: set[str] = dataclasses.field(default_factory=set)


def serial_string_enum(
    *, labels: Optional[dict[str, str]] = None, deprecated: Optional[set[str]] = None
) -> Callable[[_ClassT], _ClassT]:
    """
    A decorator for enums to provide serialization data, including labels.
    """

    def decorate(orig_class: _ClassT) -> _ClassT:
        cast(Any, orig_class).__unc_serial_string_enum_data = _SerialStringEnumData(
            labels=labels or {}, deprecated=deprecated or set()
        )
        return orig_class

    return decorate


class SerialStringEnumInspector:
    def __init__(self, current: _SerialStringEnumData) -> None:
        self.current = current

    def get_label(self, value: str) -> Optional[str]:
        return self.current.labels.get(value)

    def get_deprecated(self, value: str) -> bool:
        return value in self.current.deprecated


def get_serial_string_enum_data(type_class: type[StrEnum]) -> SerialStringEnumInspector:
    return SerialStringEnumInspector(
        cast(_SerialStringEnumData, type_class.__unc_serial_string_enum_data)
        if hasattr(type_class, "__unc_serial_string_enum_data")
        else _SerialStringEnumData(),
    )
