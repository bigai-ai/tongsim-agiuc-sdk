from typing import Any, TypedDict

from .registry import PG_COMPONENT_REGISTRY


class PGQueryMeta(TypedDict, total=False):
    component: str  # 要提取的组件类型名，如 "pose"
    fields: list[str]  # 要提取的字段名列表，如 ["location"]
    subject_filter: dict[str, Any]  # subject 过滤器，如 {"subject_destroyed": False}
    as_: dict[str, str]  # 字段别名，如 {"location": "pos"}
    allow_multiple: bool  # 是否允许同类型组件重复出现


class PGQueryError(Exception):
    pass


def validate_query_meta(meta: dict) -> PGQueryMeta:
    """
    校验并标准化 PGQueryMeta。

    Raises:
        PGQueryError: 任何非法字段或格式错误
    """
    if "component" not in meta:
        raise PGQueryError("Missing 'component' field in query meta")

    component = meta["component"]
    if component not in PG_COMPONENT_REGISTRY:
        raise PGQueryError(f"Unknown component type: '{component}'")

    schema = PG_COMPONENT_REGISTRY[component]
    valid_fields = schema["fields"]
    allow_multiple = schema["allow_multiple"]

    fields = meta.get("fields", [])
    for f in fields:
        if f not in valid_fields:
            raise PGQueryError(
                f"Field '{f}' not in component '{component}' (valid: {valid_fields})"
            )

    if "as" in meta:
        alias_map = meta["as"]
        if not isinstance(alias_map, dict):
            raise PGQueryError("'as' must be a dict of field renaming")
        for src_field in alias_map:
            if src_field not in fields:
                raise PGQueryError(f"Alias field '{src_field}' must be in fields list")

    return {
        "component": component,
        "fields": fields,
        "subject_filter": meta.get("subject_filter", {}),
        "as_": meta.get("as", {}),
        "allow_multiple": allow_multiple,
    }
