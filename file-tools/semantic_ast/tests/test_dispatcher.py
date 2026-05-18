from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from textwrap import dedent


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import parse_source, run  # noqa: E402


class SemanticAstDispatcherTests(unittest.TestCase):
    def test_parse_source_remains_import_compatible(self) -> None:
        result = parse_source("VALUE = 1\n")

        self.assertEqual(result["type"], "module")
        self.assertEqual(result["body"][0]["type"], "assignment")

    def test_run_dispatches_ast_parsing_operation(self) -> None:
        result = run(
            {
                "operation": "ast_parsing.parse_source",
                "params": {"source": "VALUE = 1\n"},
            }
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["meta"]["subtool"], "ast_parsing")
        self.assertEqual(result["result"]["body"][0]["type"], "assignment")

    def test_run_dispatches_compression_operation(self) -> None:
        tree = parse_source("VALUE = 1\n")

        result = run({"operation": "compress_ast", "params": {"tree": tree}})

        self.assertTrue(result["success"])
        self.assertEqual(result["meta"]["subtool"], "compression")
        self.assertEqual(result["result"]["type"], "module")

    def test_run_dispatches_parse_and_call_graph_operation(self) -> None:
        source = dedent(
            """
            def helper():
                return 1

            def main():
                return helper()
            """
        ).strip() + "\n"

        result = run(
            {
                "operation": "parse_and_build_call_graph",
                "params": {"source": source},
            }
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["meta"]["subtool"], "call_graph")
        self.assertEqual(
            result["result"]["edges"],
            [{"caller": "main", "callee": "helper", "call": "helper"}],
        )

    def test_root_entrypoint_reads_stdin_json(self) -> None:
        payload = {
            "operation": "parse_source",
            "params": {
                "source": "VALUE = 1 + 2\n",
            },
        }

        completed = subprocess.run(
            [sys.executable, str(TOOL_DIR / "semantic_ast.py")],
            input=json.dumps(payload).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0)
        response = json.loads(completed.stdout.decode("utf-8"))
        self.assertTrue(response["success"])
        self.assertEqual(response["meta"]["subtool"], "ast_parsing")


if __name__ == "__main__":
    unittest.main()
