# ast_parsing

Parse Python source into the compact semantic AST format used by
`semantic_ast`.

## Operations

- `parse_source`: parse Python source text directly.
- `parse_file`: read and parse a Python file.

Both operations preserve 1-based `line` values and inclusive `end_line` values.

## Example

```json
{
  "operation": "parse_source",
  "params": {
    "source": "def hello():\n    return 1\n",
    "path": "example.py",
    "include_source": false
  }
}
```

## Validation

```bash
python3 -m unittest discover -s file-tools/semantic_ast/ast_parsing/tests
```

## Entry Point

`ast_parser.py` contains the parser implementation and stdin JSON entrypoint.
