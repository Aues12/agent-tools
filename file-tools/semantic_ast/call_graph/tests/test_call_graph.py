from __future__ import annotations

import sys
import unittest
from pathlib import Path
from textwrap import dedent


SEMANTIC_AST_DIR = Path(__file__).resolve().parents[2]
CALL_GRAPH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SEMANTIC_AST_DIR))
sys.path.insert(0, str(CALL_GRAPH_DIR))

from call_graph import build_call_graph  # noqa: E402
from tool import parse_source  # noqa: E402


class CallGraphTests(unittest.TestCase):
    def test_build_call_graph_extracts_local_function_edges(self) -> None:
        tree = parse_source(
            dedent(
                """
                def helper():
                    return 1

                def main():
                    print(helper())
                    return helper()
                """
            ).strip()
            + "\n",
            path="sample.py",
        )

        graph = build_call_graph(tree)

        self.assertEqual(graph["type"], "call_graph")
        self.assertEqual(graph["stats"]["functions"], 2)
        self.assertEqual(
            graph["edges"],
            [{"caller": "main", "callee": "helper", "call": "helper"}],
        )
        self.assertEqual(graph["roots"], ["main"])
        self.assertEqual(graph["leaves"], ["helper"])
        self.assertEqual(graph["tree"], "main\n└── helper")
        main_node = next(node for node in graph["nodes"] if node["id"] == "main")
        self.assertEqual(main_node["external_calls"], ["print"])

    def test_build_call_graph_resolves_self_method_calls(self) -> None:
        tree = parse_source(
            dedent(
                """
                class Runner:
                    def execute(self):
                        return self.step()

                    def step(self):
                        return 1
                """
            ).strip()
            + "\n"
        )

        graph = build_call_graph(tree)

        self.assertEqual(
            graph["edges"],
            [{"caller": "Runner.execute", "callee": "Runner.step", "call": "self.step"}],
        )
        self.assertIn("Runner.execute", graph["tree"])
        self.assertIn("Runner.step", graph["tree"])

    def test_nested_function_calls_do_not_attach_to_parent(self) -> None:
        tree = parse_source(
            dedent(
                """
                def outer():
                    def inner():
                        return helper()
                    return inner()

                def helper():
                    return 1
                """
            ).strip()
            + "\n"
        )

        graph = build_call_graph(tree)

        self.assertIn(
            {"caller": "outer", "callee": "outer.inner", "call": "inner"},
            graph["edges"],
        )
        self.assertIn(
            {"caller": "outer.inner", "callee": "helper", "call": "helper"},
            graph["edges"],
        )
        self.assertNotIn(
            {"caller": "outer", "callee": "helper", "call": "helper"},
            graph["edges"],
        )


if __name__ == "__main__":
    unittest.main()
