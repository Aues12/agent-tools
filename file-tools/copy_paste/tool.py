"""Deterministic text transfer primitives for files.

Public line-number APIs use 1-based indexing. Ranges are inclusive.

Transport contract:
- `run()` accepts a JSON-like dict with `operation` and `params`
- `main()` reads stdin JSON and prints stdout JSON
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


_OPS = {"read_file", "find_text", "extract_range", "insert_text"}


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a copy_paste operation from a structured request payload."""
    try:
        operation, params = _parse_request(input_data)
        result, message = _dispatch(operation, params)
        return {
            "success": True,
            "message": message,
            "result": result,
            "meta": {"operation": operation},
        }
    except Exception as exc:
        return _error_envelope(exc)


def main() -> None:
    """Read stdin JSON, execute an operation, and print stdout JSON."""
    raw = sys.stdin.read().strip()
    if not raw:
        response = _error_envelope(ValueError("No input received"))
        print(json.dumps(response, ensure_ascii=False, indent=2))
        sys.exit(2)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        response = _error_envelope(ValueError(f"Invalid JSON: {exc.msg}"))
        print(json.dumps(response, ensure_ascii=False, indent=2))
        sys.exit(2)

    response = run(payload)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    sys.exit(_exit_code(response))


def read_file(path: str | Path, encoding: str = "utf-8") -> str:
    """Read a text file and return its contents."""
    return _as_path(path).read_text(encoding=encoding)


def find_text(
    file: str | Path,
    text: str,
    encoding: str = "utf-8",
    allow_overlap: bool = False,
) -> list[dict[str, Any]]:
    """Find exact text occurrences in a file.

    Returns dictionaries containing 1-based `line` and `column` values plus the
    0-based character `offset`. Empty search text is rejected because it creates
    ambiguous infinite matches.
    """
    if text == "":
        raise ValueError("text must not be empty")

    content = read_file(file, encoding=encoding)
    matches: list[dict[str, Any]] = []
    start = 0
    step = 1 if allow_overlap else len(text)

    while True:
        offset = content.find(text, start)
        if offset == -1:
            break
        line, column = _line_column(content, offset)
        matches.append(
            {
                "line": line,
                "column": column,
                "offset": offset,
                "end_offset": offset + len(text),
                "text": text,
            }
        )
        start = offset + step

    return matches


def extract_range(
    file: str | Path,
    start: int,
    end: int,
    encoding: str = "utf-8",
) -> str:
    """Extract an inclusive 1-based line range from a text file."""
    content = read_file(file, encoding=encoding)
    lines = content.splitlines(keepends=True)
    _validate_line_range(start, end, len(lines))
    return "".join(lines[start - 1 : end])


def insert_text(
    file: str | Path,
    line: int,
    content: str,
    encoding: str = "utf-8",
) -> None:
    """Insert text before a 1-based line, or append at line_count + 1."""
    if not isinstance(content, str):
        raise TypeError("content must be a string")

    path = _as_path(file)
    original = path.read_text(encoding=encoding)
    lines = original.splitlines(keepends=True)
    _validate_insert_line(line, len(lines))

    if line == len(lines) + 1:
        separator = "" if original == "" or original.endswith(("\n", "\r")) else "\n"
        updated = original + separator + content
    else:
        lines.insert(line - 1, content)
        updated = "".join(lines)

    _write_text_atomically(path, updated, encoding=encoding)


def _as_path(path: str | Path) -> Path:
    if isinstance(path, Path):
        return path
    if not isinstance(path, str):
        raise TypeError("path must be a string or Path")
    return Path(path)


def _line_column(content: str, offset: int) -> tuple[int, int]:
    line = content.count("\n", 0, offset) + 1
    previous_newline = content.rfind("\n", 0, offset)
    column = offset + 1 if previous_newline == -1 else offset - previous_newline
    return line, column


def _validate_line_range(start: int, end: int, line_count: int) -> None:
    if start < 1:
        raise ValueError("start must be >= 1")
    if end < start:
        raise ValueError("end must be >= start")
    if end > line_count:
        raise ValueError(f"end must be <= line count ({line_count})")


def _validate_insert_line(line: int, line_count: int) -> None:
    if line < 1:
        raise ValueError("line must be >= 1")
    if line > line_count + 1:
        raise ValueError(f"line must be <= line count + 1 ({line_count + 1})")


def _write_text_atomically(path: Path, content: str, encoding: str) -> None:
    """Write through a sibling temp file, then replace the target path."""
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(content, encoding=encoding)
    temp_path.replace(path)


def _parse_request(input_data: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dictionary")

    operation = input_data.get("operation")
    if not isinstance(operation, str) or not operation:
        raise ValueError("operation must be a non-empty string")
    if operation not in _OPS:
        raise ValueError(f"unknown operation: {operation}")

    params = input_data.get("params")
    if params is None:
        params = {
            key: value
            for key, value in input_data.items()
            if key not in {"operation", "params", "meta"}
        }
    if not isinstance(params, dict):
        raise TypeError("params must be a dictionary")

    return operation, params


def _dispatch(operation: str, params: dict[str, Any]) -> tuple[dict[str, Any], str]:
    if operation == "read_file":
        return _run_read_file(params)
    if operation == "find_text":
        return _run_find_text(params)
    if operation == "extract_range":
        return _run_extract_range(params)
    if operation == "insert_text":
        return _run_insert_text(params)
    raise ValueError(f"unknown operation: {operation}")


def _run_read_file(params: dict[str, Any]) -> tuple[dict[str, Any], str]:
    _validate_allowed_keys(params, {"path", "encoding"}, "read_file")
    if "path" not in params:
        raise ValueError("read_file requires path")

    encoding = params.get("encoding", "utf-8")
    path = params["path"]
    content = read_file(path, encoding=encoding)
    return (
        {
            "path": str(_as_path(path)),
            "encoding": encoding,
            "content": content,
        },
        f"Read file {path}",
    )


def _run_find_text(params: dict[str, Any]) -> tuple[dict[str, Any], str]:
    _validate_allowed_keys(params, {"file", "text", "encoding", "allow_overlap"}, "find_text")
    if "file" not in params:
        raise ValueError("find_text requires file")
    if "text" not in params:
        raise ValueError("find_text requires text")

    file = params["file"]
    text = params["text"]
    encoding = params.get("encoding", "utf-8")
    allow_overlap = bool(params.get("allow_overlap", False))
    matches = find_text(file, text, encoding=encoding, allow_overlap=allow_overlap)
    return (
        {
            "file": str(_as_path(file)),
            "text": text,
            "encoding": encoding,
            "allow_overlap": allow_overlap,
            "count": len(matches),
            "matches": matches,
        },
        f"Found {len(matches)} match(es)",
    )


def _run_extract_range(params: dict[str, Any]) -> tuple[dict[str, Any], str]:
    _validate_allowed_keys(params, {"file", "start", "end", "encoding"}, "extract_range")
    if "file" not in params:
        raise ValueError("extract_range requires file")
    if "start" not in params:
        raise ValueError("extract_range requires start")
    if "end" not in params:
        raise ValueError("extract_range requires end")

    file = params["file"]
    start = params["start"]
    end = params["end"]
    encoding = params.get("encoding", "utf-8")
    content = extract_range(file, start, end, encoding=encoding)
    return (
        {
            "file": str(_as_path(file)),
            "start": start,
            "end": end,
            "encoding": encoding,
            "content": content,
        },
        f"Extracted lines {start}-{end}",
    )


def _run_insert_text(params: dict[str, Any]) -> tuple[dict[str, Any], str]:
    _validate_allowed_keys(params, {"file", "line", "content", "encoding"}, "insert_text")
    if "file" not in params:
        raise ValueError("insert_text requires file")
    if "line" not in params:
        raise ValueError("insert_text requires line")
    if "content" not in params:
        raise ValueError("insert_text requires content")

    file = params["file"]
    line = params["line"]
    content = params["content"]
    encoding = params.get("encoding", "utf-8")
    insert_text(file, line, content, encoding=encoding)
    return (
        {
            "file": str(_as_path(file)),
            "line": line,
            "encoding": encoding,
            "written": True,
        },
        f"Inserted text before line {line}",
    )


def _validate_allowed_keys(
    params: dict[str, Any],
    allowed: set[str],
    operation: str,
) -> None:
    unexpected = set(params) - allowed
    if unexpected:
        joined = ", ".join(sorted(unexpected))
        raise ValueError(f"{operation} received unexpected parameter(s): {joined}")


def _error_envelope(exc: Exception) -> dict[str, Any]:
    error_type = exc.__class__.__name__
    return {
        "success": False,
        "message": str(exc),
        "error": {
            "type": error_type,
            "message": str(exc),
        },
    }


def _exit_code(response: dict[str, Any]) -> int:
    if response.get("success") is True:
        return 0

    error = response.get("error") or {}
    error_type = error.get("type")
    if error_type in {
        "TypeError",
        "ValueError",
        "FileNotFoundError",
        "NotADirectoryError",
    }:
        return 2
    return 3
