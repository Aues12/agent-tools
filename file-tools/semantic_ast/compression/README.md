# compression

Compress verbose semantic AST structures into compact deterministic shapes.

## What it does

- Recursively compresses semantic AST dictionaries and lists
- Summarizes functions by name, args, calls, returns, and line range
- Summarizes classes by name, bases, methods, and line range
- Converts simple names/constants into compact scalar values
- Leaves parsing and file reads to the parent `semantic_ast` tool

## Python usage

```python
from compression import compress_ast

tree = {
    "type": "function",
    "name": "main",
    "args": {"positional_or_keyword": []},
    "body": [],
    "line": 1,
    "end_line": 2,
}

compressed = compress_ast(tree)
```

## Parent Tool Usage

The executable stdin/stdout JSON interface is exposed through
`file-tools/semantic_ast/semantic_ast.py`:

```json
{
  "operation": "compress_ast",
  "params": {
    "tree": {
      "type": "module",
      "body": []
    }
  }
}
```

## Validation

```bash
python3 -m unittest discover -s file-tools/semantic_ast/compression/tests
```
