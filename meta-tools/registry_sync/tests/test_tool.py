import json
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "registry_sync"))
if importlib.util.find_spec("yaml"):
    from tool import plan, run, sync


SPEC = """name: sample_tool
type: tool
capability: sample_capability
purpose: Sample.
status: experimental
interfaces:
  - name: stdin_json
    entrypoint: tool.py
    transport: stdin_json
operations:
  - name: sample
    available_via: [stdin_json]
    params: {}
    returns: {type: object}
side_effects: {reads: [], writes: []}
"""


@unittest.skipUnless(importlib.util.find_spec("yaml"), "PyYAML optional dependency is not installed")
class RegistrySyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "registry").mkdir()
        (self.root / "file-tools" / "sample_tool").mkdir(parents=True)
        (self.root / "file-tools" / "sample_tool" / "SKILL.yaml").write_text(SPEC)
        (self.root / "registry" / "tool_registry.json").write_text(
            json.dumps({"version": "0.1.0", "tools": [
                {"name": "legacy", "capability": "old", "path": "file-tools/legacy",
                 "custom": "keep"}]}))

    def test_plan_apply_and_preserve_unrepresented(self):
        before = (self.root / "registry" / "tool_registry.json").read_text()
        preview = sync("plan", root=self.root)
        self.assertEqual(before, (self.root / "registry" / "tool_registry.json").read_text())
        self.assertEqual(preview["changes"], [{"kind": "add", "name": "sample_tool"}])
        self.assertEqual(preview["unrepresented"], ["legacy"])
        result = sync("apply", root=self.root, expected_plan_sha256=preview["plan_sha256"])
        self.assertTrue(result["applied"])
        entries = json.loads((self.root / "registry" / "tool_registry.json").read_text())["tools"]
        self.assertEqual(entries[0]["custom"], "keep")
        self.assertEqual(entries[1]["operations"], ["sample"])
        self.assertEqual(sync("check", root=self.root)["changes"], [])

    def test_stale_plan_cannot_write(self):
        preview = plan(self.root)
        (self.root / "file-tools" / "sample_tool" / "SKILL.yaml").write_text(
            SPEC.replace("sample_capability", "changed_capability"))
        response = run({"operation": "apply", "params": {
            "root": str(self.root), "expected_plan_sha256": preview["plan_sha256"]}})
        self.assertFalse(response["success"])
        self.assertEqual(len(json.loads((self.root / "registry" / "tool_registry.json").read_text())["tools"]), 1)

    def test_update_preserves_custom_fields(self):
        path = self.root / "registry" / "tool_registry.json"
        path.write_text(json.dumps({"version": "0.1.0", "tools": [
            {"name": "sample_tool", "capability": "old", "path": "file-tools/sample_tool",
             "entrypoint": "tool.py", "transport": "stdin_json", "status": "experimental",
             "operations": ["sample"], "interfaces": [{"name": "stdin_json",
             "entrypoint": "tool.py", "transport": "stdin_json"}], "custom": "keep"}]}))
        preview = plan(self.root)
        self.assertEqual(preview["changes"][0]["fields"], ["capability"])
        sync("apply", root=self.root, expected_plan_sha256=preview["plan_sha256"])
        self.assertEqual(json.loads(path.read_text())["tools"][0]["custom"], "keep")


if __name__ == "__main__":
    unittest.main()
