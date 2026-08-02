from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from textwrap import dedent


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import build_cpg_from_file, build_cpg_from_source, run, summarize_cpg  # noqa: E402


SOURCE = dedent(
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
).strip() + "\n"


class SemanticCpgToolTests(unittest.TestCase):
    def test_run_build_cpg_from_source(self) -> None:
        response = run(
            {
                "operation": "build_cpg_from_source",
                "params": {
                    "source": SOURCE,
                    "path": "example.py",
                },
            }
        )

        self.assertTrue(response["success"])
        self.assertEqual(response["result"]["type"], "semantic_code_property_graph")
        self.assertEqual(response["meta"]["normalized_operation"], "build_cpg_from_source")

    def test_build_cpg_from_file_reads_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.py"
            path.write_text("def main(value):\n    return value\n", encoding="utf-8")

            result = build_cpg_from_file(path)

            self.assertEqual(result["stats"]["functions"], 1)
            self.assertTrue(any(node["kind"] == "function" for node in result["nodes"]))

    def test_summarize_cpg_outputs_kind_counts(self) -> None:
        cpg = build_cpg_from_source(SOURCE, path="example.py")
        summary = summarize_cpg(cpg)

        text = summary["text"]
        self.assertIn("Semantic CPG", text)
        self.assertIn("control_branch", text)
        self.assertIn("data_returns", text)

    def test_invalid_operation_returns_structured_error(self) -> None:
        response = run({"operation": "missing", "params": {}})

        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["type"], "ValueError")

    def test_entrypoint_reads_stdin_json(self) -> None:
        payload = {
            "operation": "build_cpg_from_source",
            "params": {
                "source": SOURCE,
                "path": "example.py",
            },
        }

        completed = subprocess.run(
            [sys.executable, str(TOOL_DIR / "semantic_cpg.py")],
            input=json.dumps(payload).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr.decode("utf-8"))
        response = json.loads(completed.stdout.decode("utf-8"))
        self.assertTrue(response["success"])
        self.assertEqual(response["result"]["type"], "semantic_code_property_graph")


if __name__ == "__main__":
    unittest.main()
