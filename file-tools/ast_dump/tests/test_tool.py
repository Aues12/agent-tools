from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import dump_file, dump_source, run  # noqa: E402


class AstDumpToolTests(unittest.TestCase):
    def test_dump_source_returns_ast_dump(self) -> None:
        result = dump_source("x = 1\n", path="sample.py")

        self.assertEqual(result["path"], "sample.py")
        self.assertIn("Module(", result["ast_dump"])
        self.assertIn("Assign(", result["ast_dump"])

    def test_dump_file_reads_and_parses_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.py"
            path.write_text("def main():\n    return 1\n", encoding="utf-8")

            result = dump_file(path)

            self.assertEqual(result["path"], str(path))
            self.assertIn("FunctionDef(", result["ast_dump"])

    def test_run_dump_source_operation(self) -> None:
        result = run(
            {
                "operation": "dump_source",
                "params": {"source": "value = 3\n"},
            }
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["meta"]["operation"], "dump_source")
        self.assertIn("Assign(", result["result"]["ast_dump"])

    def test_run_rejects_invalid_indent(self) -> None:
        result = run(
            {
                "operation": "dump_source",
                "params": {"source": "value = 3\n", "indent": -1},
            }
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["error"]["type"], "ValueError")

    def test_entrypoint_reads_stdin_json(self) -> None:
        payload = {
            "operation": "dump_source",
            "params": {"source": "value = 1\n"},
        }

        completed = subprocess.run(
            [sys.executable, str(TOOL_DIR / "ast_dump.py")],
            input=json.dumps(payload).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0)
        response = json.loads(completed.stdout.decode("utf-8"))
        self.assertTrue(response["success"])
        self.assertIn("Module(", response["result"]["ast_dump"])


if __name__ == "__main__":
    unittest.main()
