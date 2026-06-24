"""Shared schema helpers for semantic_dfg.

The structures are intentionally small and JSON-compatible. They describe local
function-level value movement without attempting type or control-flow analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DFGNode:
    """One value, binding, input, output, or unknown dependency."""

    id: str
    name: str
    kind: str
    scope: str
    flow_level: int | None = None
    depth: int | None = None
    lineno: int | None = None
    col_offset: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a compact JSON-compatible node dictionary."""
        return _clean_dict(
            {
                "id": self.id,
                "name": self.name,
                "kind": self.kind,
                "scope": self.scope,
                "flow_level": self.flow_level,
                "depth": self.depth,
                "lineno": self.lineno,
                "col_offset": self.col_offset,
            }
        )


@dataclass(frozen=True)
class DFGEdge:
    """One dependency, call input, production, or return relationship."""

    source: str
    target: str
    kind: str
    operation: str | None = None
    lineno: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a compact JSON-compatible edge dictionary."""
        return _clean_dict(
            {
                "source": self.source,
                "target": self.target,
                "kind": self.kind,
                "operation": self.operation,
                "lineno": self.lineno,
            }
        )


@dataclass
class DFGWarning:
    """Structured warning for partial analysis."""

    kind: str
    message: str
    lineno: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a compact JSON-compatible warning dictionary."""
        return _clean_dict(
            {
                "kind": self.kind,
                "message": self.message,
                "lineno": self.lineno,
            }
        )


@dataclass
class FunctionDFG:
    """Data-flow graph for one local Python function."""

    id: str
    name: str
    qualified_name: str
    nodes: list[DFGNode] = field(default_factory=list)
    edges: list[DFGEdge] = field(default_factory=list)
    returns: list[str] = field(default_factory=list)
    warnings: list[DFGWarning] = field(default_factory=list)
    path: str | None = None
    line: int | None = None
    end_line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-compatible function DFG."""
        return _clean_dict(
            {
                "id": self.id,
                "name": self.name,
                "qualified_name": self.qualified_name,
                "path": self.path,
                "line": self.line,
                "end_line": self.end_line,
                "nodes": [node.to_dict() for node in self.nodes],
                "edges": [edge.to_dict() for edge in self.edges],
                "returns": self.returns,
                "warnings": [warning.to_dict() for warning in self.warnings],
            }
        )


def _clean_dict(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: item
        for key, item in value.items()
        if item is not None and item != [] and item != {}
    }
