from __future__ import annotations

import sys
import unittest
from pathlib import Path
from textwrap import dedent


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import build_cfg_from_source  # noqa: E402


class SemanticCfgBuilderTests(unittest.TestCase):
    def test_builds_straight_line_flow(self) -> None:
        result = build_cfg_from_source(
            dedent(
                """
                def main(value):
                    total = value + 1
                    return total
                """
            ).strip()
            + "\n",
            path="simple.py",
        )

        function = result["functions"][0]
        edges = {(edge["source"], edge["target"], edge["kind"]) for edge in function["edges"]}
        labels = {node["id"]: node["label"] for node in function["nodes"]}
        by_label = {node["label"]: node["id"] for node in function["nodes"]}

        self.assertEqual(function["entry"], "function:simple.main:entry")
        self.assertEqual(function["exit"], "function:simple.main:exit")
        self.assertIn((function["entry"], by_label["assign"], "next"), edges)
        self.assertIn((by_label["assign"], by_label["return"], "next"), edges)
        self.assertIn((by_label["return"], function["exit"], "return"), edges)
        self.assertEqual(labels[function["entry"]], "entry")

    def test_builds_if_else_branches_and_join(self) -> None:
        result = build_cfg_from_source(
            dedent(
                """
                def choose(flag):
                    if flag:
                        value = 1
                    else:
                        value = 0
                    return value
                """
            ).strip()
            + "\n",
            path="choose.py",
        )

        function = result["functions"][0]
        nodes = {node["label"]: node["id"] for node in function["nodes"]}
        edges = {(edge["source"], edge["target"], edge["kind"], edge.get("condition")) for edge in function["edges"]}

        self.assertIn("if flag", nodes)
        self.assertIn("if join", nodes)
        self.assertTrue(any(edge[0] == nodes["if flag"] and edge[2] == "branch_true" for edge in edges))
        self.assertTrue(any(edge[0] == nodes["if flag"] and edge[2] == "branch_false" for edge in edges))
        self.assertTrue(any(edge[0] == nodes["if join"] and edge[2] == "next" for edge in edges))

    def test_early_return_does_not_fall_through_to_following_statement(self) -> None:
        result = build_cfg_from_source(
            dedent(
                """
                def guard(flag):
                    if flag:
                        return 1
                    value = 0
                    return value
                """
            ).strip()
            + "\n",
            path="guard.py",
        )

        function = result["functions"][0]
        nodes = function["nodes"]
        branch_return = next(node for node in nodes if node["kind"] == "return" and node["line"] == 3)
        assign = next(node for node in nodes if node["label"] == "assign")

        self.assertFalse(
            any(
                edge["source"] == branch_return["id"]
                and edge["target"] == assign["id"]
                for edge in function["edges"]
            )
        )

    def test_fully_terminal_if_else_does_not_fall_through(self) -> None:
        result = build_cfg_from_source(
            dedent(
                """
                def choose(flag):
                    if flag:
                        return 1
                    else:
                        return 0
                    value = 2
                    return value
                """
            ).strip()
            + "\n",
            path="terminal.py",
        )

        function = result["functions"][0]
        assign = next(node for node in function["nodes"] if node["label"] == "assign")

        self.assertFalse(
            any(edge["target"] == assign["id"] for edge in function["edges"])
        )

    def test_loop_has_body_exit_and_back_edges(self) -> None:
        result = build_cfg_from_source(
            dedent(
                """
                def count(items):
                    total = 0
                    for item in items:
                        total += item
                    return total
                """
            ).strip()
            + "\n",
            path="loops.py",
        )

        function = result["functions"][0]
        loop = next(node for node in function["nodes"] if node["kind"] == "loop")
        kinds_from_loop = {edge["kind"] for edge in function["edges"] if edge["source"] == loop["id"]}
        kinds_to_loop = {edge["kind"] for edge in function["edges"] if edge["target"] == loop["id"]}

        self.assertIn("loop_body", kinds_from_loop)
        self.assertIn("loop_exit", kinds_from_loop)
        self.assertIn("loop_back", kinds_to_loop)

    def test_break_and_continue_target_loop_control_nodes(self) -> None:
        result = build_cfg_from_source(
            dedent(
                """
                def scan(items):
                    for item in items:
                        if item is None:
                            continue
                        if item == "stop":
                            break
                    return item
                """
            ).strip()
            + "\n",
            path="scan.py",
        )

        function = result["functions"][0]
        edge_kinds = {edge["kind"] for edge in function["edges"]}

        self.assertIn("continue", edge_kinds)
        self.assertIn("break", edge_kinds)

    def test_try_adds_partial_warning_and_exception_edge(self) -> None:
        result = build_cfg_from_source(
            dedent(
                """
                def parse(value):
                    try:
                        parsed = int(value)
                    except ValueError:
                        parsed = 0
                    return parsed
                """
            ).strip()
            + "\n",
            path="parse.py",
        )

        function = result["functions"][0]
        edge_kinds = {edge["kind"] for edge in function["edges"]}

        self.assertTrue(function["warnings"])
        self.assertIn("exception", edge_kinds)


if __name__ == "__main__":
    unittest.main()
