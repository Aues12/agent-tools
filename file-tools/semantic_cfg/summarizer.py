"""Human-readable summaries for semantic_cfg output."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def summarize_cfg(cfg: Any) -> dict[str, Any]:
    """Return compact text summaries for each function CFG."""
    if not isinstance(cfg, Mapping):
        raise TypeError("cfg must be a dictionary")
    if cfg.get("type") != "control_flow_graph":
        raise ValueError("cfg must be a semantic_cfg control_flow_graph result")

    functions = cfg.get("functions", [])
    summaries = [
        _summarize_function(function)
        for function in functions
        if isinstance(function, Mapping)
    ]
    return {
        "type": "control_flow_summary",
        "path": cfg.get("path"),
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
            source_label = _node_label(nodes, edge.get("source"))
            target_label = _node_label(nodes, edge.get("target"))
            kind = edge.get("kind") or "next"
            condition = edge.get("condition")
            suffix = f" [{condition}]" if isinstance(condition, str) and condition else ""
            lines.append(f"{source_label} -> {target_label} via {kind}{suffix}")

    if len(lines) == 2:
        lines.append("No local control flow detected.")

    return {
        "id": function.get("id"),
        "name": function.get("name"),
        "qualified_name": function.get("qualified_name"),
        "text": "\n".join(lines),
    }


def _node_label(nodes: dict[str, Mapping[str, Any]], node_id: Any) -> str:
    if isinstance(node_id, str) and node_id in nodes:
        label = nodes[node_id].get("label")
        if isinstance(label, str) and label:
            return label
    return str(node_id)
