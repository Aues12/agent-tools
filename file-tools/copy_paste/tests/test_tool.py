from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import extract_range, find_text, insert_text, read_file  # noqa: E402


class CopyPasteToolTests(unittest.TestCase):
    def test_read_file_returns_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("alpha\nbeta\n", encoding="utf-8")

            self.assertEqual(read_file(path), "alpha\nbeta\n")

    def test_find_text_returns_line_column_and_offsets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("alpha\nbeta alpha\n", encoding="utf-8")

            self.assertEqual(
                find_text(path, "alpha"),
                [
                    {
                        "line": 1,
                        "column": 1,
                        "offset": 0,
                        "end_offset": 5,
                        "text": "alpha",
                    },
                    {
                        "line": 2,
                        "column": 6,
                        "offset": 11,
                        "end_offset": 16,
                        "text": "alpha",
                    },
                ],
            )

    def test_find_text_rejects_empty_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("alpha\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                find_text(path, "")

    def test_extract_range_uses_inclusive_one_based_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("one\ntwo\nthree\n", encoding="utf-8")

            self.assertEqual(extract_range(path, 2, 3), "two\nthree\n")

    def test_extract_range_rejects_invalid_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("one\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                extract_range(path, 2, 2)

    def test_insert_text_before_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("one\nthree\n", encoding="utf-8")

            insert_text(path, 2, "two\n")

            self.assertEqual(path.read_text(encoding="utf-8"), "one\ntwo\nthree\n")

    def test_insert_text_appends_at_line_count_plus_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("one\n", encoding="utf-8")

            insert_text(path, 2, "two\n")

            self.assertEqual(path.read_text(encoding="utf-8"), "one\ntwo\n")

    def test_insert_text_rejects_invalid_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("one\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                insert_text(path, 3, "two\n")


if __name__ == "__main__":
    unittest.main()
