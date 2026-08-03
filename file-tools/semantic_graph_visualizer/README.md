# semantic_graph_visualizer

`semantic_graph_visualizer` renders Semantic CPG JSON into a self-contained
interactive HTML debug view.

It is intended as a small graph microscope for understanding what the current
CPG contains. It does not perform semantic analysis and does not replace
projection tools.

## Operations

### render_cpg_html

Return an HTML string for a provided CPG object.

```json
{
  "operation": "render_cpg_html",
  "params": {
    "cpg": {
      "type": "semantic_code_property_graph",
      "nodes": [],
      "edges": [],
      "stats": {}
    },
    "title": "Example CPG",
    "max_nodes": 200
  }
}
```

### render_cpg_file

Read a CPG JSON file and write a local HTML file.

```json
{
  "operation": "render_cpg_file",
  "params": {
    "path": "agent-playground/example_cpg.json",
    "output_path": "agent-playground/example_cpg.html",
    "title": "Example CPG",
    "max_nodes": 200
  }
}
```

## HTML Features

* origin filters
* edge-kind filters
* edge-origin filters, including `call_graph` when calls are present
* deterministic compact source-order lane layout by node origin and source line
* virtual `call_graph` lane nodes derived from `calls` edges
* selected node and edge details
* visible node and edge counts

The `call_graph` lane is a visualization convenience. It does not add new CPG
analysis nodes; it turns visible `calls` edges into small inspectable nodes so
call relationships do not disappear inside the AST lane.

The source-order layout is compact: it preserves source line labels but skips
empty lines that do not have visible graph nodes.

## Validation

```sh
python3 -m unittest discover -s file-tools/semantic_graph_visualizer/tests
```
