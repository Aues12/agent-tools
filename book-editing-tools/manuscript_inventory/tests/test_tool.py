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
        self.assertFalse(run_request("manuscript_inventory", {"operation": "wrong", "params": {}})["success"])

    def test_docx_and_markdown(self):
        from common import inventory
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            doc = make_docx(folder / "book.docx", [("h1", "First"), ("", "01.02.2024"), ("h1", "Second"), ("", "03.02.2024")])
            result = inventory(str(doc))
            self.assertEqual([x["date"] for x in result["items"]], ["2024-02-01", "2024-02-03"])
            (folder / "post.md").write_text("---\ntitle: Test\ndate: '2023-02-22T01:38:30'\n---\n# Test\n", encoding="utf-8")
            self.assertEqual(inventory(str(folder / "post.md"))["items"][0]["date"], "2023-02-22")
            page = inventory(str(doc), limit=1)
            self.assertEqual((page["count"], len(page["items"]), page["next_offset"]), (2, 1, 1))

    def test_chaptered_docx_and_approximate_date(self):
        from common import inventory
        with tempfile.TemporaryDirectory() as tmp:
            doc = make_docx(Path(tmp) / "chaptered.docx", [
                ("h1", "Part One"), ("h2", "First Essay"), ("", "01.02.2024"),
                ("h1", "Part Two"), ("h2", "Second Essay"),
                ("", "03.02.2024 [yaklaşık tarih]"),
            ])
            result = inventory(str(doc), article_level=2)
            self.assertEqual(result["count"], 2)
            self.assertEqual([x["part"] for x in result["items"]], ["Part One", "Part Two"])
            self.assertEqual([x["date_status"] for x in result["items"]], ["exact", "approximate"])
            self.assertEqual(result["items"][0]["body_characters"], len("01.02.2024"))
            self.assertEqual(inventory(str(doc))["count"], 2)


if __name__ == "__main__":
    unittest.main()
