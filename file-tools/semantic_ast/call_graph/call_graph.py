"""Call graph extraction from semantic AST structures.

The module is intentionally lightweight: it does not parse source code or
execute Python. It consumes the normalized dictionaries produced by
`semantic_ast.tool.parse_source()` / `parse_file()` and extracts direct function
relationships that are useful for navigation.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


SemanticNode = Mapping[str, Any]


def build_call_graph(tree: Any) -> dict[str, Any]:
    """Build a deterministic call graph from a semantic AST tree."""
    functions = _collect_functions(tree)
    local_names = _local_name_index(functions)
    edges: list[dict[str, str]] = []
    nodes: list[dict[str, Any]] = []

    for function in functions:
        calls = _extract_direct_calls(function["body"])
        local_calls: list[str] = []
        external_calls: list[str] = []

        for call in calls:
            target = _resolve_call(call, function, local_names)
            if target is None:
                external_calls.append(call)
                continue
            local_calls.append(target)
            edges.append(
                {
                    "caller": function["id"],
                    "callee": target,
                    "call": call,
                }
            )

        nodes.append(
            _clean_dict(
                {
                    "id": function["id"],
                    "name": function["name"],
                    "qualified_name": function["id"],
                    "scope": function.get("scope"),
                    "path": function.get("path"),
                    "line": function.get("line"),
                    "end_line": function.get("end_line"),
                    "calls": sorted(set(local_calls)),
                    "external_calls": sorted(set(external_calls)),
                }
            )
        )

    edges = _dedupe_edges(edges)
    levels = _compute_levels(nodes, edges)
    for node in nodes:
        node["level"] = levels.get(node["id"], 1)

    roots = _find_roots(nodes, edges)
    leaves = _find_leaves(nodes, edges)

    return {
        "type": "call_graph",
        "path": _module_path(tree),
        "nodes": nodes,
        "edges": edges,
        "roots": roots,
        "leaves": leaves,
        "tree": render_call_tree(nodes, edges, roots),
        "stats": {
            "functions": len(nodes),
            "edges": len(edges),
            "roots": len(roots),
            "leaves": len(leaves),
        },
    }


def render_call_tree(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, str]],
    roots: list[str] | None = None,
) -> str:
    """Render a compact human-readable call tree."""
    node_ids = [node["id"] for node in nodes]
    root_ids = roots if roots is not None else _find_roots(nodes, edges)
    if not root_ids:
        root_ids = node_ids

    children = _children_by_caller(edges)
    lines: list[str] = []
    for index, root in enumerate(root_ids):
        if root not in node_ids:
            continue
        _render_node(root, children, lines, prefix="", is_last=True, active=[], is_root=True)
    return "\n".join(lines)


def _collect_functions(tree: Any) -> list[dict[str, Any]]:
    functions: list[dict[str, Any]] = []
    module_path = _module_path(tree)
    _walk_for_functions(tree, functions, module_path, scope=[])
    return sorted(functions, key=lambda item: (item.get("line") or 0, item["id"]))


def _walk_for_functions(
    node: Any,
    functions: list[dict[str, Any]],
    path: str | None,
    scope: list[str],
) -> None:
    if isinstance(node, list):
        for item in node:
            _walk_for_functions(item, functions, path, scope)
        return

    if not isinstance(node, Mapping):
        return

    node_type = node.get("type")
    if node_type == "module":
        child_path = node.get("path") if isinstance(node.get("path"), str) else path
        _walk_for_functions(node.get("body", []), functions, child_path, scope)
        return

    if node_type == "class":
        name = _string_value(node.get("name"), "unknown_class")
        _walk_for_functions(node.get("body", []), functions, path, [*scope, name])
        return

    if node_type == "function":
        name = _string_value(node.get("name"), "unknown_function")
        function_scope = [*scope, name]
        functions.append(
            {
                "id": ".".join(function_scope),
                "name": name,
                "scope": ".".join(scope) if scope else None,
                "path": path,
                "line": node.get("line"),
                "end_line": node.get("end_line"),
                "body": node.get("body", []),
            }
        )
        _walk_for_functions(node.get("body", []), functions, path, function_scope)
        return

    _walk_for_functions(node.get("body", []), functions, path, scope)


def _extract_direct_calls(body: Any) -> list[str]:
    calls: list[str] = []
    _walk_for_calls(body, calls)
    return sorted(set(calls))


def _walk_for_calls(node: Any, calls: list[str]) -> None:
    if isinstance(node, list):
        for item in node:
            _walk_for_calls(item, calls)
        return

    if not isinstance(node, Mapping):
        return

    if node.get("type") in {"function", "class"}:
        return

    if node.get("type") == "call":
        call_name = _callable_name(node.get("func"))
        if call_name:
            calls.append(call_name)

    for value in node.values():
        _walk_for_calls(value, calls)


def _callable_name(node: Any) -> str | None:
    if not isinstance(node, Mapping):
        return None

    node_type = node.get("type")
    if node_type == "name":
        value = node.get("id")
        return value if isinstance(value, str) else None

    if node_type == "attribute":
        attr = node.get("attr")
        attr_name = attr if isinstance(attr, str) else None
        base = _callable_name(node.get("value"))
        if base and attr_name:
            return f"{base}.{attr_name}"
        return attr_name

    return None


def _local_name_index(functions: list[dict[str, Any]]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for function in functions:
        index.setdefault(function["name"], []).append(function["id"])
        index.setdefault(function["id"], []).append(function["id"])
    for key, values in index.items():
        index[key] = sorted(set(values))
    return index


def _resolve_call(
    call: str,
    function: dict[str, Any],
    local_names: dict[str, list[str]],
) -> str | None:
    if call in local_names and len(local_names[call]) == 1:
        return local_names[call][0]

    scope = function.get("scope")
    if call.startswith("self.") and isinstance(scope, str):
        method_name = call.split(".", 1)[1]
        candidate = f"{scope}.{method_name}"
        if candidate in local_names:
            return candidate

    if "." in call:
        parts = call.split(".")
        candidate = ".".join(parts[-2:])
        if candidate in local_names:
            return candidate

    return None


def _dedupe_edges(edges: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[tuple[str, str, str]] = set()
    result: list[dict[str, str]] = []
    for edge in sorted(edges, key=lambda item: (item["caller"], item["callee"], item["call"])):
        key = (edge["caller"], edge["callee"], edge["call"])
        if key in seen:
            continue
        seen.add(key)
        result.append(edge)
    return result


def _find_roots(nodes: list[dict[str, Any]], edges: list[dict[str, str]]) -> list[str]:
    node_ids = {node["id"] for node in nodes}
    callees = {edge["callee"] for edge in edges}
    return sorted(node_ids - callees)


def _find_leaves(nodes: list[dict[str, Any]], edges: list[dict[str, str]]) -> list[str]:
    node_ids = {node["id"] for node in nodes}
    callers = {edge["caller"] for edge in edges}
    return sorted(node_ids - callers)


def _compute_levels(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, str]],
) -> dict[str, int]:
    """Compute longest call-path height for each local call graph node."""
    node_ids = {node["id"] for node in nodes}
    children = {
        caller: [child for child in values if child in node_ids]
        for caller, values in _children_by_caller(edges).items()
        if caller in node_ids
    }
    components = _strongly_connected_components(node_ids, children)
    component_by_node = {
        node_id: component_id
        for component_id, component in enumerate(components)
        for node_id in component
    }
    component_children: dict[int, set[int]] = {
        component_id: set() for component_id in range(len(components))
    }

    for caller, callee_ids in children.items():
        caller_component = component_by_node[caller]
        for callee in callee_ids:
            callee_component = component_by_node[callee]
            if callee_component != caller_component:
                component_children[caller_component].add(callee_component)

    component_levels: dict[int, int] = {}

    def component_level(component_id: int) -> int:
        if component_id in component_levels:
            return component_levels[component_id]
        child_levels = [
            component_level(child_id)
            for child_id in sorted(component_children.get(component_id, set()))
        ]
        level = 1 + max(child_levels) if child_levels else 1
        component_levels[component_id] = level
        return level

    return {
        node_id: component_level(component_by_node[node_id])
        for node_id in sorted(node_ids)
    }


def _strongly_connected_components(
    node_ids: set[str],
    children: dict[str, list[str]],
) -> list[list[str]]:
    """Group nodes so cycles can be leveled without recursion loops."""
    index = 0
    stack: list[str] = []
    stack_members: set[str] = set()
    indexes: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[list[str]] = []

    def visit(node_id: str) -> None:
        nonlocal index
        indexes[node_id] = index
        lowlinks[node_id] = index
        index += 1
        stack.append(node_id)
        stack_members.add(node_id)

        for child_id in children.get(node_id, []):
            if child_id not in indexes:
                visit(child_id)
                lowlinks[node_id] = min(lowlinks[node_id], lowlinks[child_id])
            elif child_id in stack_members:
                lowlinks[node_id] = min(lowlinks[node_id], indexes[child_id])

        if lowlinks[node_id] != indexes[node_id]:
            return

        component: list[str] = []
        while stack:
            member = stack.pop()
            stack_members.remove(member)
            component.append(member)
            if member == node_id:
                break
        components.append(sorted(component))

    for node_id in sorted(node_ids):
        if node_id not in indexes:
            visit(node_id)

    return components


def _children_by_caller(edges: list[dict[str, str]]) -> dict[str, list[str]]:
    children: dict[str, list[str]] = {}
    for edge in edges:
        children.setdefault(edge["caller"], []).append(edge["callee"])
    for caller, values in children.items():
        children[caller] = sorted(set(values))
    return children


def _render_node(
    node_id: str,
    children: dict[str, list[str]],
    lines: list[str],
    *,
    prefix: str,
    is_last: bool,
    active: list[str],
    is_root: bool = False,
) -> None:
    connector = "" if is_root else ("└── " if is_last else "├── ")
    cycle_suffix = " (cycle)" if node_id in active else ""
    lines.append(f"{prefix}{connector}{node_id}{cycle_suffix}")
    if cycle_suffix:
        return

    next_prefix = prefix if is_root else prefix + ("    " if is_last else "│   ")
    child_ids = children.get(node_id, [])
    for index, child_id in enumerate(child_ids):
        _render_node(
            child_id,
            children,
            lines,
            prefix=next_prefix,
            is_last=index == len(child_ids) - 1,
            active=[*active, node_id],
            is_root=False,
        )


def _module_path(tree: Any) -> str | None:
    if isinstance(tree, Mapping):
        path = tree.get("path")
        return path if isinstance(path, str) else None
    return None


def _clean_dict(data: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in data.items()
        if value is not None and value != [] and value != {}
    }


def _string_value(value: Any, default: str) -> str:
    return value if isinstance(value, str) and value else default
