# semantic_ast

Parse Python source into a compact semantic AST for navigation, analysis, and refactoring workflows.

## What it does

- Parses Python source text or files into a normalized semantic tree
- Preserves 1-based `line` and inclusive `end_line` values
- Returns a JSON envelope with `success`, `message`, `result`, and `meta`
- Keeps parsing deterministic and side-effect free

## Entry points

- `semantic_ast.py`: executable entry point
- `tool.py`: core implementation

## Supported operations

### `parse_source`

Parse Python source text directly.

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

### `parse_file`

Read and parse a Python file.

```json
{
  "operation": "parse_file",
  "params": {
    "path": "file-tools/semantic_ast/tests/test_tool.py",
    "encoding": "utf-8",
    "include_source": false
  }
}
```

## Python usage

```python
from tool import parse_source

result = parse_source(
    "def run():\n    return 1\n",
    path="example.py",
)
```

## Example output shape

```json
{
  "type": "module",
  "language": "python",
  "path": "example.py",
  "line": 1,
  "end_line": 2,
  "line_count": 2,
  "docstring": null,
  "body": [],
  "stats": {}
}
```

## Validation

Run the tool tests with:

```bash
python3 -m unittest discover -s file-tools/semantic_ast/tests
```

## Notes

- Use `parse_source` when the source text is already available in memory.
- Use `parse_file` when the tool should read a file from disk.
- Use `include_source: true` only when the caller explicitly needs the original source in the result.
