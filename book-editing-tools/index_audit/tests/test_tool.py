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
        self.assertFalse(run_request("index_audit", {"operation": "wrong", "params": {}})["success"])

    def test_coverage_and_alias(self):
        from common import index_audit
        with tempfile.TemporaryDirectory() as tmp:
            doc = make_docx(Path(tmp) / "book.docx", [("h1", "One"), ("", "body"), ("h1", "Adaletli-Hüküm İlkesi"), ("", "body"), ("h1", "Third"), ("h1", "Yazı Serileri Dizini"), ("", "Group"), ("", "One\t1"), ("", "11. İlke — Adaletli-Hüküm İlkesi\t2"), ("", "Unknown\t3")])
            result = index_audit(str(doc))
            self.assertEqual((result["covered_items"], result["total_items"]), (2, 3))
            self.assertEqual(len(result["alias_matches"]), 1)
            self.assertEqual(len(result["unmatched_entries"]), 1)


if __name__ == "__main__":
    unittest.main()
