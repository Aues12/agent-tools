from __future__ import annotations

import sys
import unittest
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from semantic_view import (  # noqa: E402
    build_card_index,
    build_relation_index,
    card_view,
    summary_view,
    tree_view,
)


def fixture_cards() -> dict[str, object]:
    return {
        "type": "semantic_cards",
        "language": "python",
        "path": "sample.py",
        "root_ids": ["module:sample"],
        "cards": [
            {
                "id": "module:sample",
                "kind": "module",
                "title": "sample",
                "depth": 0,
                "level": 2,
                "children": [
                    "function:sample.main",
                    "function:sample.helper",
                    "class:sample.Example",
                ],
                "trace": {"path": "sample.py", "line": 1, "end_line": 20},
            },
            {
                "id": "function:sample.main",
                "kind": "function",
                "title": "main",
                "depth": 1,
                "level": 2,
                "parent_id": "module:sample",
                "children": ["statement:sample.main@L3"],
                "detail": {"docstring": "Run the sample workflow."},
                "trace": {"path": "sample.py", "line": 2, "end_line": 4},
            },
            {
                "id": "statement:sample.main@L3",
                "kind": "statement",
                "title": "return",
                "depth": 2,
                "level": 1,
                "parent_id": "function:sample.main",
                "children": [],
                "detail": {"summary": "returns helper()"},
                "trace": {"path": "sample.py", "line": 3, "end_line": 3},
            },
            {
                "id": "function:sample.helper",
                "kind": "function",
                "title": "helper",
                "depth": 1,
                "level": 1,
                "parent_id": "module:sample",
                "children": [],
                "trace": {"path": "sample.py", "line": 6, "end_line": 7},
            },
            {
                "id": "class:sample.Example",
                "kind": "class",
                "title": "Example",
                "depth": 1,
                "level": 2,
                "parent_id": "module:sample",
                "children": ["function:sample.Example.run"],
                "trace": {"path": "sample.py", "line": 10, "end_line": 14},
            },
            {
                "id": "function:sample.Example.run",
                "kind": "function",
                "title": "run",
                "depth": 2,
                "level": 2,
                "parent_id": "class:sample.Example",
                "children": [],
                "trace": {"path": "sample.py", "line": 11, "end_line": 12},
            },
        ],
        "relations": [
            {
                "kind": "contains",
                "source_id": "module:sample",
                "target_id": "function:sample.main",
            },
            {
                "kind": "calls",
                "source_id": "function:sample.main",
                "target_id": "function:sample.helper",
            },
            {
                "kind": "calls",
                "source_id": "function:sample.Example.run",
                "target_id": "function:sample.helper",
            },
            {
                "kind": "imports",
                "source_id": "module:sample",
                "target": "json",
            },
        ],
    }


class SemanticViewTests(unittest.TestCase):
    def test_summary_view_counts_and_caps_relations(self) -> None:
        view = summary_view(fixture_cards(), max_relations=2)

        self.assertEqual(view["type"], "semantic_summary_view")
        self.assertEqual(view["source"], "sample.py")
        self.assertEqual(view["counts"]["module"], 1)
        self.assertEqual(view["counts"]["function"], 3)
        self.assertEqual(view["counts"]["statement"], 1)
        self.assertEqual(
            view["top_level"],
            [
                "function:main",
                "function:helper",
                "class:Example",
            ],
        )
        self.assertEqual(len(view["relations"]), 2)

    def test_tree_view_hides_statements_by_default(self) -> None:
        view = tree_view(fixture_cards())

        self.assertEqual(
            view["tree"],
            "\n".join(
                [
                    "module: sample",
                    "+- function: main",
                    "+- function: helper",
                    "`- class: Example",
                    "   `- function: run",
                ]
            ),
        )

    def test_tree_view_can_include_statements(self) -> None:
        view = tree_view(fixture_cards(), include_statements=True)

        self.assertIn("statement: return", view["tree"])

    def test_tree_view_respects_max_depth(self) -> None:
        view = tree_view(fixture_cards(), max_depth=1, include_statements=True)

        self.assertNotIn("statement: return", view["tree"])
        self.assertNotIn("function: run", view["tree"])

    def test_card_view_returns_compact_card_details(self) -> None:
        view = card_view(fixture_cards(), "function:sample.main")

        self.assertEqual(view["type"], "semantic_card_view")
        self.assertEqual(view["kind"], "function")
        self.assertEqual(view["title"], "main")
        self.assertEqual(view["depth"], 1)
        self.assertEqual(view["level"], 2)
        self.assertEqual(view["location"], "L2-L4")
        self.assertEqual(view["summary"], "Run the sample workflow.")
        self.assertEqual(
            view["relations"]["outgoing"]["calls"],
            ["function:sample.helper"],
        )

    def test_card_view_uses_neutral_summary_fallback(self) -> None:
        view = card_view(fixture_cards(), "function:sample.helper")

        self.assertEqual(view["summary"], "No summary available.")

    def test_card_view_missing_card_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            card_view(fixture_cards(), "function:sample.missing")

    def test_missing_cards_input_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            summary_view({"type": "semantic_cards"})

    def test_empty_card_collection(self) -> None:
        view = summary_view({"cards": [], "relations": []})

        self.assertEqual(view["counts"], {})
        self.assertEqual(view["top_level"], [])
        self.assertEqual(view["relations"], [])

    def test_indexes_group_cards_and_relations(self) -> None:
        cards = fixture_cards()
        card_index = build_card_index(cards)
        relation_index = build_relation_index(cards)

        self.assertIn("module:sample", card_index)
        self.assertEqual(
            relation_index["incoming"]["function:sample.helper"]["calls"],
            ["function:sample.Example.run", "function:sample.main"],
        )


if __name__ == "__main__":
    unittest.main()
