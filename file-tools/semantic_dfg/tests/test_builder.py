from __future__ import annotations

import sys
import unittest
from pathlib import Path
from textwrap import dedent


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import build_dfg_from_source  # noqa: E402


class SemanticDfgBuilderTests(unittest.TestCase):
    def test_builds_simple_call_assignment_chain(self) -> None:
        result = build_dfg_from_source(
            dedent(
                """
                def parse_file(path):
                    text = read_file(path)
                    tree = ast.parse(text)
                    return tree
                """
            ).strip()
            + "\n",
            path="example.py",
        )

        function = result["functions"][0]
        node_ids = {node["id"] for node in function["nodes"]}
        edge_tuples = {
            (edge["source"], edge["target"], edge["kind"], edge["operation"])
            for edge in function["edges"]
        }

        self.assertIn("function:example.parse_file:parameter:path", node_ids)
        self.assertIn("function:example.parse_file:binding:text", node_ids)
        self.assertIn("function:example.parse_file:binding:tree", node_ids)
        levels = {node["id"]: node["flow_level"] for node in function["nodes"]}
        depths = {node["id"]: node["depth"] for node in function["nodes"]}
        self.assertEqual(levels["function:example.parse_file:parameter:path"], 0)
        self.assertEqual(levels["function:example.parse_file:binding:text"], 1)
        self.assertEqual(levels["function:example.parse_file:binding:tree"], 2)
        self.assertEqual(levels["function:example.parse_file:return_value:return_value"], 3)
        self.assertEqual(depths["function:example.parse_file:parameter:path"], 0)
        self.assertEqual(depths["function:example.parse_file:binding:text"], 1)
        self.assertEqual(depths["function:example.parse_file:binding:tree"], 1)
        self.assertEqual(depths["function:example.parse_file:return_value:return_value"], 1)
        self.assertIn(
            (
                "function:example.parse_file:parameter:path",
                "function:example.parse_file:binding:text",
                "depends_on",
                "read_file",
            ),
            edge_tuples,
        )
        self.assertIn(
            (
                "function:example.parse_file:binding:text",
                "function:example.parse_file:binding:tree",
                "depends_on",
                "ast.parse",
            ),
            edge_tuples,
        )
        self.assertIn("function:example.parse_file:return_value:return_value", function["returns"])

    def test_builds_expression_dependencies(self) -> None:
        result = build_dfg_from_source(
            dedent(
                """
                def calculate_total(price, quantity):
                    total = price * quantity
                    return total
                """
            ).strip()
            + "\n",
            path="calc.py",
        )

        function = result["functions"][0]
        edges = function["edges"]

        self.assertTrue(
            any(
                edge["source"] == "function:calc.calculate_total:parameter:price"
                and edge["target"] == "function:calc.calculate_total:binding:total"
                and edge["operation"] == "Mult"
                for edge in edges
            )
        )
        self.assertTrue(
            any(
                edge["source"] == "function:calc.calculate_total:parameter:quantity"
                and edge["target"] == "function:calc.calculate_total:binding:total"
                and edge["operation"] == "Mult"
                for edge in edges
            )
        )

    def test_tuple_assignment_is_supported_simply(self) -> None:
        result = build_dfg_from_source(
            dedent(
                """
                def pair(x):
                    a, b = get_pair(x)
                    return a
                """
            ).strip()
            + "\n",
            path="pairs.py",
        )

        function = result["functions"][0]
        node_ids = {node["id"] for node in function["nodes"]}

        self.assertIn("function:pairs.pair:binding:a", node_ids)
        self.assertIn("function:pairs.pair:binding:b", node_ids)
        self.assertTrue(
            any(edge["target"] == "function:pairs.pair:binding:a" for edge in function["edges"])
        )
        self.assertTrue(
            any(edge["target"] == "function:pairs.pair:binding:b" for edge in function["edges"])
        )

    def test_partial_control_flow_adds_warning_and_visits_body(self) -> None:
        result = build_dfg_from_source(
            dedent(
                """
                def choose(flag, value):
                    if flag:
                        selected = value
                    return selected
                """
            ).strip()
            + "\n",
            path="choose.py",
        )

        function = result["functions"][0]

        self.assertTrue(function["warnings"])
        self.assertTrue(
            any(node["id"] == "function:choose.choose:binding:selected" for node in function["nodes"])
        )
        depths = {node["id"]: node["depth"] for node in function["nodes"]}
        self.assertEqual(depths["function:choose.choose:binding:selected"], 2)
        self.assertEqual(depths["function:choose.choose:return_value:return_value"], 1)

    def test_literal_return_has_return_edge(self) -> None:
        result = build_dfg_from_source(
            "def main():\n    return 1\n",
            path="literal.py",
        )

        function = result["functions"][0]

        self.assertTrue(
            any(
                edge["source"] == "function:literal.main:literal:return_value_literal"
                and edge["target"] == "function:literal.main:return_value:return_value"
                and edge["kind"] == "returns"
                for edge in function["edges"]
            )
        )

    def test_simple_pipeline_flow_levels_follow_downstream_distance(self) -> None:
        result = build_dfg_from_source(
            dedent(
                """
                def calculate_total(price, quantity, tax_rate):
                    subtotal = price * quantity
                    tax = subtotal * tax_rate
                    total = subtotal + tax
                    return total
                """
            ).strip()
            + "\n",
            path="simple_pipeline.py",
        )

        function = result["functions"][0]
        levels = {node["name"]: node["flow_level"] for node in function["nodes"]}

        self.assertEqual(levels["price"], 0)
        self.assertEqual(levels["quantity"], 0)
        self.assertEqual(levels["tax_rate"], 0)
        self.assertEqual(levels["subtotal"], 1)
        self.assertEqual(levels["tax"], 2)
        self.assertEqual(levels["total"], 3)
        self.assertEqual(levels["return_value"], 4)


if __name__ == "__main__":
    unittest.main()
