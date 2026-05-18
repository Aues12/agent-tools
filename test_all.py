from __future__ import annotations

import subprocess
import sys
import unittest


TOOL_TEST_DIRS = [
    "file-tools/copy_paste/tests",
    "file-tools/rename_files/tests",
    "file-tools/semantic_ast/tests",
    "file-tools/semantic_ast/call_graph/tests",
    "runtime/tests",
]


class RepositoryTestSuites(unittest.TestCase):
    def test_tool_test_suites_pass(self) -> None:
        for test_dir in TOOL_TEST_DIRS:
            with self.subTest(test_dir=test_dir):
                completed = subprocess.run(
                    [sys.executable, "-m", "unittest", "discover", "-s", test_dir],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    completed.returncode,
                    0,
                    completed.stdout + completed.stderr,
                )


if __name__ == "__main__":
    unittest.main()
