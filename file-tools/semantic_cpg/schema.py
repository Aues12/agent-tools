"""Shared schema helpers for semantic_cpg.

The structures are intentionally small and JSON-compatible. They preserve
analysis provenance while allowing AST, CFG, DFG, and call graph outputs to be
projected through one graph surface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class CPGNode:
    """One normalized Semantic CPG node with origin and source trace."""

    id: str
    kind: str
    label: str
    origin: dict[str, Any]
    trace: dict[str, Any] | None = None
    scope: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a compact JSON-compatible node dictionary."""
        return _clean_dict(
            {
                "id": self.id,
                "kind": self.kind,
                "label": self.label,
                "scope": self.scope,
                "trace": self.trace,
                "origin": self.origin,
                "properties": self.properties,
            }
        )


@dataclass(frozen=True)
class CPGEdge:
    """One normalized Semantic CPG edge with origin and optional trace."""

    source: str
    target: str
    kind: str
    origin: dict[str, Any]
    trace: dict[str, Any] | None = None
    condition: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a compact JSON-compatible edge dictionary."""
        return _clean_dict(
            {
                "source": self.source,
                "target": self.target,
                "kind": self.kind,
                "condition": self.condition,
                "trace": self.trace,
                "origin": self.origin,
                "properties": self.properties,
            }
        )


@dataclass
class CPGWarning:
    """Structured warning carried from source analyses or the merge step."""

    kind: str
    message: str
    source: str | None = None
    lineno: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a compact JSON-compatible warning dictionary."""
        return _clean_dict(
            {
                "kind": self.kind,
                "message": self.message,
                "source": self.source,
                "lineno": self.lineno,
            }
        )


def _clean_dict(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: item
        for key, item in value.items()
        if item is not None and item != [] and item != {}
    }
