# Using tools

The registry lists actual entrypoints, operations, and interfaces:
[tool_registry.json](registry/tool_registry.json). Use the selected tool's
local contract and example for its parameters; no need to read every tool
description. Most tools accept a JSON request on stdin and return a JSON
response on stdout:

```json
{"operation":"read_file","params":{"path":"README.md"}}
```

```bash
printf '%s' '{"operation":"read_file","params":{"path":"README.md"}}' | python3 file-tools/copy_paste/copy_paste.py
```

A typical response has `success`, `message`, `result`, and `meta`; errors have
`success: false` and an `error` object. Use explicit `params` and inspect the
local README for operation-specific fields.

## v0.1 graph path

```bash
python3 file-tools/semantic_graph/semantic_graph.py session
```

The session accepts `new`, `add-node`, `add-edge`, `show`, and `save`. See the
[tool README](file-tools/semantic_graph/README.md) for the command contract.
The [viewer](visual-tools/semantic_graph_viewer/README.md) accepts saved
v0.1.0 graph JSON and includes its own runnable example.

## Other tested tools

`semantic_ast`, `semantic_cards`, CFG, DFG, CPG, and the observatory pipeline
have separate entrypoints and output formats; the registry and local READMEs
specify each interface and its limits. The registry currently labels them
`experimental`, which does not prevent using their tested operations. It means
their APIs have no declared cross-version stability promise. The legacy
writing timeline under `experiments/` uses a different JSON schema and does
not consume v0.1.0 `semantic_graph` files.

Before relying on a tool, run its local tests where present:

```bash
python3 -m unittest discover -s file-tools/semantic_graph/tests
```
