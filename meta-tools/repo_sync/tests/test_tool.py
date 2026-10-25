import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tool import plan, run, sync


class RepoSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.source = base / "public"
        self.target = base / "dev"
        self.source.mkdir()
        self.target.mkdir()
        (self.source / "code").mkdir()
        (self.target / "code").mkdir()
        (self.source / "code" / "tool.py").write_text("new code\n")
        (self.target / "code" / "tool.py").write_text("old code\n")
        (self.source / "code" / "added.py").write_text("added\n")
        (self.target / "code" / "dev_only.py").write_text("dev only\n")
        (self.target / "study-packs").mkdir()
        (self.target / "study-packs" / "notes.pdf").write_bytes(b"private notes")
        self.manifest = base / "manifest.json"
        self.manifest.write_text(json.dumps({"version": "0.1.0", "include": ["code"],
                                             "exclude": ["code/**/preferences.md"]}))

    def params(self):
        return {"source_root": self.source, "target_root": self.target,
                "manifest_path": self.manifest}

    def test_plan_apply_preserves_private_and_target_only_files(self):
        report = plan(**self.params())
        self.assertEqual({item["path"] for item in report["changes"]},
                         {"code/added.py", "code/tool.py"})
        self.assertEqual(report["target_only"], ["code/dev_only.py"])
        self.assertEqual((self.target / "code" / "tool.py").read_text(), "old code\n")
        result = sync("apply", **self.params(), expected_plan_sha256=report["plan_sha256"])
        self.assertEqual(result["applied_count"], 2)
        self.assertEqual((self.target / "code" / "tool.py").read_text(), "new code\n")
        self.assertEqual((self.target / "code" / "dev_only.py").read_text(), "dev only\n")
        self.assertEqual((self.target / "study-packs" / "notes.pdf").read_bytes(), b"private notes")
        self.assertTrue(sync("check", **self.params())["valid"])

    def test_stale_source_or_target_cannot_be_applied(self):
        first = plan(**self.params())
        (self.source / "code" / "tool.py").write_text("changed again\n")
        result = run({"operation": "apply", "params": {**self.params(),
                       "expected_plan_sha256": first["plan_sha256"]}})
        self.assertFalse(result["success"])
        self.assertEqual((self.target / "code" / "tool.py").read_text(), "old code\n")
        second = plan(**self.params())
        (self.target / "code" / "tool.py").write_text("local edit\n")
        self.assertFalse(run({"operation": "apply", "params": {**self.params(),
                         "expected_plan_sha256": second["plan_sha256"]}})["success"])

    def test_protected_paths_and_traversal_are_rejected(self):
        self.manifest.write_text(json.dumps({"version": "0.1.0", "include": ["study-packs"]}))
        self.assertFalse(run({"operation": "plan", "params": self.params()})["success"])
        self.manifest.write_text(json.dumps({"version": "0.1.0", "include": ["../outside"]}))
        self.assertFalse(run({"operation": "plan", "params": self.params()})["success"])
        self.manifest.write_text(json.dumps({"version": "0.1.0", "include": ["code"]}))
        self.assertFalse(run({"operation": "plan", "params": {
            "source_root": self.source, "target_root": self.source,
            "manifest_path": self.manifest}})["success"])

    def test_symlink_and_private_skill_preferences_are_not_copied(self):
        (self.source / "code" / "link.py").symlink_to(self.source / "code" / "tool.py")
        self.assertFalse(run({"operation": "plan", "params": self.params()})["success"])
        (self.source / "code" / "link.py").unlink()
        (self.source / "skills" / "sample").mkdir(parents=True)
        (self.source / "skills" / "sample" / "SKILL.yaml").write_text("name: sample\n")
        (self.source / "skills" / "sample" / "preferences.md").write_text("private")
        self.manifest.write_text(json.dumps({"version": "0.1.0", "include": ["skills"]}))
        report = plan(**self.params())
        self.assertEqual([entry["path"] for entry in report["changes"]],
                         ["skills/sample/SKILL.yaml"])

    def test_generated_package_metadata_is_excluded(self):
        (self.source / "code" / "sample.egg-info").mkdir()
        (self.source / "code" / "sample.egg-info" / "PKG-INFO").write_text("generated")
        report = plan(**self.params())
        self.assertNotIn("code/sample.egg-info/PKG-INFO",
                         [item["path"] for item in report["changes"]])


if __name__ == "__main__":
    unittest.main()
