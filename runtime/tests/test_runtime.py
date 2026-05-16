from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.engine import run_task
from runtime.executor import execute_tool
from runtime.planner import create_plan


class RuntimeTests(unittest.TestCase):
    def test_create_plan_normalizes_single_tool_call(self) -> None:
        plan = create_plan(
            {
                "tool": "copy_paste",
                "operation": "read_file",
                "params": {"path": "sample.txt"},
            }
        )

        self.assertEqual(plan[0]["tool"], "copy_paste")
        self.assertEqual(plan[0]["operation"], "read_file")

    def test_execute_tool_dispatches_registry_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("hello\n", encoding="utf-8")

            result = execute_tool(
                {
                    "tool": "copy_paste",
                    "operation": "read_file",
                    "params": {"path": str(path)},
                }
            )

            self.assertTrue(result["success"])
            self.assertEqual(result["result"]["content"], "hello\n")
            self.assertEqual(result["meta"]["tool"], "copy_paste")

    def test_run_task_executes_steps_in_order(self) -> None:
        task = {
            "steps": [
                {
                    "tool": "semantic_ast",
                    "operation": "parse_source",
                    "params": {"source": "VALUE = 1\n"},
                }
            ]
        }

        result = run_task(task)

        self.assertTrue(result["success"])
        self.assertEqual(result["results"][0]["result"]["body"][0]["type"], "assignment")


if __name__ == "__main__":
    unittest.main()
