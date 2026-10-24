from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parent


def test_directories() -> list[Path]:
    """Find every self-contained Python test suite in the tool families."""
    return sorted(
        path
        for family in (ROOT / "file-tools", ROOT / "book-editing-tools", ROOT / "meta-tools")
        for path in family.rglob("tests")
        if any(path.glob("test*.py"))
    )


class RepositoryTestSuites(unittest.TestCase):
    def test_tool_test_suites_pass(self) -> None:
        suites = test_directories()
        self.assertTrue(suites, "No tool test suites were discovered")
        for test_dir in suites:
            with self.subTest(test_dir=test_dir.relative_to(ROOT)):
                completed = subprocess.run(
                    [sys.executable, "-m", "unittest", "discover", "-s", str(test_dir)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                    cwd=ROOT,
                )
                self.assertEqual(
                    completed.returncode,
                    0,
                    completed.stdout + completed.stderr,
                )


if __name__ == "__main__":
    unittest.main()
