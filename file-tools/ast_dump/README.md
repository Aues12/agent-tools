# ast_dump

Deterministic tool that exposes canonical Python `ast.dump()` output.

## What it does

- Parses source text (`dump_source`)
- Parses a file (`dump_file`)
- Returns `ast.dump(...)` output with optional `include_attributes` and
  configurable `indent`
- Uses the standard `operation + params` stdin JSON envelope

## Entry points

- `tool.py`: core implementation and canonical entrypoint
- `ast_dump.py`: thin executable wrapper

## Supported operations

### `dump_source`

```json
{
  "operation": "dump_source",
  "params": {
    "source": "x = 1\n",
    "path": "example.py",
    "include_attributes": false,
    "indent": 2
  }
}
```

### `dump_file`

```json
{
  "operation": "dump_file",
  "params": {
    "path": "file-tools/ast_dump/examples/basic_usage.py",
    "encoding": "utf-8",
    "include_attributes": false,
    "indent": 2
  }
}
```

## Validation

```bash
python3 -m unittest discover -s file-tools/ast_dump/tests
```
