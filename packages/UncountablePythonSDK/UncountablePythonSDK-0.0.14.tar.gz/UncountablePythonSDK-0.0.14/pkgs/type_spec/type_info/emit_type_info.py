import copy
import dataclasses
import io
import json
from typing import Any, Optional, TypeAlias, Union, cast

from main.base.types import data_t
from main.base.types.base import PureJsonValue
from pkgs.argument_parser import CachedParser
from pkgs.serialization_util import serialize_for_api, serialize_for_storage

from .. import builder, util
from ..emit_typescript_util import MODIFY_NOTICE, ts_name
from ..value_spec import convert_to_value_spec_type

ext_info_parser = CachedParser(data_t.ExtInfo)


def type_path_of(stype: builder.SpecType) -> object:  # NamePath
    """
    Returns a type path for a given type. The output syntax, below, is chosen for storage
    in JSON with relatively easy understanding, and hopefully forward compatible with
    extended scopes, generics, and enum literal values.
    - Scoped Type: [ (namespace-string)..., type-string ]
    - Instance Type: [ "$instance", Scoped-Type-Base, [TypePath-Parameters...] ]
    - Literal Type: [ "$literal", [ "$value", value ]... ]

    @return (string-specific, multiple-types)
    """
    if isinstance(stype, builder.SpecTypeDefn):
        if stype.is_base:  # assume correct namespace
            return [stype.name]
        return [stype.namespace.name, stype.name]

    if isinstance(stype, builder.SpecTypeInstance):
        if stype.defn_type.name == builder.BaseTypeName.s_literal:
            parts: list[str | list[str | bool]] = ["$literal"]
            for parameter in stype.parameters:
                assert isinstance(parameter, builder.SpecTypeLiteralWrapper)
                # This allows expansion to enum literal values later
                parts.append(["$value", parameter.value])
            return parts

        return [
            # this allows the front-end to not have to know if something is a generic by name
            "$instance",
            type_path_of(stype.defn_type),
            [type_path_of(parameter) for parameter in stype.parameters],
        ]

    raise Exception("unhandled-SpecType")


def _dict_null_strip(data: dict[str, object]) -> dict[str, object]:
    """
    We know the output supports missing fields in place of nulls for the
    dictionary keys. This will not look inside lists ensuring any eventual
    complex data literals/constants will be preserved.
    This is strictly to compact the output, as there will be many nulls.
    """
    return {
        key: (_dict_null_strip(value) if isinstance(value, dict) else value)
        for key, value in data.items()
        if value is not None
    }


def emit_type_info(build: builder.SpecBuilder, output: str) -> None:
    type_map = _build_map_all(build)

    # sort for stability, indent for smaller diffs
    stripped = _dict_null_strip(dataclasses.asdict(type_map))
    serial = json.dumps(stripped, sort_keys=True, indent=2)
    type_map_out = io.StringIO()
    type_map_out.write(MODIFY_NOTICE)
    type_map_out.write(f"export const TYPE_MAP = {serial}")

    util.rewrite_file(f"{output}/type_map.ts", type_map_out.getvalue())


@dataclasses.dataclass
class MapProperty:
    api_name: str
    type_name: str
    label: str | None
    type_path: object
    extant: str
    ext_info: PureJsonValue | None
    desc: str | None
    # We don't have typing on defaults yet, relying on emitters to check it. Limit
    # use of this field, as it'll necessarily change when adding type info
    default: object


@dataclasses.dataclass
class MapTypeBase:
    type_name: str
    label: str | None
    desc: str | None
    ext_info: PureJsonValue | None


@dataclasses.dataclass
class MapTypeObject(MapTypeBase):
    base_type_path: object
    properties: dict[str, MapProperty]


@dataclasses.dataclass
class MapTypeAlias(MapTypeBase):
    alias_type_path: object
    discriminator: str | None


@dataclasses.dataclass
class MapStringEnum(MapTypeBase):
    values: dict[str, str]


MapType: TypeAlias = Union[MapTypeObject, MapTypeAlias, MapStringEnum]


@dataclasses.dataclass
class MapNamespace:
    types: dict[str, MapType]


@dataclasses.dataclass
class MapAll:
    namespaces: dict[str, MapNamespace]


def _build_map_all(build: builder.SpecBuilder) -> MapAll:
    map_all = MapAll(namespaces={})

    for namespace in build.namespaces.values():
        if not namespace.emit_type_info:
            continue

        map_namespace = MapNamespace(types={})
        map_all.namespaces[namespace.name] = map_namespace

        for type_ in namespace.types.values():
            map_type = _build_map_type(build, type_)
            if map_type is not None:
                map_namespace.types[type_.name] = map_type

    return map_all


def _build_map_type(
    build: builder.SpecBuilder, stype: builder.SpecTypeDefn
) -> MapType | None:
    # limited support for now
    if (
        isinstance(stype, builder.SpecTypeDefnObject)
        and len(stype.parameters) == 0
        and not stype.is_base
        and stype.base is not None
    ):
        properties: dict[str, MapProperty] = {}
        map_type = MapTypeObject(
            type_name=stype.name,
            label=stype.label,
            properties=properties,
            desc=stype.desc,
            base_type_path=type_path_of(stype.base),
            ext_info=_convert_ext_info(stype.ext_info),
        )

        if stype.properties is not None:
            for prop in stype.properties.values():
                map_property = MapProperty(
                    type_name=prop.name,
                    label=prop.label,
                    api_name=ts_name(prop.name, prop.name_case),
                    extant=prop.extant,
                    type_path=type_path_of(prop.spec_type),
                    ext_info=_convert_ext_info(prop.ext_info),
                    desc=prop.desc,
                    default=prop.default,
                )
                map_type.properties[prop.name] = map_property

        return map_type

    if isinstance(stype, builder.SpecTypeDefnAlias):
        return MapTypeAlias(
            type_name=stype.name,
            label=stype.label,
            desc=stype.desc,
            alias_type_path=type_path_of(stype.alias),
            ext_info=_convert_ext_info(stype.ext_info),
            discriminator=stype.discriminator,
        )

    if isinstance(stype, builder.SpecTypeDefnStringEnum):
        return MapStringEnum(
            type_name=stype.name,
            label=stype.label,
            desc=stype.desc,
            ext_info=_convert_ext_info(stype.ext_info),
            # IMPROVE: We probably want the label here, but this requires a change
            # to the front-end type-info and form code to handle
            values={
                entry.value: (entry.label or entry.name)
                for entry in stype.values.values()
            },
        )

    return None


def _convert_ext_info(in_ext: Any) -> Optional[PureJsonValue]:
    if in_ext is None:
        return None
    assert isinstance(in_ext, dict)
    mod_ext = copy.deepcopy(in_ext)

    df = mod_ext.get("data_format")
    if df is not None:
        df_type = df.get("type")
        assert df_type is not None

        # Do some patch-ups before parsing to get better syntax on types
        if df_type == data_t.DataFormatType.VALUE_SPEC and "result_type" in df:
            result_type_path = util.parse_type_str(df["result_type"])
            converted = convert_to_value_spec_type(result_type_path)
            df["result_type"] = serialize_for_storage(converted)
            mod_ext["data_format"] = df

    parsed = ext_info_parser.parse_storage(mod_ext)
    # we need to convert this to API storage since it'll be used as-is in the UI
    return cast(PureJsonValue, serialize_for_api(parsed))
