# USE_TOOL.md

This document is the quick entrypoint for using tools in this repository.

## 1) Standard Tool Contract

Tools in this repo use a common CLI contract:

- Input: JSON from `stdin`
- Output: JSON to `stdout`
- Envelope:
  - `operation`: string
  - `params`: object

Canonical request shape:

```json
{
  "operation": "some_operation",
  "params": {
    "key": "value"
  }
}
```

Canonical response shape:

```json
{
  "success": true,
  "message": "Human-readable summary",
  "result": {},
  "meta": {}
}
```

Error shape:

```json
{
  "success": false,
  "message": "Error message",
  "error": {
    "type": "ValueError",
    "message": "Detailed reason"
  }
}
```

## 2) How To Run Any Tool

From repo root:

```bash
printf '%s' '{"operation":"op_name","params":{"k":"v"}}' | python3 file-tools/<tool_name>/<entrypoint>.py
```

Find entrypoint from:
- `registry/tool_registry.json`
- tool-local `README.md`

## 3) Discover Available Tools

Check registry:

```bash
cat registry/tool_registry.json
```

Each tool entry includes:
- `name`
- `capability`
- `path`
- `entrypoint`
- `operations`
- `interfaces`

## 4) Quick Examples

### `copy_paste` — read file

```bash
printf '%s' '{
  "operation":"read_file",
  "params":{"path":"README.md"}
}' | python3 file-tools/copy_paste/copy_paste.py
```

### `semantic_ast` — parse and call graph

```bash
printf '%s' '{
  "operation":"parse_and_build_call_graph",
  "params":{"path":"file-tools/semantic_ast/tool.py"}
}' | python3 file-tools/semantic_ast/semantic_ast.py
```

### `semantic_cards` — cards and relations

```bash
printf '%s' '{
  "operation":"cards_from_file",
  "params":{"path":"file-tools/semantic_ast/tool.py"}
}' | python3 file-tools/semantic_cards/semantic_cards.py
```

### `ast_dump` — canonical Python ast.dump

```bash
printf '%s' '{
  "operation":"dump_file",
  "params":{"path":"file-tools/ast_dump/tool.py","include_attributes":false,"indent":2}
}' | python3 file-tools/ast_dump/ast_dump.py
```

## 5) Validation Pattern

Before relying on a tool, run its tests:

```bash
python3 -m unittest discover -s file-tools/<tool_name>/tests
```

## 6) Tool Selection (Practical)

- Use `copy_paste` for deterministic text operations (read/find/extract/insert).
- Use `semantic_ast` for semantic JSON tree, compression, and call-graph analysis.
- Use `semantic_cards` for semantic navigation cards and separate relations.
- Use `ast_dump` for Python-native AST fidelity (`ast.dump`) and low-level AST checks.

## 7) Notes

- Prefer explicit `params`; avoid hidden defaults in agent workflows.
- Keep operations narrow and deterministic.
- If adding a new tool, update `registry/tool_registry.json` and include tests/examples.
