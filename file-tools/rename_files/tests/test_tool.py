from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import rename_files  # noqa: E402


class RenameFilesToolTests(unittest.TestCase):
    def test_dry_run_reports_planned_rename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "draft_notes.txt"
            source.write_text("hello", encoding="utf-8")

            result = rename_files(root, "draft", "final", dry_run=True)

            self.assertTrue(result["ok"])
            self.assertEqual(result["renamed_count"], 1)
            self.assertEqual(result["matched_count"], 1)
            self.assertEqual(source.exists(), True)
            self.assertEqual(
                Path(result["renamed"][0]["new_path"]),
                (root / "final_notes.txt").resolve(),
            )

    def test_apply_rename_changes_file_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "draft_notes.txt"
            source.write_text("hello", encoding="utf-8")

            result = rename_files(root, "draft", "final", dry_run=False)

            self.assertEqual(result["renamed_count"], 1)
            self.assertFalse(source.exists())
            self.assertTrue((root / "final_notes.txt").exists())

    def test_extension_filter_skips_non_matching_suffixes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "draft_notes.txt").write_text("a", encoding="utf-8")
            (root / "draft_notes.md").write_text("b", encoding="utf-8")

            result = rename_files(root, "draft", "final", extensions=[".txt"])

            self.assertEqual(result["renamed_count"], 1)
            self.assertEqual(result["skipped_count"], 1)
            self.assertEqual(
                Path(result["renamed"][0]["new_path"]),
                (root / "final_notes.txt").resolve(),
            )

    def test_targets_limit_scan_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selected = root / "draft_one.txt"
            ignored = root / "draft_two.txt"
            selected.write_text("a", encoding="utf-8")
            ignored.write_text("b", encoding="utf-8")

            result = rename_files(
                root,
                "draft",
                "final",
                targets=["draft_one.txt"],
                dry_run=True,
            )

            self.assertEqual(result["scanned_count"], 1)
            self.assertEqual(result["renamed_count"], 1)
            self.assertEqual(
                Path(result["renamed"][0]["old_path"]),
                selected.resolve(),
            )

    def test_conflict_is_reported_when_target_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "draft_notes.txt").write_text("a", encoding="utf-8")
            (root / "final_notes.txt").write_text("b", encoding="utf-8")

            result = rename_files(root, "draft", "final", dry_run=True)

            self.assertEqual(result["renamed_count"], 0)
            self.assertEqual(result["conflict_count"], 1)
            self.assertIn("target path already exists", result["conflicts"][0]["reason"])

    def test_outside_target_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = Path(tmp).parent / "outside.txt"
            outside.write_text("x", encoding="utf-8")
            try:
                with self.assertRaises(ValueError):
                    rename_files(root, "draft", "final", targets=[str(outside)])
            finally:
                if outside.exists():
                    outside.unlink()

    def test_empty_find_text_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                rename_files(tmp, "", "final")


if __name__ == "__main__":
    unittest.main()
