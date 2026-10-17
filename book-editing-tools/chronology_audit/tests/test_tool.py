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
        self.assertFalse(run_request("chronology_audit", {"operation": "wrong", "params": {}})["success"])

    def test_date_inversion_and_undated(self):
        from common import chronology_audit
        with tempfile.TemporaryDirectory() as tmp:
            doc = make_docx(Path(tmp) / "book.docx", [("h1", "Later"), ("", "03.02.2024"), ("h1", "Unknown"), ("", "body"), ("h1", "Earlier"), ("", "01.02.2024")])
            result = chronology_audit(str(doc))
            self.assertEqual(len(result["inversions"]), 1)
            self.assertEqual(result["undated"][0]["title"], "Unknown")


if __name__ == "__main__":
    unittest.main()
