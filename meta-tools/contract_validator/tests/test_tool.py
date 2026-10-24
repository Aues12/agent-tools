import json
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "contract_validator"))
if importlib.util.find_spec("yaml"):
    from tool import run, validate


SPEC = """name: sample_tool
type: tool
capability: sample
purpose: Sample.
status: experimental
interfaces:
  - name: stdin_json
    entrypoint: tool.py
    transport: stdin_json
  - name: python_api
    entrypoint: tool.py
    callables: [run]
operations:
  - name: sample
    available_via: [stdin_json, python_api]
    params:
      value: {type: string, required: true}
    returns: {type: object}
side_effects: {reads: [], writes: []}
"""


@unittest.skipUnless(importlib.util.find_spec("yaml"), "PyYAML optional dependency is not installed")
class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "sample_tool"
        self.path.mkdir()
        (self.path / "AGENTS.md").write_text("# Instructions")
        (self.path / "SKILL.yaml").write_text(SPEC)
        (self.path / "tool.py").write_text("def run(payload):\n    return payload\n")
        (self.path / "tests").mkdir()
        (self.path / "examples").mkdir()
        (self.path / "examples" / "request.json").write_text(
            json.dumps({"operation": "sample", "params": {"value": "x"}}))

    def test_valid_contract(self):
        result = validate(self.path)
        self.assertTrue(result["valid"])
        self.assertEqual(result["findings"], [])

    def test_reports_invalid_metadata_and_example(self):
        (self.path / "SKILL.yaml").write_text(SPEC.replace("[stdin_json, python_api]", "[missing]"))
        (self.path / "examples" / "request.json").write_text('{"operation":"wrong","params":{}}')
        result = validate(self.path)
        self.assertFalse(result["valid"])
        self.assertEqual({x["code"] for x in result["findings"]},
                         {"invalid_available_via", "invalid_example_operation"})

    def test_missing_files_and_no_target_execution(self):
        (self.path / "tool.py").write_text("raise RuntimeError('must not execute')\ndef run(x): return x\n")
        self.assertTrue(validate(self.path)["valid"])
        (self.path / "AGENTS.md").unlink()
        self.assertIn("missing_file", [x["code"] for x in validate(self.path)["findings"]])
        self.assertFalse(run({"operation": "validate", "params": {"path": str(self.path)}})["result"]["valid"])

    def test_malformed_types_are_findings_not_crashes(self):
        (self.path / "SKILL.yaml").write_text(
            SPEC.replace("status: experimental", "status: [experimental]")
                .replace("[stdin_json, python_api]", "[{bad: value}]"))
        result = validate(self.path)
        self.assertFalse(result["valid"])
        self.assertIn("invalid_status", [x["code"] for x in result["findings"]])
        self.assertIn("invalid_available_via", [x["code"] for x in result["findings"]])

    def test_declared_alternative_entrypoint_is_valid(self):
        (self.path / "tool.py").rename(self.path / "sample.py")
        (self.path / "SKILL.yaml").write_text(SPEC.replace("tool.py", "sample.py"))
        result = validate(self.path)
        self.assertTrue(result["valid"])
        self.assertEqual(result["warnings"], 0)
        (self.path / "sample.py").unlink()
        self.assertIn("missing_entrypoint_file", [x["code"] for x in validate(self.path)["findings"]])


if __name__ == "__main__":
    unittest.main()
