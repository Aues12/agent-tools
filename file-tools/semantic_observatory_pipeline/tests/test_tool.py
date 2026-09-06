import copy
import hashlib
import tempfile
import importlib.util
import unittest
from pathlib import Path


TOOL_PATH = Path(__file__).resolve().parents[1] / "tool.py"
spec = importlib.util.spec_from_file_location("semantic_observatory_pipeline_tool", TOOL_PATH)
tool = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(tool)


class SemanticObservatoryPipelineTests(unittest.TestCase):
    def test_analyze_source_returns_artifacts_and_ui_cards(self):
        source = """\
def calculate_total(price, quantity):
    subtotal = price * quantity
    return subtotal
"""

        result = tool.analyze_source(source, path="sample.py")

        self.assertEqual(result["type"], "semantic_observatory_analysis")
        self.assertIn("semantic_ast", result["artifacts"])
        self.assertIn("semantic_cards", result["artifacts"])
        self.assertIn("data_flow_graph", result["artifacts"])
        self.assertIn("semantic_cpg", result["artifacts"])
        self.assertEqual(
            result["artifacts"]["semantic_cpg"]["type"],
            "semantic_code_property_graph",
        )
        self.assertGreater(result["stats"]["cpgNodes"], 0)
        self.assertGreater(result["stats"]["cpgEdges"], 0)
        cards = result["ui"]["semanticCards"]
        function_card = next(card for card in cards if card["id"] == "function:sample.calculate_total")
        self.assertEqual(function_card["kind"], "function")
        self.assertEqual(function_card["phase"], "Transformation")
        self.assertIn("dfg", function_card)
        self.assertGreaterEqual(len(function_card["dfg"]["nodes"]), 3)
        self.assertNotIn("statement", {card["kind"] for card in cards})
        self.assertNotIn("block", {card["kind"] for card in cards})

    def test_ambiguous_names_preserve_candidates_and_existing_precedence(self):
        result = tool.analyze_source("def read_and_build():\n    return 1\n")
        card = next(c for c in result["ui"]["semanticCards"] if c["kind"] == "function")
        self.assertEqual(card["role"], "Parser")
        self.assertEqual(card["phase"], "Understanding")
        record = card["classification"]
        self.assertEqual(record["targetId"], card["id"])
        self.assertTrue(record["role"]["ambiguous"])
        self.assertEqual(record["role"]["candidates"], [
            {"value": "Parser", "keywords": ["read"]},
            {"value": "Builder", "keywords": ["build"]},
        ])
        self.assertEqual(record["phase"]["dependsOn"], "role")
        self.assertEqual(record["phase"]["status"], "derived")

    def test_rename_changes_hint_without_claiming_behavioral_evidence(self):
        records = []
        for name in ("mystery", "parse_value"):
            result = tool.analyze_source(f"def {name}(value):\n    return value\n")
            card = next(c for c in result["ui"]["semanticCards"] if c["kind"] == "function")
            records.append(card["classification"]["role"])
        self.assertEqual(records[0]["status"], "fallback")
        self.assertEqual(records[0]["candidates"], [])
        self.assertEqual(records[1]["status"], "heuristic")
        self.assertEqual(records[1]["basis"], "title_substring")
        self.assertEqual(records[1]["evidence"]["title"], "parse_value")

    def test_adaptation_preserves_input_and_explains_structural_labels(self):
        cards = {"type": "semantic_cards", "cards": [
            {"id": "module:read", "kind": "module", "title": "read"},
            {"id": "statement:import", "kind": "statement", "title": "import"},
            {"id": "statement:return", "kind": "statement", "title": "return"},
        ], "relations": []}
        before = copy.deepcopy(cards)
        result = tool.adapt_for_ui(cards)
        self.assertEqual(cards, before)
        self.assertEqual([c["role"] for c in result["semanticCards"]],
                         ["Container", "Locator", "Statement"])
        for card in result["semanticCards"]:
            record = card["classification"]
            self.assertEqual(record["role"]["value"], card["role"])
            self.assertEqual(record["phase"]["value"], card["phase"])
            self.assertFalse(record["role"]["ambiguous"])

    def test_source_fingerprint_tracks_content_not_display_path(self):
        source = "# ölçüm\ndef identity(value):\n    return value\n"
        first = tool.analyze_source(source, path="original.py", display_path="shown.py")
        second = tool.analyze_source(source, path="renamed.py")
        changed = tool.analyze_source(source + "# revision\n", path="original.py")
        self.assertEqual(first["source"]["contentHash"], hashlib.sha256(source.encode("utf-8")).hexdigest())
        self.assertEqual(first["source"]["hashBasis"], "sha256:utf8-decoded-source")
        self.assertEqual(first["source"]["contentHash"], second["source"]["contentHash"])
        self.assertNotEqual(first["source"]["contentHash"], changed["source"]["contentHash"])
        self.assertEqual(first, tool.analyze_source(source, path="original.py", display_path="shown.py"))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.py"
            path.write_text(source, encoding="utf-8")
            from_file = tool.analyze_file(path)
        self.assertEqual(first["source"]["contentHash"], from_file["source"]["contentHash"])
        self.assertNotIn("classification", first["artifacts"]["semantic_cards"]["cards"][0])

    def test_file_fingerprint_uses_decoding_and_text_newline_normalization(self):
        source = "# café\ndef identity(value):\n    return value\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.py"
            path.write_bytes(source.replace("\n", "\r\n").encode("latin-1"))
            result = tool.analyze_file(path, encoding="latin-1")
        response = tool.run({"operation": "analyze_source", "params": {"source": source}})
        self.assertTrue(response["success"])
        self.assertEqual(result["source"]["contentHash"], response["result"]["source"]["contentHash"])
        self.assertIn("classification", response["result"]["ui"]["semanticCards"][0])

    def test_run_returns_error_envelope_for_invalid_source(self):
        response = tool.run(
            {
                "operation": "analyze_source",
                "params": {"source": "def broken(", "path": "broken.py"},
            }
        )

        self.assertFalse(response["success"])
        self.assertIn(response["error"]["type"], {"SyntaxError", "IndentationError"})

    def test_pipeline_generation_omits_block_cards_by_default(self):
        source = """\
def choose(value):
    if value:
        return value
    return 0
"""

        result = tool.analyze_source(source, path="branching.py")

        kinds = {card["kind"] for card in result["artifacts"]["semantic_cards"]["cards"]}
        self.assertNotIn("statement", kinds)
        self.assertNotIn("block", kinds)
        self.assertEqual(
            {card["kind"] for card in result["ui"]["semanticCards"]},
            {"module", "function"},
        )

    def test_adapt_for_ui_allows_missing_dfg(self):
        semantic_cards = {
            "type": "semantic_cards",
            "cards": [
                {
                    "id": "module:sample",
                    "kind": "module",
                    "title": "sample",
                    "depth": 0,
                    "level": 1,
                    "qualified_name": "sample",
                    "trace": {"path": "sample.py", "line": 1, "end_line": 1},
                }
            ],
            "relations": [],
        }

        ui = tool.adapt_for_ui(semantic_cards)

        self.assertEqual(ui["semanticCards"][0]["module"], "sample")
        self.assertEqual(ui["filterOptions"]["kind"], ["all", "module"])
        self.assertEqual(ui["semanticCards"][0]["relations"], [])

    def test_adapt_for_ui_matches_dfg_by_name_and_line_when_modules_differ(self):
        semantic_cards = {
            "type": "semantic_cards",
            "cards": [
                {
                    "id": "function:nested.sample.add",
                    "kind": "function",
                    "title": "add",
                    "depth": 1,
                    "level": 1,
                    "qualified_name": "nested.sample.add",
                    "trace": {"path": "/tmp/nested/sample.py", "line": 2, "end_line": 4},
                }
            ],
            "relations": [],
        }
        dfg = {
            "type": "data_flow_graph",
            "functions": [
                {
                    "id": "function:sample.add",
                    "name": "add",
                    "qualified_name": "sample.add",
                    "line": 2,
                    "nodes": [],
                    "edges": [],
                }
            ],
        }

        ui = tool.adapt_for_ui(semantic_cards, dfg)

        self.assertIn("dfg", ui["semanticCards"][0])
        self.assertEqual(ui["stats"]["dfgFunctions"], 1)


if __name__ == "__main__":
    unittest.main()
