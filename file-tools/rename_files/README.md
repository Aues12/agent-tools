# rename_files

Deterministic file-renaming primitives for directory-scoped workflows.

## What it does

- Scans a directory for files whose names contain a target substring
- Supports optional recursive search
- Supports optional extension filtering
- Supports optional target file lists
- Defaults to `dry_run: true` so plans can be reviewed before mutation
- Uses a canonical `operation + params` JSON envelope for CLI execution

## Entry points

- `tool.py`: core implementation and canonical entrypoint
- `rename_files.py`: thin executable wrapper

## Supported operation

### `rename_files`

```json
{
  "operation": "rename_files",
  "params": {
    "directory": "./tmp",
    "find_text": "draft",
    "replace_text": "final",
    "recursive": false,
    "dry_run": true
  }
}
```

Optional parameters:
- `extensions`: list of file extensions such as `[".py", ".md"]`
- `targets`: explicit list of files to consider

## Python usage

```python
from tool import rename_files

result = rename_files(
    "./tmp",
    "draft",
    "final",
    dry_run=True,
    recursive=False,
)
```

## Validation

Run the tool tests with:

```bash
python3 -m unittest discover -s file-tools/rename_files/tests
```

## Notes

- Renames stay inside the provided directory boundary.
- Conflicts are reported instead of overwritten.
- `dry_run=True` is recommended for agent workflows before applying changes.
- This tool is intentionally narrow and does not manage registry, memory, or state.
