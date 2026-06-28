# semantic_cards

Build deterministic semantic cards from Python semantic AST trees.

## What it does

- Uses `semantic_ast` as the source of truth for parsing
- Preserves containment through `parent_id` and `children`
- Emits graph-friendly `contains` relations separately
- Adds deterministic `imports`, `inherits`, and local `calls` relations
- Distinguishes structural `depth` from architectural `level`
- Keeps source audit data in `trace` instead of embedding source text
- Avoids expression-level cards in the first version
- Provides compact semantic views over existing card output

## Conceptual Alignment

In Semantic Observatory terms:

- A module, class, function, block, or statement is an observation target.
- A Semantic Card is a localized interface to that target.
- `semantic_ast` provides structural localization.
- `call_graph` provides relation localization.
- `semantic_cards` provides card/interface localization.
- `semantic_view` provides presentation localization.

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

## Depth and Level

Semantic cards expose two separate vertical measurements:

- `depth`: structural nesting from the semantic AST containment tree
- `level`: architectural height from the local call graph

For function cards, `level` is the longest call-path height beneath that
function. Leaf functions have `level: 1`; callers have
`1 + max(callee levels)`.

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

### `summary_view`

Build a compact overview from an existing semantic card result.

```json
{
  "operation": "summary_view",
  "params": {
    "cards": { "... semantic_cards result ..." },
    "max_relations": 10
  }
}
```

### `tree_view`

Build a compact text containment tree from an existing semantic card result.

```json
{
  "operation": "tree_view",
  "params": {
    "cards": { "... semantic_cards result ..." },
    "max_depth": 3,
    "include_statements": false,
    "include_blocks": false
  }
}
```

### `card_view`

Build a compact view for one card from an existing semantic card result.

```json
{
  "operation": "card_view",
  "params": {
    "cards": { "... semantic_cards result ..." },
    "card_id": "function:sample.main"
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
