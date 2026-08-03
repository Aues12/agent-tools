"""Shared schema helpers for semantic_cfg.

The structures are intentionally small and JSON-compatible. They describe local
function-level control flow without attempting full compiler analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CFGNode:
    """One entry, exit, statement, branch, loop, jump, return, or join point."""

    id: str
    kind: str
    label: str
    scope: str
    depth: int | None = None
    line: int | None = None
    end_line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a compact JSON-compatible node dictionary."""
        return _clean_dict(
            {
                "id": self.id,
                "kind": self.kind,
                "label": self.label,
                "scope": self.scope,
                "depth": self.depth,
                "line": self.line,
                "end_line": self.end_line,
            }
        )


@dataclass(frozen=True)
class CFGEdge:
    """One possible transfer of control between CFG nodes."""

    source: str
    target: str
    kind: str
    condition: str | None = None
    lineno: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a compact JSON-compatible edge dictionary."""
        return _clean_dict(
            {
                "source": self.source,
                "target": self.target,
                "kind": self.kind,
                "condition": self.condition,
                "lineno": self.lineno,
            }
        )


@dataclass
class CFGWarning:
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
class FunctionCFG:
    """Control-flow graph for one local Python function."""

    id: str
    name: str
    qualified_name: str
    entry: str
    exit: str
    nodes: list[CFGNode] = field(default_factory=list)
    edges: list[CFGEdge] = field(default_factory=list)
    exits: list[str] = field(default_factory=list)
    warnings: list[CFGWarning] = field(default_factory=list)
    path: str | None = None
    line: int | None = None
    end_line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-compatible function CFG."""
        return _clean_dict(
            {
                "id": self.id,
                "name": self.name,
                "qualified_name": self.qualified_name,
                "path": self.path,
                "line": self.line,
                "end_line": self.end_line,
                "entry": self.entry,
                "exit": self.exit,
                "exits": self.exits,
                "nodes": [node.to_dict() for node in self.nodes],
                "edges": [edge.to_dict() for edge in self.edges],
                "warnings": [warning.to_dict() for warning in self.warnings],
            }
        )


def _clean_dict(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: item
        for key, item in value.items()
        if item is not None and item != [] and item != {}
    }
