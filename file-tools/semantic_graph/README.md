# semantic_graph

`semantic_graph` builds and validates small directed graphs supplied by an LLM
or another caller. It is a graph-construction aid, not a source-code analyzer
and not a complete context-graph generator.

The broader model, persistent agent session, profiles, and protocol ideas are
being explored in the [research notebook](research/README.md). Research notes
are not yet part of the stable tool contract.

The prototype intentionally has a small contract:

```text
node: id, optional label/kind/attributes
edge: source, target, optional kind/label/attributes
```

Node and edge kinds are open strings. The tool supplies convenient defaults
but does not maintain a fixed ontology.

## Example

```json
{
  "operation": "build_graph",
  "params": {
    "name": "BookBarcode flow",
    "nodes": [
      {"id": "input", "label": "ISBN input", "kind": "input"},
      {"id": "validate", "label": "Validate ISBN", "kind": "step"},
      {"id": "render", "label": "Render barcode", "kind": "step"},
      {"id": "artifact", "label": "SVG/PDF", "kind": "output"}
    ],
    "edges": [
      {"source": "input", "target": "validate", "kind": "next"},
      {"source": "validate", "target": "render", "kind": "next"},
      {"source": "render", "target": "artifact", "kind": "produces"}
    ],
    "require_acyclic": true
  }
}
```

Run through stdin/stdout:

```bash
python3 file-tools/semantic_graph/semantic_graph.py < request.json
```

Python API:

```python
from tool import build_graph

graph = build_graph(
    nodes=[{"id": "input"}, {"id": "output"}],
    edges=[{"source": "input", "target": "output"}],
    require_acyclic=True,
)
```

Cycles are accepted by default. Set `require_acyclic=True` when the intended
result must be a DAG. The tool validates structure but does not decide whether
the graph is a semantically correct description of the subject.

## Validation

```bash
python3 -m unittest discover -s file-tools/semantic_graph/tests -v
```
