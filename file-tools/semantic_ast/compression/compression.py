"""Semantic AST compression utilities.

Transforms verbose semantic AST structures into compact,
LLM-friendly semantic representations.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any


SemanticNode = Mapping[str, Any]
Compressor = Callable[[SemanticNode], Any]


def compress_ast(tree: Any) -> Any:
    """Compress a semantic AST structure."""

    if isinstance(tree, list):
        return [compress_ast(item) for item in tree]

    if not isinstance(tree, Mapping):
        return tree

    node_type = tree.get("type")

    if not isinstance(node_type, str):
        return compress_generic(tree)

    compressor = COMPRESSORS.get(node_type, compress_generic)

    return compressor(tree)


# ============================================================
# Node Compressors
# ============================================================


def compress_function(node: SemanticNode) -> dict[str, Any]:

    return clean_dict(
        {
            "type": "function",
            "name": node.get("name"),
            "args": extract_argument_names(node),
            "calls": extract_calls(node),
            "returns": compress_ast(node.get("returns")),
            "line": node.get("line"),
            "end_line": node.get("end_line"),
        }
    )


def compress_class(node: SemanticNode) -> dict[str, Any]:

    return clean_dict(
        {
            "type": "class",
            "name": node.get("name"),
            "bases": extract_base_names(node),
            "methods": extract_method_names(node),
            "line": node.get("line"),
            "end_line": node.get("end_line"),
        }
    )


def compress_import(node: SemanticNode) -> dict[str, Any]:

    return {
        "type": "import",
        "modules": _extract_alias_names(node),
    }


def compress_import_from(node: SemanticNode) -> dict[str, Any]:

    return {
        "type": "import_from",
        "module": node.get("module"),
        "names": _extract_alias_names(node),
    }


def compress_assignment(node: SemanticNode) -> dict[str, Any]:

    return clean_dict(
        {
            "type": "assignment",
            "targets": compress_ast(node.get("targets")),
            "value": compress_ast(node.get("value")),
        }
    )


def compress_name(node: SemanticNode) -> str:

    return _get_str(node, "id")


def compress_constant(node: SemanticNode) -> Any:

    return node.get("value")


def compress_call(node: SemanticNode) -> dict[str, Any]:

    return clean_dict(
        {
            "type": "call",
            "function": compress_ast(node.get("func")),
            "args": compress_ast(node.get("args")),
        }
    )


def compress_return(node: SemanticNode) -> dict[str, Any]:

    return clean_dict(
        {
            "type": "return",
            "value": compress_ast(node.get("value")),
        }
    )


def compress_binop(node: SemanticNode) -> dict[str, Any]:

    return clean_dict(
        {
            "type": "binop",
            "operator": node.get("operator"),
            "left": compress_ast(node.get("left")),
            "right": compress_ast(node.get("right")),
        }
    )


# ============================================================
# Generic Compressor
# ============================================================


def compress_generic(node: SemanticNode) -> dict[str, Any]:
    """Fallback compressor."""

    result: dict[str, Any] = {"type": _get_str(node, "type")}

    important_fields = [
        "name",
        "value",
        "body",
        "args",
        "targets",
        "module",
        "line",
        "end_line",
    ]

    for field in important_fields:

        if field in node:
            result[field] = compress_ast(node[field])

    return clean_dict(result)


# ============================================================
# Extractors
# ============================================================


def extract_argument_names(node: SemanticNode) -> list[str]:

    args = _get_mapping(node.get("args"))

    if args is None:
        return []

    positional = _get_list(args, "positional_or_keyword")

    return [
        _get_str(arg, "name")
        for arg in positional
        if isinstance(arg, Mapping)
    ]


def extract_method_names(node: SemanticNode) -> list[str]:

    methods: list[str] = []

    for item in _get_list(node, "body"):

        if isinstance(item, Mapping) and item.get("type") == "function":
            methods.append(_get_str(item, "name"))

    return methods


def extract_base_names(node: SemanticNode) -> list[Any]:

    return [
        compress_ast(base)
        for base in node.get("bases", [])
    ]


def extract_calls(node: Any) -> list[str]:
    """Recursively extract function calls."""

    calls = []

    walk_for_calls(node, calls)

    return sorted(set(calls))


def walk_for_calls(node: Any, calls: list[str]) -> None:

    if isinstance(node, list):

        for item in node:
            walk_for_calls(item, calls)

        return

    if not isinstance(node, Mapping):
        return

    if node.get("type") == "call":

        func = node.get("func")

        name = extract_callable_name(func)

        if name:
            calls.append(name)

    for value in node.values():
        walk_for_calls(value, calls)


def extract_callable_name(node: Any) -> str | None:

    if not isinstance(node, Mapping):
        return None

    node_type = node.get("type")

    if node_type == "name":
        node_id = node.get("id")
        return node_id if isinstance(node_id, str) else None

    if node_type == "attribute":

        base = extract_callable_name(node.get("value"))

        attr = node.get("attr")

        if base and attr:
            return f"{base}.{attr}"

        return attr if isinstance(attr, str) else None

    return None


# ============================================================
# Utilities
# ============================================================


def clean_dict(data: Mapping[str, Any]) -> dict[str, Any]:
    """Remove empty values."""

    cleaned: dict[str, Any] = {}

    for key, value in data.items():

        if value is None:
            continue

        if value == []:
            continue

        if value == {}:
            continue

        cleaned[key] = value

    return cleaned


# ============================================================
# Compressor Registry
# ============================================================


COMPRESSORS: dict[str, Compressor] = {
    "function": compress_function,
    "class": compress_class,
    "import": compress_import,
    "import_from": compress_import_from,
    "assignment": compress_assignment,
    "name": compress_name,
    "constant": compress_constant,
    "call": compress_call,
    "return": compress_return,
    "binop": compress_binop,
}


def _extract_alias_names(node: SemanticNode) -> list[str]:
    names = _get_list(node, "names")
    result: list[str] = []
    for alias in names:
        if isinstance(alias, Mapping):
            result.append(_get_str(alias, "name"))
    return result


def _get_mapping(value: Any) -> SemanticNode | None:
    if isinstance(value, Mapping):
        return value
    return None


def _get_list(node: SemanticNode, key: str) -> list[Any]:
    value = node.get(key, [])
    if isinstance(value, list):
        return value
    return []


def _get_str(node: SemanticNode, key: str, default: str = "unknown") -> str:
    value = node.get(key, default)
    if isinstance(value, str):
        return value
    return default
