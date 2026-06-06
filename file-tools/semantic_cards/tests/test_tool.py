from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import build_cards, cards_from_file, cards_from_source, run  # noqa: E402


SOURCE = """
import json


def helper():
    return 1


class Worker(BaseWorker):
    def run(self):
        if helper():
            return helper()
        return 0
"""


class SemanticCardsToolTests(unittest.TestCase):
    def test_cards_from_source_builds_short_ids_and_trace(self) -> None:
        result = cards_from_source(SOURCE, path="file-tools/sample.py")
        ids = {card["id"] for card in result["cards"]}

        self.assertIn("module:sample", ids)
        self.assertIn("function:sample.helper", ids)
        self.assertIn("class:sample.Worker", ids)
        self.assertIn("function:sample.Worker.run", ids)
        self.assertNotIn("file-tools", " ".join(ids))

        helper = self._card(result, "function:sample.helper")
        self.assertTrue(helper["trace"]["path"].endswith("file-tools/sample.py"))
        self.assertEqual(helper["trace"]["line"], 5)

    def test_build_cards_preserves_containment_and_relations(self) -> None:
        result = cards_from_source(SOURCE, path="file-tools/sample.py")
        module = self._card(result, "module:sample")
        worker = self._card(result, "class:sample.Worker")
        run_card = self._card(result, "function:sample.Worker.run")

        self.assertIn("class:sample.Worker", module["children"])
        self.assertIn("function:sample.Worker.run", worker["children"])
        self.assertEqual(run_card["parent_id"], "class:sample.Worker")

        relations = result["relations"]
        self.assertTrue(
            any(
                relation["kind"] == "imports" and relation["target"] == "json"
                for relation in relations
            )
        )
        self.assertTrue(
            any(
                relation["kind"] == "inherits" and relation["target"] == "BaseWorker"
                for relation in relations
            )
        )
        self.assertTrue(
            any(
                relation["kind"] == "calls"
                and relation["source_id"] == "function:sample.Worker.run"
                and relation["target_id"] == "function:sample.helper"
                for relation in relations
            )
        )

    def test_statement_cards_can_be_disabled(self) -> None:
        result = cards_from_source(
            SOURCE,
            path="file-tools/sample.py",
            include_statements=False,
        )

        self.assertFalse(
            any(card["kind"] == "statement" for card in result["cards"])
        )
        self.assertTrue(any(card["kind"] == "block" for card in result["cards"]))

    def test_cards_from_file_reads_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.py"
            path.write_text("def main():\n    return 1\n", encoding="utf-8")

            result = cards_from_file(path)

            self.assertIn(
                "function:sample.main",
                {card["id"] for card in result["cards"]},
            )

    def test_build_cards_rejects_non_module_tree(self) -> None:
        response = run(
            {
                "operation": "build_cards",
                "params": {"tree": {"type": "function"}},
            }
        )

        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["type"], "ValueError")

    def test_entrypoint_reads_stdin_json(self) -> None:
        payload = {
            "operation": "cards_from_source",
            "params": {
                "source": "def main():\n    return 1\n",
                "path": "file-tools/sample.py",
            },
        }

        completed = subprocess.run(
            [sys.executable, str(TOOL_DIR / "semantic_cards.py")],
            input=json.dumps(payload).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr.decode("utf-8"))
        response = json.loads(completed.stdout.decode("utf-8"))
        self.assertTrue(response["success"])
        self.assertIn(
            "function:sample.main",
            {card["id"] for card in response["result"]["cards"]},
        )

    def test_build_cards_from_minimal_tree(self) -> None:
        result = build_cards(
            {
                "type": "module",
                "language": "python",
                "path": "example.py",
                "line": 1,
                "end_line": 1,
                "body": [],
            }
        )

        self.assertEqual(result["root_ids"], ["module:example"])
        self.assertEqual(result["stats"]["cards"], 1)

    def _card(self, result: dict[str, object], card_id: str) -> dict[str, object]:
        cards = result["cards"]
        assert isinstance(cards, list)
        for card in cards:
            if isinstance(card, dict) and card.get("id") == card_id:
                return card
        self.fail(f"card not found: {card_id}")


if __name__ == "__main__":
    unittest.main()
