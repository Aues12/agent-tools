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
        self.assertFalse(run_request("ebook_preflight", {"operation": "wrong", "params": {}})["success"])

    def test_blank_media_and_float(self):
        from common import ebook_preflight
        with tempfile.TemporaryDirectory() as tmp:
            doc = make_docx(Path(tmp) / "book.docx", [("", "Title")] + [("", "")]*4 + [("", "Text")], media=True, floating=True)
            result = ebook_preflight(str(doc))
            self.assertEqual({x["code"] for x in result["issues"]}, {"long_blank_runs", "review_media_format", "floating_images"})


if __name__ == "__main__":
    unittest.main()
