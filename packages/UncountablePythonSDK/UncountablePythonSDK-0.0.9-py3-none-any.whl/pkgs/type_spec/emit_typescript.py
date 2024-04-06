import io
import os
from typing import Any, Tuple

from . import builder, util
from .builder import SpecTypeDefnObject
from .config import TypeScriptConfig
from .emit_io_ts import emit_type_io_ts
from .emit_typescript_util import (
    INDENT,
    MODIFY_NOTICE,
    EmitTypescriptContext,
    resolve_namespace_ref,
    ts_name,
    ts_type_name,
)


def ts_enum_name(name: str, name_case: builder.NameCase) -> str:
    if name_case == builder.NameCase.js_upper:
        return name.upper()
    return ts_name(name, name_case)


def _resolve_namespace_name(namespace: builder.SpecNamespace) -> str:
    return namespace.name


def _emit_value(ctx: EmitTypescriptContext, stype: builder.SpecType, value: Any) -> str:
    """Mimics emit_python even if not all types are used in TypeScript yet"""
    literal = builder.unwrap_literal_type(stype)
    if literal is not None:
        return _emit_value(ctx, literal.value_type, literal.value)

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
    elif isinstance(stype, builder.SpecTypeInstance):
        if stype.defn_type.is_base_type(builder.BaseTypeName.s_list):
            sub_type = stype.parameters[0]
            return "[" + ", ".join([_emit_value(ctx, sub_type, x) for x in value]) + "]"

        if stype.defn_type.is_base_type(builder.BaseTypeName.s_dict):
            key_type = stype.parameters[0]
            value_type = stype.parameters[1]
            return (
                "{\n\t"
                + ",\n\t".join(
                    "["
                    + _emit_value(ctx, key_type, dkey)
                    + "]: "
                    + _emit_value(ctx, value_type, dvalue)
                    for dkey, dvalue in value.items()
                )
                + "\n}"
            )

        if stype.defn_type.is_base_type(builder.BaseTypeName.s_optional):
            sub_type = stype.parameters[0]
            if value is None:
                return "null"
            return _emit_value(ctx, sub_type, value)

    elif isinstance(stype, builder.SpecTypeDefnStringEnum):
        return f"{refer_to(ctx, stype)}.{ts_enum_name(value, stype.name_case)}"

    raise Exception("invalid constant type", value, stype)


def emit_typescript(builder: builder.SpecBuilder, config: TypeScriptConfig) -> None:
    _emit_types(builder, config)
    _emit_id_source(builder, config)


def _emit_types(builder: builder.SpecBuilder, config: TypeScriptConfig) -> None:
    index_out = io.StringIO()
    index_out.write(MODIFY_NOTICE)

    index_out_end = io.StringIO()

    for namespace in sorted(
        builder.namespaces.values(),
        key=lambda ns: _resolve_namespace_name(ns),
    ):
        ctx = EmitTypescriptContext(out=io.StringIO(), namespace=namespace, config=config)

        _emit_namespace(ctx, namespace)

        prepart = builder.preparts["typescript"].get(namespace.name)
        part = builder.parts["typescript"].get(namespace.name)

        # Don't emit an empty file
        if (
            prepart is None
            and part is None
            and len(namespace.types) == 0
            and len(namespace.constants) == 0
        ):
            # Try to capture some common incompleteness errors
            if namespace.endpoint is None or namespace.endpoint.function is None:
                raise Exception(
                    f"Namespace {'/'.join(namespace.path)} is incomplete. It should have an endpoint with function, types, and/or constants"
                )
            continue

        full = io.StringIO()
        if prepart:
            full.write(MODIFY_NOTICE)
            full.write(f"// === START section from {namespace.name}.ts.prepart ===\n")
            full.write(prepart)
            full.write(f"// === END section from {namespace.name}.ts.prepart ===\n")
            full.write("\n")

        for ns in sorted(
            ctx.namespaces,
            key=lambda name: _resolve_namespace_name(name),
        ):
            import_as = resolve_namespace_ref(ns)
            import_path = (
                "./" if len(namespace.path) == 1 else "../" * (len(namespace.path) - 1)
            )
            import_from = f"{import_path}{_resolve_namespace_name(ns)}"
            full.write(f'import * as {import_as} from "{import_from}"\n')  # noqa: E501
        if namespace.emit_io_ts:
            full.write("import * as IO from 'io-ts';")
        full.write(ctx.out.getvalue())

        if part:
            full.write("\n")
            full.write(MODIFY_NOTICE)
            full.write(f"// === START section from {namespace.name}.ts.part ===\n")
            full.write(part)
            full.write(f"// === END section from {namespace.name}.ts.part ===\n")

        full.write(MODIFY_NOTICE)

        basename = "/".join(namespace.path)
        filename = f"{config.types_output}/{basename}.ts"
        util.rewrite_file(filename, full.getvalue())

        if len(namespace.path) == 1:
            index_out.write(
                f"import * as {resolve_namespace_ref(namespace)} from './{_resolve_namespace_name(namespace)}'\n"
            )  # noqa: E501
            index_out_end.write(f"export {{{resolve_namespace_ref(namespace)}}}\n")

    index_out.write("\n")
    index_out.write(MODIFY_NOTICE)
    index_out.write(index_out_end.getvalue())
    index_out.write(MODIFY_NOTICE)
    util.rewrite_file(f"{config.types_output}/index.ts", index_out.getvalue())


def _emit_namespace(ctx: EmitTypescriptContext, namespace: builder.SpecNamespace) -> None:
    for stype in namespace.types.values():
        if namespace.emit_io_ts:
            emit_type_io_ts(ctx, stype, namespace.derive_types_from_io_ts)
        if not namespace.emit_io_ts or not namespace.derive_types_from_io_ts:
            _emit_type(ctx, stype)

    for sconst in namespace.constants.values():
        _emit_constant(ctx, sconst)

    if namespace.endpoint is not None:
        _emit_endpoint(ctx, namespace, namespace.endpoint)


def _emit_endpoint(
    ctx: EmitTypescriptContext,
    namespace: builder.SpecNamespace,
    endpoint: builder.SpecEndpoint,
) -> None:
    if endpoint.suppress_ts:
        return

    assert namespace.path[0] == "api"
    has_arguments = "Arguments" in namespace.types
    has_data = "Data" in namespace.types
    has_deprecated_result = "DeprecatedResult" in namespace.types
    is_binary = endpoint.result_type == builder.ResultType.binary

    result_type_count = sum([has_data, has_deprecated_result, is_binary])
    assert result_type_count < 2

    # Don't emit interface for those with unsupported types
    if not has_arguments or result_type_count == 0:
        return

    if not is_binary:
        assert endpoint.result_type == builder.ResultType.json

    data_loader_head = ""
    data_loader_body = ""
    if endpoint.data_loader:
        # Don't support alternately named data for now
        assert has_data

        data_loader_head = (
            'import { buildApiDataLoader, argsKey } from "unc_base/data_manager"\n'
        )
        data_loader_body = (
            "\nexport const data = buildApiDataLoader(argsKey(), apiCall)\n"
        )

    method = endpoint.method.capitalize()
    if endpoint.has_attachment:
        assert endpoint.method == "post"
        method = f"{method}Attach"
    wrap_name = (
        f"buildWrappedBinary{method}Call" if is_binary else f"buildWrapped{method}Call"
    )
    wrap_call = (
        f"{wrap_name}<Arguments>" if is_binary else f"{wrap_name}<Arguments, Response>"
    )
    type_path = f"unc_mat/types/{'/'.join(namespace.path)}"

    if is_binary:
        tsx_response_part = f"""import {{ {wrap_name} }} from "unc_base/api"
import {{ Arguments }} from "{type_path}"

export type {{ Arguments }}
"""
    elif has_data and endpoint.has_attachment:
        tsx_response_part = f"""import {{ {wrap_name}, AttachmentResponse }} from "unc_base/api"
import {{ Arguments, Data }} from "{type_path}"

export type {{ Arguments, Data }}
export type Response = AttachmentResponse<Data>
"""
    elif has_data:
        tsx_response_part = f"""import {{ {wrap_name}, JsonResponse }} from "unc_base/api"
import {{ Arguments, Data }} from "{type_path}"

export type {{ Arguments, Data }}
export type Response = JsonResponse<Data>
"""

    else:
        assert has_deprecated_result
        tsx_response_part = f"""import {{ {wrap_name} }} from "unc_base/api"
import {{ Arguments, DeprecatedResult }} from "{type_path}"

export type {{ Arguments }}
export type Response = DeprecatedResult
"""

    tsx_api = f"""{MODIFY_NOTICE}
{data_loader_head}{tsx_response_part}
export const apiCall = {wrap_call}(
  "{endpoint.path_root}/{endpoint.path_dirname}/{endpoint.path_basename}",
)
{data_loader_body}"""

    output = f"{ctx.config.routes_output}/{'/'.join(namespace.path)}.tsx"
    util.rewrite_file(output, tsx_api)

    # Hacky index support, until enough is migrated to regen entirely
    # Emits the import into the UI API index file
    index_path = f"{ctx.config.routes_output}/{'/'.join(namespace.path[0:-1])}/index.tsx"
    api_name = f"Api{ts_type_name(namespace.path[0 - 1])}"
    if os.path.exists(index_path):
        with open(index_path) as index:
            index_data = index.read()
            need_index = index_data.find(api_name) == -1
    else:
        need_index = True

    if need_index:
        with open(index_path, "a") as index:
            print(f"Updated API Index {index_path}")
            index.write("\n// eslint-disable-next-line import/first\n")
            index.write(f'import * as {api_name} from "./{namespace.path[-1]}"\n\n')
            index.write(f"export {{ {api_name} }}\n")


MARKER_BEGIN = "### BEGIN:TYPE_SPEC"
MARKER_END = "### END:TYPE_SPEC"


def _patch_file_line(filename: str, line: str) -> None:
    """
    Adds a line into a file inside a marked region. The file section is
    kept ordered. The rest of the file is untouched.
    """
    with open(filename) as ignore_in:
        ignore_data = ignore_in.read()
        need_ignore = ignore_data.find(line) == -1
        if not need_ignore:
            return

    begin = ignore_data.find(MARKER_BEGIN)
    end = ignore_data.find(MARKER_END)
    if begin == -1 or end == -1:
        predata = ignore_data
        postdata = ""
        linedata = ""
    else:
        predata = ignore_data[:begin]
        postdata = ignore_data[(end + len(MARKER_END)) :]
        linedata = ignore_data[begin + len(MARKER_BEGIN) : end]

    lines = [y for y in [x.strip() for x in linedata.split("\n")] if len(y) > 0]
    lines.append(line)

    with open(filename, "w") as ignore_out:
        ignore_out.write(f"{predata}{MARKER_BEGIN}\n")
        ignore_out.write("\n".join(sorted(lines)))
        ignore_out.write(f"\n{MARKER_END}{postdata}")


def _emit_type(ctx: EmitTypescriptContext, stype: builder.SpecType) -> None:
    if not isinstance(stype, builder.SpecTypeDefn):
        return

    if stype.is_base or stype.is_predefined:
        return

    ctx.out.write("\n")
    ctx.out.write(MODIFY_NOTICE)

    if isinstance(stype, builder.SpecTypeDefnExternal):
        assert not stype.is_exported, "expecting private names"
        ctx.out.write(stype.external_map["ts"])
        ctx.out.write("\n")
        return

    assert stype.is_exported, "expecting exported names"
    if isinstance(stype, builder.SpecTypeDefnAlias):
        ctx.out.write(f"export type {stype.name} = {refer_to(ctx, stype.alias)}\n")
        return

    if isinstance(stype, builder.SpecTypeDefnStringEnum):
        ctx.out.write(f"export enum {stype.name} {{\n")
        assert stype.values
        for name, entry in stype.values.items():
            ctx.out.write(
                f'{INDENT}{ts_enum_name(name, stype.name_case)} = "{entry.value}",\n'
            )
        ctx.out.write("}\n")
        return

    assert isinstance(stype, builder.SpecTypeDefnObject)
    assert stype.base is not None

    base_type = ""
    if not stype.base.is_base:
        base_type = f"{refer_to(ctx, stype.base)} & "

    if stype.properties is None and base_type == "":
        ctx.out.write(f"export type {stype.name} = TEmpty\n")
    elif stype.properties is None:
        ctx.out.write(f"export type {stype.name} = {base_type}{{}}\n")
    else:
        if isinstance(stype, SpecTypeDefnObject) and len(stype.parameters) > 0:
            full_type_name = f'{stype.name}<{", ".join(stype.parameters)}>'
        else:
            full_type_name = stype.name
        ctx.out.write(f"export type {full_type_name} = {base_type}{{")
        ctx.out.write("\n")
        for prop in stype.properties.values():
            ref_type = refer_to(ctx, prop.spec_type)
            prop_name = ts_name(prop.name, prop.name_case)
            if prop.has_default and not prop.parse_require:
                # For now, we'll assume the generated types with defaults are meant as
                # arguments, thus treat like extant==missing
                # IMPROVE: if we can decide they are meant as output instead, then
                # they should be marked as required
                ctx.out.write(f"{INDENT}{prop_name}?: {ref_type}")
            elif prop.extant == builder.PropertyExtant.missing:
                # Unlike optional below, missing does not imply null is possible. They
                # treated distinctly.
                ctx.out.write(f"{INDENT}{prop_name}?: {ref_type}")
            elif prop.extant == builder.PropertyExtant.optional:
                # Need to add in |null since Python side can produce null's right now
                # IMPROVE: It would be better if the serializer could instead omit the None's
                # Dropping the null should be forward compatible
                ctx.out.write(f"{INDENT}{prop_name}?: {ref_type} | null")
            else:
                ctx.out.write(f"{INDENT}{prop_name}: {ref_type}")
            ctx.out.write("\n")
        ctx.out.write("}\n")


def _emit_constant(ctx: EmitTypescriptContext, sconst: builder.SpecConstant) -> None:
    ctx.out.write("\n\n")
    ctx.out.write(MODIFY_NOTICE)
    value = _emit_value(ctx, sconst.value_type, sconst.value)
    const_name = sconst.name.upper()
    ctx.out.write(f"export const {const_name} = {value}\n")


base_name_map = {
    builder.BaseTypeName.s_boolean: "boolean",
    builder.BaseTypeName.s_date: "string",  # IMPROVE: Aliased DateStr
    builder.BaseTypeName.s_date_time: "string",  # IMPROVE: Aliased DateTimeStr
    # Decimal's are marked as to_string_values thus are strings in the front-end
    builder.BaseTypeName.s_decimal: "string",
    builder.BaseTypeName.s_dict: "PartialRecord",
    builder.BaseTypeName.s_integer: "number",
    builder.BaseTypeName.s_lossy_decimal: "number",
    builder.BaseTypeName.s_opaque_key: "string",
    builder.BaseTypeName.s_none: "null",
    builder.BaseTypeName.s_string: "string",
    # UNC: global types
    builder.BaseTypeName.s_json_value: "JsonValue",
}


def refer_to(ctx: EmitTypescriptContext, stype: builder.SpecType) -> str:
    return refer_to_impl(ctx, stype)[0]


def refer_to_impl(
    ctx: EmitTypescriptContext, stype: builder.SpecType
) -> Tuple[str, bool]:
    """
    @return (string-specific, multiple-types)
    """
    if isinstance(stype, builder.SpecTypeInstance):
        if stype.defn_type.name == builder.BaseTypeName.s_list:
            spec, multi = refer_to_impl(ctx, stype.parameters[0])
            return f"({spec})[]" if multi else f"{spec}[]", False
        if stype.defn_type.name == builder.BaseTypeName.s_union:
            return f'({" | ".join([refer_to(ctx, p) for p in stype.parameters])})', False
        if stype.defn_type.name == builder.BaseTypeName.s_literal:
            parts = []
            for parameter in stype.parameters:
                assert isinstance(parameter, builder.SpecTypeLiteralWrapper)
                parts.append(refer_to(ctx, parameter))
            return f'({" | ".join(parts)})', False
        if stype.defn_type.name == builder.BaseTypeName.s_optional:
            return f"{refer_to(ctx, stype.parameters[0])} | null", True
        if stype.defn_type.name == builder.BaseTypeName.s_tuple:
            return f"[{', '.join([refer_to(ctx, p) for p in stype.parameters])}]", False
        params = ", ".join([refer_to(ctx, p) for p in stype.parameters])
        return f"{refer_to(ctx, stype.defn_type)}<{params}>", False

    if isinstance(stype, builder.SpecTypeLiteralWrapper):
        return _emit_value(ctx, stype.value_type, stype.value), False

    if isinstance(stype, builder.SpecTypeGenericParameter):
        return stype.name, False

    assert isinstance(stype, builder.SpecTypeDefn)
    if stype.is_base:  # assume correct namespace
        if stype.name == builder.BaseTypeName.s_list:
            return "any[]", False  # TODO: generic type
        return base_name_map[builder.BaseTypeName(stype.name)], False

    if stype.namespace == ctx.namespace:
        return stype.name, False

    ctx.namespaces.add(stype.namespace)
    return f"{resolve_namespace_ref(stype.namespace)}.{stype.name}", False


def _emit_id_source(builder: builder.SpecBuilder, config: TypeScriptConfig) -> None:
    id_source_output = config.id_source_output
    if id_source_output is None:
        return
    enum_out = io.StringIO()
    enum_out.write(MODIFY_NOTICE)

    enum_out.write("export type KnownEnumsType =\n")
    enum_map = {
        builder.resolve_proper_name(string_enum): string_enum
        for string_enum in builder.emit_id_source_enums
    }
    sorted_keys = sorted(enum_map.keys())
    for key in sorted_keys:
        enum_out.write(f'  | "{key}"\n')

    enum_out.write(f"\n{MODIFY_NOTICE}")
    enum_out.write("export const ENUM_NAME_MAPS = {\n")
    for key in sorted_keys:
        string_enum = enum_map[key]
        enum_out.write(f'  "{builder.resolve_proper_name(string_enum)}": {{\n')
        for entry in string_enum.values.values():
            if entry.label is not None:
                enum_out.write(f'    "{entry.value}": "{entry.label}",\n')
        enum_out.write("  },\n")
    enum_out.write("}\n")

    enum_out.write(f"\n{MODIFY_NOTICE}")
    util.rewrite_file(id_source_output, enum_out.getvalue())
