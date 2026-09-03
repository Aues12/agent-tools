from __future__ import annotations

import sys
import unittest
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import build_graph, run  # noqa: E402


class SemanticGraphTests(unittest.TestCase):
    def test_builds_graph_with_open_kinds(self) -> None:
        graph = build_graph(
            nodes=[
                {"id": "input", "kind": "input"},
                {"id": "render", "kind": "process_step"},
            ],
            edges=[{"source": "input", "target": "render", "kind": "feeds"}],
            require_acyclic=True,
        )

        self.assertTrue(graph["directed"])
        self.assertTrue(graph["acyclic"])
        self.assertEqual(graph["kinds"]["nodes"], ["input", "process_step"])
        self.assertEqual(graph["kinds"]["edges"], ["feeds"])

    def test_rejects_missing_endpoint(self) -> None:
        response = run(
            {
                "operation": "build_graph",
                "params": {
                    "nodes": [{"id": "input"}],
                    "edges": [{"source": "input", "target": "missing"}],
                },
            }
        )

        self.assertFalse(response["success"])
        self.assertIn("edge target does not exist", response["message"])

    def test_cycles_are_optional(self) -> None:
        nodes = [{"id": "a"}, {"id": "b"}]
        edges = [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "a"},
        ]

        graph = build_graph(nodes, edges)
        self.assertFalse(graph["acyclic"])
        self.assertEqual(graph["warnings"][0]["kind"], "cycle_detected")
        with self.assertRaisesRegex(ValueError, "directed cycle"):
            build_graph(nodes, edges, require_acyclic=True)


if __name__ == "__main__":
    unittest.main()
