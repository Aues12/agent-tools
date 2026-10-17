from pathlib import Path
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tests"))
from common import run_request
from fixtures import make_docx


class ToolTests(unittest.TestCase):
    def test_invalid_request(self):
        self.assertFalse(run_request("edition_diff", {"operation": "wrong", "params": {}})["success"])

    def test_changed_and_added(self):
        from common import edition_diff
        with tempfile.TemporaryDirectory() as tmp:
            old = make_docx(Path(tmp) / "old.docx", [("h1", "One"), ("", "old")])
            new = make_docx(Path(tmp) / "new.docx", [("h1", "One"), ("", "new"), ("h1", "Two"), ("", "text")])
            result = edition_diff(str(old), str(new))
            self.assertEqual(len(result["body_changed"]), 1)
            self.assertEqual(result["added"][0]["title"], "Two")


if __name__ == "__main__":
    unittest.main()
