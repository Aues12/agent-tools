import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tool import plan, sync, verify


class GeneralTests(unittest.TestCase):
    def test_shared_and_private_files_and_verification(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            left, right = root / "left", root / "right"
            left.mkdir()
            right.mkdir()
            for folder in (left, right):
                (folder / "state").mkdir()
                (folder / "private").mkdir()
                (folder / "private" / "notes").write_text(folder.name)
            (left / "state" / "code").write_text("source\n")
            (right / "state" / "code").write_text("target\n")
            (right / "extra").write_text("extra")
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "version": "0.2.0",
                        "include": ["."],
                        "exclude": ["private"],
                        "verify_commands": [[sys.executable, "-c", "pass"]],
                    }
                )
            )
            params = dict(source_root=left, target_root=right, manifest_path=manifest)
            report = plan(**params, include_diff=True)
            self.assertFalse(report["valid"])
            self.assertEqual(report["target_only"], ["extra"])
            self.assertEqual(report["changes"][0]["path"], "state/code")
            self.assertIn("+source", report["changes"][0]["diff"])
            result = sync("apply", **params, expected_plan_sha256=report["plan_sha256"])
            self.assertFalse(result["valid"])
            self.assertEqual((right / "private" / "notes").read_text(), "right")
            self.assertTrue(verify(**params)["valid"])
            (right / "extra").unlink()
            self.assertTrue(plan(**params)["valid"])

    def test_verify_failure_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            left = root / "left"
            right = root / "right"
            left.mkdir()
            right.mkdir()
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "version": "0.2.0",
                        "include": ["."],
                        "verify_commands": [
                            [sys.executable, "-c", "raise SystemExit(2)"]
                        ],
                    }
                )
            )
            result = verify(source_root=left, target_root=right, manifest_path=manifest)
            self.assertFalse(result["valid"])
            self.assertEqual([r["returncode"] for r in result["results"]], [2, 2])


if __name__ == "__main__":
    unittest.main()
