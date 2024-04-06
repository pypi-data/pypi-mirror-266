import dataclasses
import types
import typing
from collections import defaultdict
from dataclasses import MISSING, dataclass
from datetime import date, datetime
from decimal import Decimal
from importlib import resources

import dateutil.parser
import yaml

from pkgs.serialization import MissingSentryType, OpaqueKey, get_serial_class_data

from ._is_enum import is_string_enum_class
from ._is_namedtuple import is_namedtuple_type
from .case_convert import camel_to_snake_case, snake_to_camel_case

T = typing.TypeVar("T")
ParserFunction = typing.Callable[[typing.Any], T]
ParserCache = dict[typing.Type[typing.Any], ParserFunction[typing.Any]]


@dataclass(frozen=True, eq=True)
class ParserOptions:
    convert_to_snake_case: bool


@dataclass(frozen=True)
class ParserContext:
    options: ParserOptions
    cache: ParserCache


def is_optional(field_type: typing.Any) -> bool:
    return typing.get_origin(field_type) is typing.Union and type(
        None
    ) in typing.get_args(field_type)


def is_missing(field_type: typing.Any) -> bool:
    origin = typing.get_origin(field_type)
    if origin is not typing.Union:
        return False
    args = typing.get_args(field_type)
    if len(args) == 0 or args[0] is not MissingSentryType:
        return False
    return True


def _invoke_tuple_parsers(
    tuple_type: typing.Type[T],
    arg_parsers: typing.Sequence[typing.Callable[[typing.Any], object]],
    has_ellipsis: bool,
    value: typing.Any,
) -> T:
    if has_ellipsis:
        assert len(arg_parsers) == 1
        arg_parser = arg_parsers[0]
        output = (arg_parser(subvalue) for subvalue in value)
    else:
        assert len(value) == len(arg_parsers)
        output = (
            arg_parser(subvalue) for arg_parser, subvalue in zip(arg_parsers, value)
        )

    return typing.cast(T, tuple(output))


def _invoke_fallback_parsers(
    original_type: typing.Type[T],
    arg_parsers: typing.Sequence[typing.Callable[[typing.Any], T]],
    value: typing.Any,
) -> T:
    for parser in arg_parsers:
        try:
            return parser(value)
        except Exception:
            continue
    raise ValueError(
        f"Unhandled value {value} cannot be cast to a member of {original_type}"
    )


def _invoke_membership_parser(
    expected_values: typing.Set[T],
    value: typing.Any,
) -> T:
    """
    Look for the expected_value that matches the provided value. We return the expected_value
    since it may not be the same type as the input (for example, with an enum)
    """
    for test_value in expected_values:
        if value == test_value:
            return test_value

    raise ValueError(f"Expected value from {expected_values} but got value {value}")


def _build_parser_inner(
    parsed_type: typing.Type[T],
    context: ParserContext,
    *,
    convert_string_to_snake_case: bool = False,
) -> ParserFunction[T]:
    """
    convert_to_snake_case - internal flag
                            if convert_to_snake_case is True, and parsed_type is str,
                            then the generated parser will convert camel to snake case case
                            should only be True for cases like dictionary keys
                            should only be True if options.convert_to_snake_case is True

    NOTE: This argument makes caching at this level difficult, as the cache-map
    would need to vary based on this argument. For this reason only dataclasses
    are cached now, as they don't use the argument, and they're known to be safe.
    This is also enough to support some recursion.
    """
    if dataclasses.is_dataclass(parsed_type):
        return _build_parser_dataclass(parsed_type, context)  # type: ignore[arg-type]

    # namedtuple support
    if is_namedtuple_type(parsed_type):
        type_hints = typing.get_type_hints(parsed_type)
        field_parsers = [
            (field_name, _build_parser_inner(type_hints[field_name], context))
            for field_name in parsed_type.__annotations__
        ]
        return lambda value: parsed_type(**{
            field_name: field_parser(
                value.get(
                    snake_to_camel_case(field_name)
                    if context.options.convert_to_snake_case
                    else field_name
                )
            )
            for field_name, field_parser in field_parsers
        })

    if parsed_type == type(None):  # noqa: E721
        return lambda value: _invoke_membership_parser({None}, value)  # type: ignore

    origin = typing.get_origin(parsed_type)
    if origin is tuple:
        args = typing.get_args(parsed_type)
        element_parsers: typing.List[typing.Callable[[typing.Any], object]] = []
        has_ellipsis = False
        for arg in args:
            assert not has_ellipsis
            if arg is Ellipsis:
                assert len(element_parsers) == 1
                has_ellipsis = True
            else:
                element_parsers.append(_build_parser_inner(arg, context))
        return lambda value: _invoke_tuple_parsers(
            parsed_type, element_parsers, has_ellipsis, value
        )

    if origin is typing.Union or isinstance(parsed_type, types.UnionType):
        args = typing.get_args(parsed_type)
        sorted_args = sorted(
            args,
            key=lambda subtype: (0 if subtype == type(None) else 1),  # noqa: E721
        )
        arg_parsers = [_build_parser_inner(arg, context) for arg in sorted_args]
        return lambda value: _invoke_fallback_parsers(parsed_type, arg_parsers, value)

    if parsed_type is typing.Any:
        return lambda value: value

    if origin in (list, set):
        args = typing.get_args(parsed_type)
        if len(args) != 1:
            raise ValueError("List types only support one argument")
        arg_parser = _build_parser_inner(args[0], context)

        def parse(value: typing.Any) -> typing.Any:
            if not isinstance(value, list):
                raise ValueError("value is not a list", parsed_type)
            return origin(arg_parser(x) for x in value)

        return parse

    if origin is dict:
        args = typing.get_args(parsed_type)
        if len(args) != 2:
            raise ValueError("Dict types only support two arguments for now")
        k_parser = _build_parser_inner(
            args[0],
            context,
            convert_string_to_snake_case=context.options.convert_to_snake_case,
        )
        v_parser = _build_parser_inner(args[1], context)
        return lambda value: origin((k_parser(k), v_parser(v)) for k, v in value.items())

    if origin == typing.Literal:
        valid_values: typing.Set[T] = set(typing.get_args(parsed_type))
        return lambda value: _invoke_membership_parser(valid_values, value)

    if parsed_type is str and convert_string_to_snake_case:
        return lambda value: camel_to_snake_case(value)  # type: ignore

    if parsed_type is int:
        # first parse ints to decimal to allow scientific notation and decimals
        # e.g. (1) 1e4 => 1000, (2) 3.0 => 3

        def parse_int(value: typing.Any) -> T:
            if isinstance(value, str):
                assert (
                    "_" not in value
                ), "numbers with underscores not considered integers"

            dec_value = Decimal(value)
            int_value = int(dec_value)
            assert (
                int_value == dec_value
            ), f"value ({value}) cannot be parsed to int without discarding precision"
            return int_value  # type: ignore

        return parse_int

    if parsed_type is datetime:
        return lambda value: dateutil.parser.isoparse(value)  # type:ignore

    if parsed_type is date:
        return lambda value: date.fromisoformat(value)  # type:ignore

    # MyPy: It's unclear why `parsed_type in (str, OpaqueKey)` is flagged as invalid
    # Thus an or statement is used instead, which isn't flagged as invalid.
    if parsed_type is str or parsed_type is OpaqueKey:

        def parse_str(value: typing.Any) -> T:
            if isinstance(value, str):
                return value  # type: ignore
            if isinstance(value, (float, int)):
                return str(value)  # type: ignore
            raise ValueError(f"Invalid string value: {type(value)}: {value}")

        return parse_str

    if parsed_type in (float, dict, bool, Decimal) or is_string_enum_class(parsed_type):
        return lambda value: parsed_type(value)  # type: ignore

    if parsed_type is MissingSentryType:

        def error(value: typing.Any) -> T:
            raise ValueError("Missing type cannot be parsed directly")

        return error
    raise ValueError(f"Unhandled type {parsed_type}")


def _build_parser_dataclass(
    parsed_type: typing.Type[T],
    context: ParserContext,
) -> ParserFunction[T]:
    """
    Use the cache so that recursion involve dataclasses is supported. This
    requires the build order is a bit inverted: the dataclass parser is added
    to the cache prior to building it's field parsers.
    """
    cur_parser = context.cache.get(parsed_type)
    if cur_parser is not None:
        return cur_parser

    type_hints = typing.get_type_hints(parsed_type)
    dc_field_parsers: list[
        typing.Tuple[
            dataclasses.Field[typing.Any],
            typing.Type[typing.Any],
            ParserFunction[typing.Any],
        ]
    ] = []

    serial_class_data = get_serial_class_data(parsed_type)

    def parse(value: typing.Any) -> typing.Any:
        data: typing.Dict[typing.Any, typing.Any] = {}
        for field, field_type, field_parser in dc_field_parsers:
            field_raw_value = None
            try:
                field_raw_value = value.get(
                    snake_to_camel_case(field.name)
                    if (
                        context.options.convert_to_snake_case
                        and not serial_class_data.has_unconverted_key(field.name)
                    )
                    else field.name,
                    MISSING,
                )
                field_value: typing.Any
                if field_raw_value == MISSING:
                    if serial_class_data.has_parse_require(field.name):
                        raise ValueError("missing-required-field", field.name)
                    if field.default != MISSING:
                        field_value = field.default
                    elif field.default_factory != MISSING:
                        field_value = field.default_factory()
                    elif is_missing(field_type):
                        field_value = MissingSentryType()
                    elif is_optional(field_type):
                        # Backwards compatibilty to dataclasses that didn't set a default value
                        # IMPROVE: should we deprecate this?
                        field_value = None
                    elif field_type is bool:
                        # Backwards compatibilty to dataclasses that didn't set a default value
                        field_value = False
                    else:
                        raise ValueError("missing-value-for-field", field.name)
                elif serial_class_data.has_unconverted_value(field.name):
                    field_value = field_raw_value
                else:
                    field_value = field_parser(field_raw_value)

                data[field.name] = field_value

            except Exception as e:
                raise ValueError(
                    f"unable to parse field:{field.name}", field_raw_value
                ) from e

        return parsed_type(**data)

    # Add to cache before building inner types, to support recursion
    parser_function = parse
    context.cache[parsed_type] = parser_function

    dc_field_parsers = [
        (
            field,
            type_hints[field.name],
            _build_parser_inner(type_hints[field.name], context),
        )
        for field in dataclasses.fields(parsed_type)  # type:ignore[arg-type]
    ]

    return parser_function


_CACHE_MAP: dict[ParserOptions, ParserCache] = defaultdict(ParserCache)


def build_parser(
    parsed_type: typing.Type[T],
    options: ParserOptions,
) -> ParserFunction[T]:
    """
    Consider using CachedParser to provide a cleaner API for storage and API
    data parsing.
    """

    # Keep a cache per ParserOptions type, as they produce distinct parsers
    cache = _CACHE_MAP[options]

    cur_parser = cache.get(parsed_type)
    if cur_parser is not None:
        return cur_parser

    context = ParserContext(options=options, cache=cache)
    built_parser = _build_parser_inner(parsed_type, context)
    cache[parsed_type] = built_parser
    return built_parser


class CachedParser(typing.Generic[T]):
    def __init__(
        self,
        args: typing.Type[T],
    ):
        self.arguments = args
        self.parser_api: typing.Optional[ParserFunction[T]] = None
        self.parser_storage: typing.Optional[ParserFunction[T]] = None

    def parse_api(self, args: typing.Any) -> T:
        """
        Parses data coming from an API/Endpoint

        NOTE: Some places use this to parse storage data due to backwards
        compatibility. If your data is coming from the DB or a file, it is
        preferred to use parse_storage.
        """
        if self.parser_api is None:
            self.parser_api = build_parser(
                self.arguments,
                ParserOptions(
                    convert_to_snake_case=True,
                ),
            )
        assert self.parser_api is not None
        return self.parser_api(args)

    def parse_storage(self, args: typing.Any) -> T:
        """
        Parses data coming from the database or file.
        """
        if self.parser_storage is None:
            self.parser_storage = build_parser(
                self.arguments,
                ParserOptions(
                    convert_to_snake_case=False,
                ),
            )
        assert self.parser_storage is not None
        return self.parser_storage(args)

    def parse_yaml_file(self, path: str) -> T:
        with open(path, encoding="utf-8") as data_in:
            return self.parse_storage(yaml.safe_load(data_in))

    def parse_yaml_resource(self, package: resources.Package, resource: str) -> T:
        with resources.open_text(package, resource) as fp:
            return self.parse_storage(yaml.safe_load(fp))
