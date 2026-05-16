"""Deterministic text transfer primitives for files.

Public line-number APIs use 1-based indexing. Ranges are inclusive.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


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
        updated = original + content
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
