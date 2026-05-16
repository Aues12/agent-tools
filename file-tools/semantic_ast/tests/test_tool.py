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

from tool import parse_file, parse_source, run  # noqa: E402


class SemanticAstToolTests(unittest.TestCase):
    def test_parse_source_normalizes_structure(self) -> None:
        source = dedent(
            '''
            """Module doc"""

            import ast
            from pathlib import Path

            VALUE = 1 + 2

            def run(input_data):
                """Function doc"""
                return VALUE

            class Demo:
                pass
            '''
        ).strip() + "\n"

        result = parse_source(source, path="sample.py")

        self.assertEqual(result["type"], "module")
        self.assertEqual(result["path"], str((Path.cwd() / "sample.py").resolve()))
        self.assertEqual(result["docstring"], "Module doc")
        self.assertEqual(result["line"], 1)
        self.assertGreaterEqual(result["end_line"], 1)
        self.assertEqual(result["body"][0]["type"], "import")
        self.assertEqual(result["body"][1]["type"], "import_from")
        self.assertEqual(result["body"][2]["type"], "assignment")
        self.assertEqual(result["body"][3]["type"], "function")
        self.assertEqual(result["body"][3]["docstring"], "Function doc")
        self.assertEqual(result["body"][4]["type"], "class")
        self.assertGreaterEqual(result["stats"]["functions"], 1)
        self.assertGreaterEqual(result["stats"]["classes"], 1)

    def test_parse_source_include_source_adds_source_snippet(self) -> None:
        source = "VALUE = 1 + 2\n"

        result = parse_source(source, include_source=True)

        self.assertEqual(result["source"], source)
        self.assertEqual(result["body"][0]["source"], "VALUE = 1 + 2")

    def test_parse_file_reads_from_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.py"
            path.write_text("VALUE = 42\n", encoding="utf-8")

            result = parse_file(path)

            self.assertEqual(result["path"], str(path.resolve()))
            self.assertEqual(result["body"][0]["type"], "assignment")

    def test_run_accepts_canonical_envelope(self) -> None:
        payload = {
            "operation": "parse_source",
            "params": {
                "source": "VALUE = 1 + 2\n",
                "path": "sample.py",
            },
        }

        result = run(payload)

        self.assertTrue(result["success"])
        self.assertEqual(result["meta"]["operation"], "parse_source")
        self.assertEqual(result["result"]["body"][0]["type"], "assignment")

    def test_invalid_syntax_returns_error_envelope(self) -> None:
        result = run(
            {
                "operation": "parse_source",
                "params": {
                    "source": "def broken(:\n    pass\n",
                },
            }
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["type"], "SyntaxError")

    def test_entrypoint_reads_stdin_json(self) -> None:
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
        self.assertEqual(response["result"]["body"][0]["type"], "assignment")


if __name__ == "__main__":
    unittest.main()
