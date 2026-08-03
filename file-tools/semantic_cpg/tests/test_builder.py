from __future__ import annotations

import sys
import unittest
from pathlib import Path
from textwrap import dedent


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import build_cpg_from_source  # noqa: E402


class SemanticCpgBuilderTests(unittest.TestCase):
    def test_merges_ast_cfg_dfg_and_call_graph(self) -> None:
        result = build_cpg_from_source(
            dedent(
                """
                def helper(value):
                    return value

                def choose(flag, a, b):
                    if flag:
                        value = helper(a)
                    else:
                        value = b
                    return value
                """
            ).strip()
            + "\n",
            path="example.py",
        )

        node_kinds = {node["kind"] for node in result["nodes"]}
        edge_kinds = {edge["kind"] for edge in result["edges"]}

        self.assertIn("function", node_kinds)
        self.assertIn("control_branch", node_kinds)
        self.assertIn("value_binding", node_kinds)
        self.assertIn("contains", edge_kinds)
        self.assertIn("calls", edge_kinds)
        self.assertIn("control_branch_true", edge_kinds)
        self.assertIn("data_returns", edge_kinds)
        self.assertIn("corresponds_to", edge_kinds)

    def test_nodes_preserve_origin_tool(self) -> None:
        result = build_cpg_from_source(
            "def main(value):\n    return value\n",
            path="origin.py",
        )

        origins = {node["origin"]["tool"] for node in result["nodes"]}

        self.assertIn("semantic_ast", origins)
        self.assertIn("semantic_cfg", origins)
        self.assertIn("semantic_dfg", origins)

    def test_call_edges_connect_function_nodes(self) -> None:
        result = build_cpg_from_source(
            dedent(
                """
                def helper(value):
                    return value

                def main(value):
                    return helper(value)
                """
            ).strip()
            + "\n",
            path="calls.py",
        )

        function_ids = {node["id"] for node in result["nodes"] if node["kind"] == "function"}
        call_edges = [edge for edge in result["edges"] if edge["kind"] == "calls"]

        self.assertEqual(len(call_edges), 1)
        self.assertIn(call_edges[0]["source"], function_ids)
        self.assertIn(call_edges[0]["target"], function_ids)

    def test_correspondence_uses_same_source_spans(self) -> None:
        result = build_cpg_from_source(
            dedent(
                """
                def main(value):
                    total = value + 1
                    return total
                """
            ).strip()
            + "\n",
            path="spans.py",
        )

        correspondence_edges = [
            edge
            for edge in result["edges"]
            if edge["kind"] == "corresponds_to"
            and edge["origin"].get("reason") == "same_source_span"
        ]

        self.assertTrue(correspondence_edges)


if __name__ == "__main__":
    unittest.main()
