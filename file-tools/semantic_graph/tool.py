"""Build and validate small LLM-authored directed semantic graphs."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping, Sequence
from typing import Any


_OPERATIONS = {"build_graph", "validate_graph"}


def build_graph(
    nodes: Sequence[Mapping[str, Any]],
    edges: Sequence[Mapping[str, Any]] | None = None,
    *,
    name: str | None = None,
    description: str | None = None,
    attributes: Mapping[str, Any] | None = None,
    require_acyclic: bool = False,
) -> dict[str, Any]:
    """Return a normalized directed graph after structural validation."""
    _require_bool(require_acyclic, "require_acyclic")
    normalized_nodes = _normalize_nodes(nodes)
    normalized_edges = _normalize_edges(edges or [], normalized_nodes)
    normalized_name = _optional_text(name, "name")
    normalized_description = _optional_text(description, "description")
    normalized_attributes = _attributes(attributes, "attributes")

    cycle = _find_cycle(normalized_nodes, normalized_edges)
    if require_acyclic and cycle:
        raise ValueError(f"graph contains a directed cycle: {' -> '.join(cycle)}")

    result: dict[str, Any] = {
        "type": "semantic_graph",
        "directed": True,
        "acyclic": cycle is None,
        "nodes": normalized_nodes,
        "edges": normalized_edges,
        "kinds": {
            "nodes": sorted({node["kind"] for node in normalized_nodes}),
            "edges": sorted({edge["kind"] for edge in normalized_edges}),
        },
        "stats": {
            "nodes": len(normalized_nodes),
            "edges": len(normalized_edges),
        },
    }
    if normalized_name is not None:
        result["name"] = normalized_name
    if normalized_description is not None:
        result["description"] = normalized_description
    if normalized_attributes:
        result["attributes"] = normalized_attributes
    if cycle:
        result["warnings"] = [{"kind": "cycle_detected", "cycle": cycle}]
    return result


def validate_graph(
    graph: Mapping[str, Any],
    *,
    require_acyclic: bool = False,
) -> dict[str, Any]:
    """Validate and normalize an existing semantic graph dictionary."""
    if not isinstance(graph, Mapping):
        raise TypeError("graph must be an object")
    graph_type = graph.get("type")
    if graph_type not in {None, "semantic_graph"}:
        raise ValueError("graph type must be semantic_graph")
    directed = graph.get("directed", True)
    if directed is not True:
        raise ValueError("semantic_graph supports directed graphs only")
    if "nodes" not in graph:
        raise ValueError("graph requires nodes")

    return build_graph(
        nodes=graph["nodes"],
        edges=graph.get("edges", []),
        name=graph.get("name"),
        description=graph.get("description"),
        attributes=graph.get("attributes"),
        require_acyclic=require_acyclic,
    )


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a semantic_graph operation using the standard envelope."""
    try:
        operation, params = _parse_request(input_data)
        if operation == "build_graph":
            result = build_graph(
                nodes=params["nodes"],
                edges=params.get("edges"),
                name=params.get("name"),
                description=params.get("description"),
                attributes=params.get("attributes"),
                require_acyclic=params.get("require_acyclic", False),
            )
            message = "Built directed semantic graph"
        else:
            result = validate_graph(
                params["graph"],
                require_acyclic=params.get("require_acyclic", False),
            )
            message = "Validated directed semantic graph"

        return {
            "success": True,
            "message": message,
            "result": result,
            "meta": {"operation": operation},
        }
    except Exception as exc:
        return _error_envelope(exc)


def main() -> None:
    """Read a JSON request from stdin and write one JSON response."""
    raw = sys.stdin.read().strip()
    if not raw:
        response = _error_envelope(ValueError("No input received"))
    else:
        try:
            response = run(json.loads(raw))
        except json.JSONDecodeError as exc:
            response = _error_envelope(ValueError(f"Invalid JSON: {exc.msg}"))

    print(json.dumps(response, ensure_ascii=False, indent=2))
    sys.exit(0 if response.get("success") is True else 2)


def _normalize_nodes(nodes: Any) -> list[dict[str, Any]]:
    if not _is_sequence(nodes):
        raise TypeError("nodes must be an array")
    if not nodes:
        raise ValueError("nodes must contain at least one node")

    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, node in enumerate(nodes):
        if not isinstance(node, Mapping):
            raise TypeError(f"nodes[{index}] must be an object")
        node_id = _required_text(node.get("id"), f"nodes[{index}].id")
        if node_id in seen:
            raise ValueError(f"duplicate node id: {node_id}")
        seen.add(node_id)

        item = {
            "id": node_id,
            "label": _optional_text(node.get("label"), f"nodes[{index}].label") or node_id,
            "kind": _optional_text(node.get("kind"), f"nodes[{index}].kind") or "node",
        }
        node_attributes = _attributes(node.get("attributes"), f"nodes[{index}].attributes")
        if node_attributes:
            item["attributes"] = node_attributes
        result.append(item)
    return result


def _normalize_edges(
    edges: Any,
    nodes: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if not _is_sequence(edges):
        raise TypeError("edges must be an array")

    node_ids = {node["id"] for node in nodes}
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for index, edge in enumerate(edges):
        if not isinstance(edge, Mapping):
            raise TypeError(f"edges[{index}] must be an object")
        source = _required_text(edge.get("source"), f"edges[{index}].source")
        target = _required_text(edge.get("target"), f"edges[{index}].target")
        kind = _optional_text(edge.get("kind"), f"edges[{index}].kind") or "relates_to"
        if source not in node_ids:
            raise ValueError(f"edge source does not exist: {source}")
        if target not in node_ids:
            raise ValueError(f"edge target does not exist: {target}")
        key = (source, target, kind)
        if key in seen:
            raise ValueError(f"duplicate edge: {source} -[{kind}]-> {target}")
        seen.add(key)

        item = {"source": source, "target": target, "kind": kind}
        label = _optional_text(edge.get("label"), f"edges[{index}].label")
        if label is not None:
            item["label"] = label
        edge_attributes = _attributes(edge.get("attributes"), f"edges[{index}].attributes")
        if edge_attributes:
            item["attributes"] = edge_attributes
        result.append(item)
    return result


def _find_cycle(
    nodes: Sequence[Mapping[str, Any]],
    edges: Sequence[Mapping[str, Any]],
) -> list[str] | None:
    adjacency = {node["id"]: [] for node in nodes}
    for edge in edges:
        adjacency[edge["source"]].append(edge["target"])

    state: dict[str, int] = {}
    stack: list[str] = []
    positions: dict[str, int] = {}

    def visit(node_id: str) -> list[str] | None:
        state[node_id] = 1
        positions[node_id] = len(stack)
        stack.append(node_id)
        for target in adjacency[node_id]:
            if state.get(target, 0) == 0:
                cycle = visit(target)
                if cycle:
                    return cycle
            elif state[target] == 1:
                return [*stack[positions[target] :], target]
        stack.pop()
        positions.pop(node_id)
        state[node_id] = 2
        return None

    for node in nodes:
        node_id = node["id"]
        if state.get(node_id, 0) == 0:
            cycle = visit(node_id)
            if cycle:
                return cycle
    return None


def _parse_request(input_data: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be an object")
    operation = input_data.get("operation")
    if operation not in _OPERATIONS:
        raise ValueError(f"unknown operation: {operation}")
    params = input_data.get("params")
    if params is None:
        params = {
            key: value
            for key, value in input_data.items()
            if key not in {"operation", "params", "meta"}
        }
    if not isinstance(params, dict):
        raise TypeError("params must be an object")
    if operation == "build_graph" and "nodes" not in params:
        raise ValueError("build_graph requires nodes")
    if operation == "validate_graph" and "graph" not in params:
        raise ValueError("validate_graph requires graph")
    return operation, params


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _required_text(value, field)


def _attributes(value: Any, field: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError(f"{field} must be an object")
    result = dict(value)
    try:
        json.dumps(result)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{field} must contain JSON-compatible values") from exc
    return result


def _require_bool(value: Any, field: str) -> None:
    if not isinstance(value, bool):
        raise TypeError(f"{field} must be a boolean")


def _is_sequence(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


def _error_envelope(exc: Exception) -> dict[str, Any]:
    message = str(exc)
    return {
        "success": False,
        "message": message,
        "error": {"type": exc.__class__.__name__, "message": message},
    }


if __name__ == "__main__":
    main()
