import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


TOOL_PATH = Path(__file__).resolve().parents[1] / "tool.py"
spec = importlib.util.spec_from_file_location("semantic_graph_visualizer_tool", TOOL_PATH)
tool = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(tool)


def sample_cpg():
    return {
        "type": "semantic_code_property_graph",
        "language": "python",
        "path": "sample.py",
        "nodes": [
            {
                "id": "module:sample",
                "kind": "module",
                "label": "sample",
                "origin": {"tool": "semantic_ast"},
                "trace": {"path": "sample.py", "line": 1, "end_line": 3},
            },
            {
                "id": "function:sample.main",
                "kind": "function",
                "label": "main",
                "origin": {"tool": "semantic_ast"},
                "trace": {"path": "sample.py", "line": 1, "end_line": 3},
            },
            {
                "id": "function:sample.helper",
                "kind": "function",
                "label": "helper",
                "origin": {"tool": "semantic_ast"},
                "trace": {"path": "sample.py", "line": 5, "end_line": 6},
            },
            {
                "id": "cfg:function:sample.main:entry",
                "kind": "control_entry",
                "label": "entry",
                "origin": {"tool": "semantic_cfg"},
                "trace": {"path": "sample.py", "line": 1, "end_line": 1},
            },
            {
                "id": "dfg:function:sample.main:return",
                "kind": "value_return",
                "label": "return value",
                "origin": {"tool": "semantic_dfg"},
                "trace": {"path": "sample.py", "line": 2, "end_line": 2},
            },
        ],
        "edges": [
            {
                "source": "module:sample",
                "target": "function:sample.main",
                "kind": "contains",
                "origin": {"tool": "semantic_ast"},
            },
            {
                "source": "function:sample.main",
                "target": "cfg:function:sample.main:entry",
                "kind": "contains",
                "origin": {"tool": "semantic_cpg", "reason": "function_scope"},
            },
            {
                "source": "cfg:function:sample.main:entry",
                "target": "dfg:function:sample.main:return",
                "kind": "corresponds_to",
                "origin": {"tool": "semantic_cpg", "reason": "same_source_span"},
            },
            {
                "source": "function:sample.main",
                "target": "function:sample.helper",
                "kind": "calls",
                "origin": {"tool": "call_graph", "call": "helper"},
            },
        ],
        "stats": {"nodes": 5, "edges": 4},
    }


class SemanticGraphVisualizerTests(unittest.TestCase):
    def test_render_cpg_html_embeds_graph_data(self):
        html = tool.render_cpg_html(sample_cpg(), title="Sample CPG")

        self.assertIn("<!doctype html>", html)
        self.assertIn("Sample CPG", html)
        self.assertIn("function:sample.main", html)
        self.assertIn("corresponds_to", html)
        self.assertIn("call_graph", html)
        self.assertIn("visual:call_graph", html)
        self.assertIn("call_edge", html)
        self.assertIn("edgeOriginFilters", html)
        self.assertIn("originFilters", html)

    def test_render_cpg_html_respects_max_nodes(self):
        html = tool.render_cpg_html(sample_cpg(), max_nodes=2)

        self.assertIn('"truncated": true', html)
        self.assertIn('"originalNodeCount": 5', html)
        self.assertNotIn("function:sample.helper", html)

    def test_render_cpg_file_writes_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / "cpg.json"
            output_path = temp_path / "cpg.html"
            input_path.write_text(json.dumps(sample_cpg()), encoding="utf-8")

            result = tool.render_cpg_file(input_path, output_path, title="File CPG")

            self.assertEqual(result["path"], str(output_path))
            self.assertEqual(result["nodes"], 6)
            self.assertTrue(output_path.exists())
            self.assertIn("File CPG", output_path.read_text(encoding="utf-8"))

    def test_run_returns_error_for_invalid_cpg(self):
        response = tool.run(
            {
                "operation": "render_cpg_html",
                "params": {"cpg": {"type": "not_cpg"}},
            }
        )

        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["type"], "ValueError")


if __name__ == "__main__":
    unittest.main()
