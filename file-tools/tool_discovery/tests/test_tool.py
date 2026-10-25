from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))
from tool import inspect_tool, list_tools, run, search_tools  # noqa: E402


class ToolDiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "registry").mkdir()
        (self.root / "file-tools" / "sample").mkdir(parents=True)
        self.entry = {
            "name": "sample", "path": "file-tools/sample", "capability": "localization",
            "status": "experimental", "entrypoint": "tool.py", "transport": "stdin_json",
            "operations": ["find_text"],
            "interfaces": [{"name": "stdin_json", "entrypoint": "tool.py", "transport": "stdin_json"}],
        }
        self._write_registry([self.entry])
        (self.root / "file-tools" / "sample" / "SKILL.yaml").write_text(
            "name: sample\ncapability: localization\nstatus: experimental\n"
            "purpose: Find text in a file.\nsearch_terms: [passages]\n"
            "interfaces:\n  - name: stdin_json\n    entrypoint: tool.py\n    transport: stdin_json\n"
            "operations:\n  - name: find_text\n    params:\n"
            "      path: {type: string, required: true}\n"
            "    returns: {type: object}\n"
            "side_effects: {reads: [files], writes: []}\n",
            encoding="utf-8",
        )

    def _write_registry(self, entries: list[dict]) -> None:
        (self.root / "registry" / "tool_registry.json").write_text(
            json.dumps({"version": "0.1.0", "tools": entries}), encoding="utf-8"
        )

    def test_list_search_and_inspect(self) -> None:
        listed = list_tools(self.root)
        self.assertEqual(listed["count"], 1)
        self.assertEqual(listed["tools"][0]["purpose"], "Find text in a file.")
        self.assertEqual(listed["tools"][0]["issues"], [])
        self.assertEqual(search_tools("FIND text", root=self.root)["count"], 1)
        self.assertEqual(search_tools("passages", root=self.root)["count"], 1)
        self.assertEqual(search_tools(capability="localization", root=self.root)["count"], 1)
        self.assertEqual(search_tools("Find the text from a file", root=self.root)["tools"][0]["matched_terms"], ["file", "find", "text"])
        self.assertEqual(search_tools("find text", capability="other", root=self.root)["count"], 0)
        self.assertEqual(search_tools("missing", root=self.root)["tools"][0]["match_ratio"], 0.0)
        detail = inspect_tool("sample", self.root)
        self.assertTrue(detail["operation_details"][0]["params"]["path"]["required"])
        self.assertEqual(detail["side_effects"]["writes"], [])

    def test_search_orders_by_coverage_without_dropping_zero_matches(self) -> None:
        other = {**self.entry, "name": "other", "path": "file-tools/other", "operations": ["rename_files"]}
        (self.root / "file-tools" / "other").mkdir()
        (self.root / "file-tools" / "other" / "SKILL.yaml").write_text(
            "name: other\ncapability: localization\nstatus: experimental\n"
            "purpose: Rename files.\n"
            "interfaces:\n  - name: stdin_json\n    entrypoint: tool.py\n    transport: stdin_json\n"
            "operations:\n  - name: rename_files\n",
            encoding="utf-8",
        )
        self._write_registry([other, self.entry])
        result = search_tools("find text", root=self.root)
        self.assertEqual([tool["name"] for tool in result["tools"]], ["sample", "other"])
        self.assertEqual([tool["match_ratio"] for tool in result["tools"]], [1.0, 0.0])
        self.assertEqual([tool["name"] for tool in search_tools("unknown", root=self.root)["tools"]], ["other", "sample"])

    def test_mismatch_and_missing_metadata_are_visible(self) -> None:
        self.entry["operations"] = ["different"]
        self._write_registry([self.entry])
        self.assertIn("registry/local operations mismatch", inspect_tool("sample", self.root)["issues"])
        (self.root / "file-tools" / "sample" / "SKILL.yaml").unlink()
        detail = inspect_tool("sample", self.root)
        self.assertEqual(detail["operation_details"], [])
        self.assertTrue(detail["issues"])

    def test_invalid_search_terms_are_reported(self) -> None:
        metadata = self.root / "file-tools" / "sample" / "SKILL.yaml"
        metadata.write_text(metadata.read_text(encoding="utf-8").replace("search_terms: [passages]", "search_terms: 7"), encoding="utf-8")
        self.assertIn("local search_terms must be a list of non-empty strings", inspect_tool("sample", self.root)["issues"])

    def test_invalid_requests_and_registry(self) -> None:
        self.assertFalse(run({"operation": "search_tools", "params": {"query": " "}}, self.root)["success"])
        self.assertFalse(run({"operation": "search_tools", "params": {"query": "and the"}}, self.root)["success"])
        self.assertFalse(run({"operation": "search_tools", "params": {}}, self.root)["success"])
        self.assertFalse(run({"operation": "inspect_tool", "params": {"name": "absent"}}, self.root)["success"])
        self.assertFalse(run({"operation": "list_tools", "params": {"extra": 1}}, self.root)["success"])
        self._write_registry([self.entry, self.entry])
        self.assertIn("duplicate", run({"operation": "list_tools"}, self.root)["message"])

    def test_rejects_registry_path_escape(self) -> None:
        self.entry["path"] = "../outside"
        self._write_registry([self.entry])
        self.assertIn("escapes", run({"operation": "list_tools"}, self.root)["message"])

    def test_cli(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL_DIR / "tool_discovery.py")],
            input=b'{"operation":"inspect_tool","params":{"name":"tool_discovery"}}',
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        detail = json.loads(completed.stdout)["result"]
        self.assertEqual(detail["name"], "tool_discovery")

    def test_real_task_phrase_retrieves_call_graph(self) -> None:
        query = "Extract functions and their call relationships from Python code"
        names = [tool["name"] for tool in search_tools(query)["tools"]]
        self.assertEqual(names[0], "call_graph")


if __name__ == "__main__":
    unittest.main()
