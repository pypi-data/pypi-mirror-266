import inspect
import typing
from enum import Enum


def is_string_enum_class(object_type: typing.Type[typing.Any]) -> bool:
    return (
        inspect.isclass(object_type)
        and issubclass(object_type, Enum)
        and issubclass(object_type, str)
    )


def is_string_enum_instance(obj: typing.Any) -> bool:
    object_type = type(obj)
    return is_string_enum_class(object_type)
