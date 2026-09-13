"""Public API and command-line entrypoint for semantic_graph v0.1.0."""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, Mapping, Optional, Sequence

from model import FORMAT_VERSION, Edge, Graph, Node
from session import run_session


__version__ = FORMAT_VERSION
_OPERATIONS = {"create_graph", "add_node", "add_edge"}


def create_graph(
    graph_id: str,
    *,
    title: Optional[str] = None,
    attributes: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Create and serialize an empty general graph."""

    return Graph(graph_id=graph_id, title=title, attributes=dict(attributes or {})).to_dict()


def add_node(
    graph: Mapping[str, Any],
    label: str,
    *,
    kind: str = "node",
    attributes: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Add one node to a serialized graph and return the mutation result."""

    restored = Graph.from_dict(graph)
    created = restored.add_node(label, kind=kind, attributes=attributes)
    return {"graph": restored.to_dict(), "created": created.to_dict()}


def add_edge(
    graph: Mapping[str, Any],
    source: int,
    target: int,
    *,
    kind: str = "edge",
    label: Optional[str] = None,
    attributes: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Add one edge to a serialized graph and return the mutation result."""

    restored = Graph.from_dict(graph)
    created = restored.add_edge(
        source,
        target,
        kind=kind,
        label=label,
        attributes=attributes,
    )
    return {"graph": restored.to_dict(), "created": created.to_dict()}


def _dispatch(operation: str, params: Mapping[str, Any]) -> Dict[str, Any]:
    """Dispatch one validated operation to its Python function."""

    if operation == "create_graph":
        return create_graph(**params)
    if operation == "add_node":
        return add_node(**params)
    return add_edge(**params)


def run(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Execute one standard stdin/stdout JSON operation.

    Terminal users should start ``session`` instead. Stateless operations return
    the complete graph so callers can pass it into the next mutation.
    """

    try:
        if not isinstance(payload, Mapping):
            raise TypeError("payload must be an object")
        operation = payload.get("operation")
        if operation not in _OPERATIONS:
            raise ValueError(f"operation must be one of {sorted(_OPERATIONS)}")
        params = payload.get("params", {})
        if not isinstance(params, Mapping):
            raise TypeError("params must be an object")
        result = _dispatch(operation, params)
        return {
            "success": True,
            "message": f"{operation} completed",
            "result": result,
            "meta": {"tool": "semantic_graph", "version": __version__},
        }
    except (KeyError, TypeError, ValueError) as error:
        return {
            "success": False,
            "message": str(error),
            "error": {"type": type(error).__name__, "message": str(error)},
        }


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run a persistent terminal session or one stdin/stdout JSON request."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments == ["session"]:
        return run_session(show_prompt=sys.stdin.isatty())
    if arguments:
        print("usage: semantic_graph.py [session]", file=sys.stderr)
        return 2

    try:
        response = run(json.load(sys.stdin))
    except json.JSONDecodeError as error:
        response = {
            "success": False,
            "message": str(error),
            "error": {"type": type(error).__name__, "message": str(error)},
        }
    json.dump(response, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if response["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
