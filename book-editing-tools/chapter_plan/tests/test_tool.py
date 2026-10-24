from pathlib import Path
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "tests"))
from chapter_plan_core import validate_plan
from fixtures import make_docx


class ChapterPlanTests(unittest.TestCase):
    def test_valid_reorder(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = make_docx(Path(tmp) / "book.docx", [
                ("h1", "Later"), ("", "02.02.2024"),
                ("h1", "Earlier"), ("", "01.02.2024"),
            ])
            result = validate_plan(str(doc), [{"title": "Chronological", "articles": [2, 1]}])
            self.assertTrue(result["valid"])
            self.assertEqual([a["title"] for a in result["parts"][0]["articles"]], ["Earlier", "Later"])

    def test_missing_duplicate_and_inversion(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = make_docx(Path(tmp) / "book.docx", [
                ("h1", "Earlier"), ("", "01.02.2024"),
                ("h1", "Later"), ("", "02.02.2024"),
                ("h1", "Third"), ("", "03.02.2024"),
            ])
            result = validate_plan(str(doc), [{"title": "One", "articles": [2, 1, 1]}])
            self.assertFalse(result["valid"])
            self.assertEqual({e["code"] for e in result["errors"]},
                             {"omitted_articles", "duplicate_article", "date_inversion"})

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            validate_plan("/missing.docx", [])


if __name__ == "__main__":
    unittest.main()
