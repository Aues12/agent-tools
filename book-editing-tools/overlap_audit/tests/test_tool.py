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
        self.assertFalse(run_request("overlap_audit", {"operation": "wrong", "params": {}})["success"])

    def test_cross_collection_match(self):
        from common import overlap_audit
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a", Path(tmp) / "b"
            a.mkdir(); b.mkdir()
            (a / "one.md").write_text("# Âlem ve Bilgi\n", encoding="utf-8")
            (b / "two.md").write_text("# Alem ve Bilgi\n", encoding="utf-8")
            result = overlap_audit([str(a), str(b)])
            self.assertEqual(len(result["exact_title_overlaps"]), 1)


if __name__ == "__main__":
    unittest.main()
