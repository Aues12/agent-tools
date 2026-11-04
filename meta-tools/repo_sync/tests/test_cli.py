import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tool import cli


class CliTests(unittest.TestCase):
    def test_manifest_roots_and_human_report(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (base / "source").mkdir()
            (base / "target").mkdir()
            (base / "source" / "code.py").write_text("new\n")
            (base / "target" / "code.py").write_text("old\n")
            manifest = base / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "version": "0.2.0",
                        "source_root": "source",
                        "target_root": "target",
                        "include": ["code.py"],
                    }
                )
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = cli(["plan", "--manifest", str(manifest)])
            self.assertEqual(status, 1)
            self.assertIn("update: code.py", output.getvalue())
            self.assertIn("Plan SHA-256:", output.getvalue())
            digest = output.getvalue().split("Plan SHA-256: ")[1].splitlines()[0]
            with contextlib.redirect_stdout(io.StringIO()):
                status = cli(
                    [
                        "apply",
                        "--manifest",
                        str(manifest),
                        "--expected-plan-sha256",
                        digest,
                    ]
                )
            self.assertEqual(status, 0)
            self.assertEqual((base / "target" / "code.py").read_text(), "new\n")

    def test_json_output_and_root_override(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (base / "left").mkdir()
            (base / "right").mkdir()
            (base / "left" / "a").write_text("x")
            (base / "right" / "a").write_text("x")
            manifest = base / "manifest.json"
            manifest.write_text(json.dumps({"version": "0.2.0", "include": ["a"]}))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = cli(
                    [
                        "check",
                        "--manifest",
                        str(manifest),
                        "--source-root",
                        str(base / "left"),
                        "--target-root",
                        str(base / "right"),
                        "--json",
                    ]
                )
            self.assertEqual(status, 0)
            self.assertTrue(json.loads(output.getvalue())["result"]["valid"])


if __name__ == "__main__":
    unittest.main()
