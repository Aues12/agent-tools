# semantic_observatory_pipeline

`semantic_observatory_pipeline` runs existing semantic tools and adapts their
outputs for Semantic Observatory UI.

```txt
source.py
  -> semantic_ast
  -> semantic_cards
  -> semantic_dfg
  -> semantic_cpg
  -> Flat View UI data
```

## CLI

```bash
python3 file-tools/semantic_observatory_pipeline/semantic_observatory_pipeline.py <<'JSON'
{
  "operation": "analyze_source",
  "params": {
    "path": "example.py",
    "source": "def add(a, b):\n    return a + b\n"
  }
}
JSON
```

## Python API

```python
from tool import analyze_source

result = analyze_source("def add(a, b):\n    return a + b\n", path="example.py")
```

The returned result includes canonical artifacts under `artifacts` and UI-ready
data under `ui`.

Current artifacts:

```txt
semantic_ast      structural localization
semantic_cards    card/interface localization
data_flow_graph   local value-flow localization
semantic_cpg      unified analysis graph for projection layers
```

Flat View UI data is still adapted from semantic cards and DFG enrichment. The
CPG is included for future projection layers such as flowchart, map, and
geometric views.

By default the pipeline requests Flat View friendly card generation:

```txt
include_statements = false
include_blocks     = false
```

This means generated Semantic Observatory analysis omits low-level statement
cards and control-flow block cards such as `if`, `try`, and `except_handler`.

## Role and Phase Metadata

Flat View `role` and `phase` values are currently deterministic UI metadata.

`role` is inferred from card kind and simple title keywords such as `parse`,
`build`, `validate`, `render`, and `run`.

`phase` is then derived from role through a fixed mapping:

```txt
Explorer / Locator      -> Discovery
Parser / Analyzer       -> Understanding
Transformer             -> Transformation
Builder / Renderer      -> Manifestation
```

This is not symbolic phase inference. It is a temporary presentation adapter
until deeper phase classification is introduced.
