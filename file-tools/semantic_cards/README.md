# semantic_cards

Build deterministic semantic cards from Python semantic AST trees.

## What it does

- Uses `semantic_ast` as the source of truth for parsing
- Preserves containment through `parent_id` and `children`
- Emits graph-friendly `contains` relations separately
- Adds deterministic `imports`, `inherits`, and local `calls` relations
- Keeps source audit data in `trace` instead of embedding source text
- Avoids expression-level cards in the first version

## ID Standard

Card IDs use the short semantic form:

```text
{kind}:{qualified_name}
```

Examples:

```text
module:semantic_ast.tool
function:semantic_ast.tool.run
class:semantic_ast.parser.Parser
statement:semantic_ast.tool.run@L74
```

Source location lives in `trace`:

```json
{
  "trace": {
    "path": "file-tools/semantic_ast/tool.py",
    "line": 62,
    "end_line": 91
  }
}
```

## Entry points

- `tool.py`: core implementation and canonical import target
- `semantic_cards.py`: executable stdin/stdout JSON entrypoint

## Supported operations

### `cards_from_source`

```json
{
  "operation": "cards_from_source",
  "params": {
    "source": "def helper():\n    return 1\n",
    "path": "example.py",
    "include_statements": true
  }
}
```

### `cards_from_file`

```json
{
  "operation": "cards_from_file",
  "params": {
    "path": "file-tools/semantic_ast/tool.py",
    "encoding": "utf-8",
    "include_statements": true
  }
}
```

### `build_cards`

```json
{
  "operation": "build_cards",
  "params": {
    "tree": {
      "type": "module",
      "language": "python",
      "path": "example.py",
      "line": 1,
      "end_line": 1,
      "body": []
    }
  }
}
```

## Output shape

```json
{
  "type": "semantic_cards",
  "language": "python",
  "path": "example.py",
  "root_ids": ["module:example"],
  "cards": [],
  "relations": [],
  "stats": {}
}
```

## Validation

```bash
python3 -m unittest discover -s file-tools/semantic_cards/tests
```
