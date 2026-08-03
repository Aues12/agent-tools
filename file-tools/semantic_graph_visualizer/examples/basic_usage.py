"""Basic semantic_graph_visualizer usage example."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


TOOL_PATH = Path(__file__).resolve().parents[1] / "tool.py"
spec = importlib.util.spec_from_file_location("semantic_graph_visualizer_tool", TOOL_PATH)
tool = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(tool)


CPG = {
    "type": "semantic_code_property_graph",
    "language": "python",
    "path": "example.py",
    "nodes": [
        {
            "id": "module:example",
            "kind": "module",
            "label": "example",
            "origin": {"tool": "semantic_ast"},
            "trace": {"path": "example.py", "line": 1, "end_line": 2},
        },
        {
            "id": "function:example.main",
            "kind": "function",
            "label": "main",
            "origin": {"tool": "semantic_ast"},
            "trace": {"path": "example.py", "line": 1, "end_line": 2},
        },
    ],
    "edges": [
        {
            "source": "module:example",
            "target": "function:example.main",
            "kind": "contains",
            "origin": {"tool": "semantic_ast"},
        }
    ],
    "stats": {"nodes": 2, "edges": 1},
}


if __name__ == "__main__":
    playground = Path("agent-playground/semantic_graph_visualizer")
    playground.mkdir(parents=True, exist_ok=True)
    input_path = playground / "example_cpg.json"
    output_path = playground / "example_cpg.html"
    input_path.write_text(json.dumps(CPG, indent=2), encoding="utf-8")
    result = tool.render_cpg_file(
        path=input_path,
        output_path=output_path,
        title="Example CPG",
    )
    print(result)
