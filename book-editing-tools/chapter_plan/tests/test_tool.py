from pathlib import Path
import json
import subprocess
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

    def test_flat_plan_without_parts(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = make_docx(Path(tmp) / "book.docx", [
                ("h1", "Later"), ("", "02.02.2024"),
                ("h1", "Earlier"), ("", "01.02.2024"),
            ])
            result = validate_plan(str(doc), articles=[2, 1])
            self.assertTrue(result["valid"])
            self.assertEqual(result["layout"], "flat")
            self.assertEqual(result["parts"], [])
            self.assertEqual([a["ordinal"] for a in result["articles"]], [2, 1])
            self.assertFalse(validate_plan(str(doc), articles=[1])["valid"])

    def test_exactly_one_layout_required(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            validate_plan("/missing.docx")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            validate_plan("/missing.docx", parts=[], articles=[])

    def test_flat_stdin_json_interface(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc = make_docx(Path(tmp) / "book.docx", [
                ("h1", "First"), ("", "01.01.2024"),
            ])
            request = {"operation": "chapter_plan", "params": {"path": str(doc), "articles": [1]}}
            completed = subprocess.run([sys.executable, str(BASE / "chapter_plan" / "tool.py")],
                                       input=json.dumps(request), text=True, capture_output=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            response = json.loads(completed.stdout)
            self.assertEqual(response["result"]["layout"], "flat")
            self.assertTrue(response["result"]["valid"])

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
