# semantic_ast

Dispatch semantic AST parsing, compression, and call graph utilities through one
tool interface.

## What it does

- Delegates parsing to `ast_parsing`
- Delegates semantic reduction to `compression`
- Delegates local call graph extraction to `call_graph`
- Preserves 1-based `line` and inclusive `end_line` values
- Returns a JSON envelope with `success`, `message`, `result`, and `meta`
- Keeps each sub-tool deterministic and independently testable

## Entry points

- `semantic_ast.py`: executable dispatcher entry point
- `tool.py`: parent dispatcher implementation
- `ast_parsing/ast_parser.py`: parsing implementation and executable entry point

## Supported operations

### `parse_source`

Parse Python source text directly through `ast_parsing`.

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

Read and parse a Python file through `ast_parsing`.

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

### `compress_ast`

Compress an existing semantic AST tree.

```json
{
  "operation": "compress_ast",
  "params": {
    "tree": {"type": "module", "body": []}
  }
}
```

### `build_call_graph`

Build a call graph from an existing semantic AST tree.

```json
{
  "operation": "build_call_graph",
  "params": {
    "tree": {"type": "module", "body": []}
  }
}
```

### `parse_and_compress`

Parse source or a file, then compress the result.

### `parse_and_build_call_graph`

Parse source or a file, then build a call graph from the parsed result.

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
python3 -m unittest discover -s file-tools/semantic_ast/ast_parsing/tests
```

## Notes

- Use `parse_source` when the source text is already available in memory.
- Use `parse_file` when the tool should read a file from disk.
- Use `include_source: true` only when the caller explicitly needs the original source in the result.
