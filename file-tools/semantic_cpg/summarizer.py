"""Human-readable summaries for semantic_cpg output."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any


def summarize_cpg(cpg: Any) -> dict[str, Any]:
    """Return a compact text summary for a Semantic CPG."""
    if not isinstance(cpg, Mapping):
        raise TypeError("cpg must be a dictionary")
    if cpg.get("type") != "semantic_code_property_graph":
        raise ValueError("cpg must be a semantic_cpg semantic_code_property_graph result")

    nodes = [node for node in cpg.get("nodes", []) if isinstance(node, Mapping)]
    edges = [edge for edge in cpg.get("edges", []) if isinstance(edge, Mapping)]
    node_counts = Counter(str(node.get("kind")) for node in nodes)
    edge_counts = Counter(str(edge.get("kind")) for edge in edges)

    lines = [
        "Semantic CPG",
        "",
        f"path: {cpg.get('path')}",
        f"nodes: {len(nodes)}",
        f"edges: {len(edges)}",
        "",
        "Node kinds:",
    ]
    lines.extend(f"- {kind}: {count}" for kind, count in sorted(node_counts.items()))
    lines.append("")
    lines.append("Edge kinds:")
    lines.extend(f"- {kind}: {count}" for kind, count in sorted(edge_counts.items()))

    return {
        "type": "semantic_cpg_summary",
        "path": cpg.get("path"),
        "text": "\n".join(lines),
        "stats": {
            "nodes": len(nodes),
            "edges": len(edges),
            "node_kinds": dict(sorted(node_counts.items())),
            "edge_kinds": dict(sorted(edge_counts.items())),
        },
    }
