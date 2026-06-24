"""Human-readable summaries for semantic_dfg output."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def summarize_dfg(dfg: Any) -> dict[str, Any]:
    """Return compact text summaries for each function DFG."""
    if not isinstance(dfg, Mapping):
        raise TypeError("dfg must be a dictionary")
    if dfg.get("type") != "data_flow_graph":
        raise ValueError("dfg must be a semantic_dfg data_flow_graph result")

    functions = dfg.get("functions", [])
    summaries = [
        _summarize_function(function)
        for function in functions
        if isinstance(function, Mapping)
    ]
    return {
        "type": "data_flow_summary",
        "path": dfg.get("path"),
        "functions": summaries,
        "stats": {
            "functions": len(summaries),
        },
    }


def _summarize_function(function: Mapping[str, Any]) -> dict[str, Any]:
    name = function.get("qualified_name") or function.get("name") or "function"
    nodes = {
        node.get("id"): node
        for node in function.get("nodes", [])
        if isinstance(node, Mapping) and isinstance(node.get("id"), str)
    }
    lines = [f"Function: {name}", ""]

    edges = function.get("edges", [])
    if isinstance(edges, list):
        for edge in edges:
            if not isinstance(edge, Mapping):
                continue
            source_name = _node_name(nodes, edge.get("source"))
            target_name = _node_name(nodes, edge.get("target"))
            operation = edge.get("operation") or edge.get("kind") or "flows"
            lines.append(f"{source_name} -> {target_name} via {operation}")

    if len(lines) == 2:
        lines.append("No local data flow detected.")

    return {
        "id": function.get("id"),
        "name": function.get("name"),
        "qualified_name": function.get("qualified_name"),
        "text": "\n".join(lines),
    }


def _node_name(nodes: dict[str, Mapping[str, Any]], node_id: Any) -> str:
    if isinstance(node_id, str) and node_id in nodes:
        name = nodes[node_id].get("name")
        if isinstance(name, str) and name:
            return name
    return str(node_id)
