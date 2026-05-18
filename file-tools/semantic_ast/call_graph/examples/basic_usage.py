"""Basic call_graph usage example."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import dedent


SEMANTIC_AST_DIR = Path(__file__).resolve().parents[2]
CALL_GRAPH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SEMANTIC_AST_DIR))
sys.path.insert(0, str(CALL_GRAPH_DIR))

from call_graph import build_call_graph  # noqa: E402
from tool import parse_source  # noqa: E402


def main() -> None:
    source = dedent(
        """
        def execute_tool():
            registry = _resolve_tool()
            return _parse_response(registry)

        def _resolve_tool():
            return load_registry()

        def _parse_response(value):
            return value
        """
    ).strip() + "\n"

    graph = build_call_graph(parse_source(source, path="example.py"))
    print(graph["tree"])
    print(json.dumps(graph["edges"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
