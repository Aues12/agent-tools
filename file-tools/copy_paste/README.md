# copy_paste

Deterministic text transfer primitives for file-based workflows.

## What it does

- Reads text files
- Finds exact text matches with line/column offsets
- Extracts inclusive 1-based line ranges
- Inserts text before a 1-based line
- Uses a canonical `operation + params` JSON envelope for CLI execution

## Entry points

- `tool.py`: core implementation and canonical entrypoint
- `copy_paste.py`: thin executable wrapper

## Supported operations

### `read_file`

```json
{
  "operation": "read_file",
  "params": {
    "path": "README.md",
    "encoding": "utf-8"
  }
}
```

### `find_text`

```json
{
  "operation": "find_text",
  "params": {
    "file": "README.md",
    "text": "tool",
    "allow_overlap": false
  }
}
```

### `extract_range`

```json
{
  "operation": "extract_range",
  "params": {
    "file": "README.md",
    "start": 1,
    "end": 5
  }
}
```

### `insert_text`

```json
{
  "operation": "insert_text",
  "params": {
    "file": "notes.txt",
    "line": 3,
    "content": "new line\n"
  }
}
```

## Python usage

```python
from tool import extract_range, find_text, insert_text, read_file

content = read_file("README.md")
matches = find_text("README.md", "tool")
snippet = extract_range("README.md", 1, 5)
insert_text("notes.txt", 3, "new line\n")
```

## Validation

Run the tool tests with:

```bash
python3 -m unittest discover -s file-tools/copy_paste/tests
```

## Notes

- Public line APIs use 1-based indexing.
- `extract_range` is inclusive on both ends.
- `insert_text` writes before the requested line, or appends at `line_count + 1`.
- This tool is intentionally narrow and does not manage registry, memory, or state.
