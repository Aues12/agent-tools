# semantic_cpg

`semantic_cpg` merges deterministic code-analysis outputs into a unified
Semantic Code Property Graph.

It answers:

```text
How do AST structure, control flow, data flow, and function calls relate?
Which analysis nodes describe the same source region?
What stable graph can projection layers consume?
```

The first version intentionally avoids new type inference, symbolic execution,
runtime tracing, path feasibility proofs, and schema replacement. It preserves
the provenance of the analyses it merges.

## Pipeline

```text
Python source
  -> semantic_ast
  -> semantic_cfg
  -> semantic_dfg
  -> call_graph
  -> semantic_cpg
  -> projection layers
```

## Operations

### build_cpg

Build a CPG from a semantic AST tree and optional precomputed analyses. Missing
CFG, DFG, and call graph inputs are computed from the tree.

```json
{
  "operation": "build_cpg",
  "params": {
    "tree": {
      "type": "module",
      "language": "python",
      "body": []
    }
  }
}
```

### build_cpg_from_source

Parse source and build a CPG.

```json
{
  "operation": "build_cpg_from_source",
  "params": {
    "source": "def main(value):\n    return value\n",
    "path": "example.py"
  }
}
```

### build_cpg_from_file

Read and parse a Python file, then build a CPG.

### summarize_cpg

Convert a CPG result into compact node-kind and edge-kind summaries.

## Validation

```sh
python3 -m unittest discover -s file-tools/semantic_cpg/tests
```
