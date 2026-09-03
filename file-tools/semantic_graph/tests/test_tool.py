from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from model import Graph  # noqa: E402
from session import GraphSession, load_graph  # noqa: E402
from tool import run  # noqa: E402


class SemanticGraphTests(unittest.TestCase):
    def test_assigns_separate_monotonic_node_and_edge_ids(self) -> None:
        graph = Graph("example")
        first = graph.add_node("First")
        second = graph.add_node("Second")
        edge = graph.add_edge(first.unique_id, second.unique_id)
        loop = graph.add_edge(second.unique_id, second.unique_id)

        self.assertEqual([first.unique_id, second.unique_id], [1, 2])
        self.assertEqual(edge.unique_id, 1)
        self.assertEqual(loop.unique_id, 2)
        self.assertEqual(graph.revision, 4)

    def test_rejects_an_edge_with_a_missing_endpoint(self) -> None:
        graph = Graph("example")
        graph.add_node("Only node")

        with self.assertRaisesRegex(ValueError, "missing node"):
            graph.add_edge(1, 2)

    def test_stdin_contract_creates_a_graph(self) -> None:
        response = run(
            {
                "operation": "create_graph",
                "params": {"graph_id": "example", "title": "Example"},
            }
        )

        self.assertTrue(response["success"])
        self.assertEqual(response["result"]["graph_id"], "example")
        self.assertEqual(response["meta"]["version"], "0.1.0")

    def test_session_uses_packets_and_persists_the_graph(self) -> None:
        session = GraphSession()
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            packet_path = directory_path / "node.json"
            packet_path.write_text(
                json.dumps({"label": "ISBN input", "kind": "input"}),
                encoding="utf-8",
            )
            graph_path = directory_path / "graph.json"

            self.assertEqual(session.execute("new --graph-id bookbarcode"), "ok graph bookbarcode")
            session.execute(f"add-node @{packet_path}")
            session.execute('add-node --label "Validate ISBN" --kind step')
            session.execute("add-edge --source 1 --target 2 --kind next")
            session.execute(f"save {graph_path}")

            restored = load_graph(graph_path)
            self.assertEqual(len(restored.nodes), 2)
            self.assertEqual(restored.edges[0].source, 1)
            self.assertEqual(restored.next_node_id, 3)


if __name__ == "__main__":
    unittest.main()
