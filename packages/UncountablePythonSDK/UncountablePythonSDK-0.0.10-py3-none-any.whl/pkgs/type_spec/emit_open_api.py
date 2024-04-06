"""
Generates an OpenAPI specification based on the type_spec definitions

WORK-IN-PROGRESS, DON'T USE!
"""

import dataclasses
import re
from typing import cast

import yaml

from . import builder, util
from .config import OpenAPIConfig
from .emit_open_api_util import (
    MODIFY_NOTICE,
    EmitOpenAPIContext,
    EmitOpenAPIEndpoint,
    EmitOpenAPIGlobalContext,
    EmitOpenAPIPath,
    EmitOpenAPIServer,
    EmitOpenAPITag,
    GlobalContextInfo,
    TagGroupToNamedTags,
    TagPathsToRef,
    resolve_namespace_ref,
)
from .emit_typescript_util import ts_name
from .open_api_util import (
    OpenAPIArrayType,
    OpenAPIBooleanT,
    OpenAPIEmptyType,
    OpenAPIEnumType,
    OpenAPIFreeFormObjectType,
    OpenAPIIntegerT,
    OpenAPIIntersectionType,
    OpenAPINumberT,
    OpenAPIObjectType,
    OpenAPIRefType,
    OpenAPIStringT,
    OpenAPIType,
    OpenAPIUnionType,
)

base_name_map = {
    builder.BaseTypeName.s_boolean: OpenAPIBooleanT,
    builder.BaseTypeName.s_date: OpenAPIStringT,  # IMPROVE: Aliased DateStr
    builder.BaseTypeName.s_date_time: OpenAPIStringT,  # IMPROVE: Aliased DateTimeStr
    # Decimal's are marked as to_string_values thus are strings in the front-end
    builder.BaseTypeName.s_decimal: OpenAPIStringT,
    builder.BaseTypeName.s_integer: OpenAPIIntegerT,
    builder.BaseTypeName.s_lossy_decimal: OpenAPINumberT,
    builder.BaseTypeName.s_opaque_key: OpenAPIStringT,
    builder.BaseTypeName.s_string: OpenAPIStringT,
    # UNC: global types
}


def _rewrite_with_notice(
    file_path: str, file_content: str, *, notice: str = MODIFY_NOTICE
) -> bool:
    pattern = re.compile("^\S", re.MULTILINE)

    file_lines = file_content.split("\n")
    comment_lines = []
    for line_number, line in enumerate(file_lines):
        match = pattern.match(line)
        if match is not None and match.group() != "-" and line_number > 0:
            comment_lines.append(f"{notice}")
        comment_lines.append(line)

    modified_file_content = "\n".join(comment_lines)

    return util.rewrite_file(file_path, f"{notice}\n{modified_file_content}")


def _open_api_info(config: OpenAPIConfig) -> GlobalContextInfo:
    description = config.description
    info: GlobalContextInfo = dict()
    info["version"] = "1.0.0"
    info["title"] = "Uncountable API Documentation"
    info["description"] = description
    info["x-logo"] = {"url": "../static/images/logo_blue.png", "altText": "Logo"}
    return info


def _open_api_servers(config: OpenAPIConfig) -> list[EmitOpenAPIServer]:
    server_url = config.server_url
    return [EmitOpenAPIServer(url=server_url)] if server_url is not None else []


def emit_open_api(builder: builder.SpecBuilder, *, config: OpenAPIConfig) -> None:
    gctx = EmitOpenAPIGlobalContext(
        version="3.0.0",
        info=_open_api_info(config),
        servers=_open_api_servers(config),
    )

    for namespace in sorted(builder.namespaces.values(), key=lambda ns: ns.name):
        ctx = EmitOpenAPIContext(namespace=namespace)

        if ctx.namespace.name == "base":
            # TODO: add additional base defintions here
            ctx.types["ObjectId"] = OpenAPIIntegerT()
            ctx.types["JsonValue"] = OpenAPIStringT()

        _emit_namespace(
            gctx,
            ctx,
            namespace=namespace,
            config=config,
        )

    _rewrite_with_notice(
        f"{config.types_output}/openapi.yaml", _serialize_global_context(gctx)
    )


def _serialize_global_context(ctx: EmitOpenAPIGlobalContext) -> str:
    oa_root: dict[str, object] = dict()

    oa_root["openapi"] = ctx.version
    oa_root["info"] = ctx.info
    oa_root["servers"] = [*map(dataclasses.asdict, ctx.servers)]

    sorted_tags = sorted(ctx.tags, key=lambda tag: tag.name)
    oa_root["tags"] = [dataclasses.asdict(tag) for tag in sorted_tags]

    oa_tag_groups: list[TagGroupToNamedTags] = []
    for tag_group in sorted(ctx.tag_groups.keys()):
        sub_tags = ctx.tag_groups[tag_group]
        oa_tag_groups.append({"name": tag_group, "tags": sorted(sub_tags)})
    oa_root["x-tagGroups"] = oa_tag_groups

    oa_paths: TagPathsToRef = dict()
    for path in ctx.paths:
        # assert path.path not in oa_paths
        oa_paths[path.path] = {"$ref": path.ref}
    oa_root["paths"] = oa_paths

    return yaml.dump(oa_root, sort_keys=False)


def _emit_endpoint_parameters(typ: OpenAPIType | None) -> dict[str, list[dict[str, str]]]:
    if not isinstance(typ, OpenAPIObjectType):
        return {}

    return {
        "parameters": [
            {"$ref": f"#/components/schema/Arguments/{prop_name}"}
            for prop_name in typ.properties
        ]
    }


def _emit_namespace(
    gctx: EmitOpenAPIGlobalContext,
    ctx: EmitOpenAPIContext,
    namespace: builder.SpecNamespace,
    *,
    config: OpenAPIConfig,
) -> None:
    for stype in namespace.types.values():
        _emit_type(ctx, stype, config=config)

    if namespace.endpoint is not None:
        _emit_endpoint(gctx, ctx, namespace, namespace.endpoint)

    oa_components: dict[str, object] = dict()

    if ctx.endpoint is not None:
        endpoint = ctx.endpoint

        argument_type = ctx.types.get("Arguments")
        oa_endpoint = dict()
        oa_endpoint[endpoint.method] = (
            {
                "tags": endpoint.tags,
                "summary": endpoint.summary,
                "description": endpoint.description,
            }
            | _emit_endpoint_parameters(argument_type)
            | {
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schema/Data"}
                            }
                        },
                    }
                },
            }
        )
        oa_components["endpoint"] = oa_endpoint

    types = ctx.types
    if ctx.endpoint is not None:
        # OpenAPI always expected Arguments and Data create
        # them here if they were not already created
        if "Arguments" not in types:
            types["Arguments"] = OpenAPIObjectType({})
        if "Data" not in types:
            types["Data"] = OpenAPIObjectType({})

    if ctx.endpoint is not None and "Data" in ctx.types:
        # IMPROVE: Handle the general case here: wrap result in data object
        types["Data"] = OpenAPIObjectType({"data": types["Data"]})

    if ctx.endpoint is not None and "Arguments" in ctx.types:
        # OpenAPI Expects a different format for arguments
        # then for regular types; do conversion here
        raw_type = types["Arguments"]
        if isinstance(
            raw_type, (OpenAPIIntersectionType, OpenAPIUnionType, OpenAPIRefType)
        ):
            print(
                f"[Warning] Skipping Documentation Generation for Endpoint {ctx.namespace.name} due to unsupported 'Argument' structure"
            )
            # TODO handle inheritence (allOf and refs); need to inline here...
            # for now skip this endpoint
            return

        assert isinstance(raw_type, (OpenAPIObjectType, OpenAPIFreeFormObjectType))

    oa_components["schema"] = cast(
        object,
        {
            name: (value.asdict() if name != "Arguments" else value.asarguments())
            for name, value in types.items()
        },
    )

    path = f"{config.types_output}/common/{'/'.join(namespace.path)}.yaml"
    oa_namespace = {"components": oa_components}
    _rewrite_with_notice(path, yaml.dump(oa_namespace, sort_keys=False))


def _emit_type(
    ctx: EmitOpenAPIContext,
    stype: builder.SpecType,
    *,
    config: OpenAPIConfig,
) -> None:
    if not isinstance(stype, builder.SpecTypeDefn):
        return
    if stype.is_base or stype.is_predefined:
        return

    if isinstance(stype, builder.SpecTypeDefnExternal):
        # IMPROVE: handle external definitions better (for now map to any)
        ctx.types[stype.name] = OpenAPIEmptyType(
            nullable=True,
            description=f"External Type Definition ({stype.name})",
        )
        return

    assert stype.is_exported, "expecting exported names"
    if isinstance(stype, builder.SpecTypeDefnAlias):
        ctx.types[stype.name] = open_api_type(ctx, stype.alias, config=config)
        return

    if isinstance(stype, builder.SpecTypeDefnStringEnum):
        # TODO: check that these are always string enums
        # IMPROVE: reflect the enum names in the description

        # we just use the values here as that is what is being sent...
        values = [entry.value for entry in stype.values.values()]
        ctx.types[stype.name] = OpenAPIEnumType(values)
        return

    assert isinstance(stype, builder.SpecTypeDefnObject)
    assert stype.base is not None

    if stype.properties is None and stype.base.is_base:
        ctx.types[stype.name] = OpenAPIObjectType({})
        return
    elif stype.properties is None:
        # TODO: check if these are actually equivalent
        ctx.types[stype.name] = open_api_type(ctx, stype.base, config=config)
        return
    else:
        properties: dict[str, OpenAPIType] = dict()
        property_desc: dict[str, str] = dict()

        for prop in stype.properties.values():
            ref_type = open_api_type(ctx, prop.spec_type, config=config)
            prop_name = ts_name(prop.name, prop.name_case or stype.name_case)
            if prop.desc:
                property_desc[prop_name] = prop.desc
            if prop.has_default and not prop.parse_require:
                # For now, we'll assume the generated types with defaults are meant as
                # arguments, thus treat like extant==missing
                # IMPROVE: if we can decide they are meant as output instead, then
                # they should be marked as required
                properties[prop_name] = ref_type
            elif prop.extant == builder.PropertyExtant.missing:
                # Unlike optional below, missing does not imply null is possible. They
                # treated distinctly.
                properties[prop_name] = ref_type
            elif prop.extant == builder.PropertyExtant.optional:
                # Need to add in |null since Python side can produce null's right now
                # IMPROVE: It would be better if the serializer could instead omit the None's
                # Dropping the null should be forward compatible
                ref_type.nullable = True
                properties[prop_name] = ref_type
            else:
                properties[prop_name] = ref_type
        final_type: OpenAPIType = OpenAPIObjectType(
            properties, property_desc=property_desc
        )

    if not stype.base.is_base:
        # support inheritance via allOf
        final_type = OpenAPIIntersectionType([
            open_api_type(ctx, stype.base, config=config),
            final_type,
        ])

    ctx.types[stype.name] = final_type


def _emit_constant(ctx: EmitOpenAPIContext, sconst: builder.SpecConstant) -> None:
    if sconst.value_type.is_base_type(builder.BaseTypeName.s_string):
        value = util.encode_common_string(cast(str, sconst.value))
    elif sconst.value_type.is_base_type(builder.BaseTypeName.s_integer):
        value = str(sconst.value)
    else:
        raise Exception("invalid constant type", sconst.name)

    const_name = sconst.name.upper()
    print("_emit_constant", value, const_name)


def _emit_endpoint(
    gctx: EmitOpenAPIGlobalContext,
    ctx: EmitOpenAPIContext,
    namespace: builder.SpecNamespace,
    endpoint: builder.SpecEndpoint,
) -> None:
    assert namespace.endpoint is not None
    assert namespace.path[0] == "api"

    has_arguments = "Arguments" in namespace.types
    has_data = "Data" in namespace.types
    has_deprecated_result = "DeprecatedResult" in namespace.types
    is_binary = endpoint.result_type == builder.ResultType.binary

    result_type_count = sum([has_data, has_deprecated_result, is_binary])

    assert result_type_count < 2
    is_binary = endpoint.result_type == builder.ResultType.binary

    # Don't emit interface for those with unsupported types
    if not has_arguments or result_type_count == 0:
        return
    if not is_binary and endpoint.result_type != builder.ResultType.json:
        return

    assert len(namespace.path) > 1
    tag_group = namespace.path[1]
    tag_subgroup = namespace.path[2] if len(namespace.path) > 2 else "General"

    tag_name = f"{tag_group}/{tag_subgroup}"
    # IMPROVE Add Per Tag Descriptions via type_spec index files
    gctx.tags.add(EmitOpenAPITag(name=tag_name, description=""))
    gctx.tag_groups[tag_group].add(tag_name)

    ref_path = f"common/{'/'.join(namespace.path)}.yaml#/components/endpoint"
    ep = namespace.endpoint
    gctx.paths.append(
        EmitOpenAPIPath(
            path=f"/{ep.path_root}/{ep.path_dirname}/{ep.path_basename}",
            ref=ref_path,
        )
    )

    description = namespace.endpoint.desc if namespace.endpoint.desc is not None else ""
    if endpoint.is_external:
        description = f"**[External API-Endpoint]** <br/> {description}"

    path_cutoff = min(3, len(namespace.path) - 1)
    ctx.endpoint = EmitOpenAPIEndpoint(
        method=namespace.endpoint.method.lower(),
        tags=[tag_name],
        summary=f"{'/'.join(namespace.path[path_cutoff:])}",
        description=description,
    )


def _enum_name(name: str, name_case: builder.NameCase) -> str:
    if name_case == builder.NameCase.js_upper:
        return name.upper()
    return ts_name(name, name_case)


def _emit_value(stype: builder.SpecType, value: object) -> str:
    """Mimics emit_python even if not all types are used in OpenAPI yet"""
    literal = builder.unwrap_literal_type(stype)
    if literal is not None:
        return _emit_value(literal.value_type, literal.value)

    if stype.is_base_type(builder.BaseTypeName.s_string):
        assert isinstance(value, str)
        return util.encode_common_string(value)
    elif stype.is_base_type(builder.BaseTypeName.s_integer):
        assert isinstance(value, int)
        return str(value)
    elif stype.is_base_type(builder.BaseTypeName.s_boolean):
        assert isinstance(value, bool)
        return "true" if value else "false"
    elif stype.is_base_type(builder.BaseTypeName.s_lossy_decimal):
        return str(value)
    elif stype.is_base_type(builder.BaseTypeName.s_decimal):
        return f"'{value}'"
    elif isinstance(stype, builder.SpecTypeDefnStringEnum):
        return f"{stype.name}.{_enum_name(str(value), stype.name_case)}"
    else:
        raise Exception("invalid constant type", value, stype)


def open_api_type(
    ctx: EmitOpenAPIContext,
    stype: builder.SpecType,
    *,
    config: OpenAPIConfig,
) -> OpenAPIType:
    if isinstance(stype, builder.SpecTypeInstance):
        if stype.defn_type.name == builder.BaseTypeName.s_list:
            return OpenAPIArrayType(
                open_api_type(ctx, stype.parameters[0], config=config)
            )
        if stype.defn_type.name == builder.BaseTypeName.s_union:
            return OpenAPIUnionType([
                open_api_type(ctx, p, config=config) for p in stype.parameters
            ])
        if stype.defn_type.name == builder.BaseTypeName.s_literal:
            # IMPROVE relax the string constraint for literals (for now treat as string)
            parts = []
            for parameter in stype.parameters:
                assert isinstance(parameter, builder.SpecTypeLiteralWrapper)
                parts.append(parameter.value)

            return OpenAPIEnumType([str(x) for x in parts])
        if stype.defn_type.name == builder.BaseTypeName.s_optional:
            ref_type = open_api_type(ctx, stype.parameters[0], config=config)
            ref_type.nullable = True
            return ref_type
        if stype.defn_type.name == builder.BaseTypeName.s_tuple:
            # IMPROVE potentially handle tuples better: for now map tupples to arrays of those types
            return OpenAPIArrayType(
                [open_api_type(ctx, p, config=config) for p in stype.parameters],
                description="TupleType",
            )

        # TODO: generics are not supported by OpenAPI
        # map to Free-Form Object and add description
        # IMPROVE: Create a better description for this
        return OpenAPIFreeFormObjectType(description=f"({stype.defn_type.name})")

    if isinstance(stype, builder.SpecTypeLiteralWrapper):
        # TODO: relax the string constraint for literals (for now treat as string)
        # i.e. convert from stype.value_type
        return OpenAPIEnumType([_emit_value(stype.value_type, stype.value)])

    assert isinstance(stype, builder.SpecTypeDefn)
    if stype.is_base:  # assume correct namespace
        if stype.name == builder.BaseTypeName.s_list:
            return OpenAPIArrayType([])  # TODO: generic type
        return base_name_map[builder.BaseTypeName(stype.name)]()

    if stype.namespace == ctx.namespace:
        # internal namespace resolution
        return OpenAPIRefType(source=f"#/components/schema/{stype.name}")

    ctx.namespaces.add(stype.namespace)
    # external namespace resolution
    return OpenAPIRefType(
        source=f"{resolve_namespace_ref(source_path=ctx.namespace.path, ref_path=stype.namespace.path, ref='/components/schema')}/{stype.name}"
    )
