"""Deterministic wrapper around Python ast.dump."""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any


_OPS = {"dump_source", "dump_file"}


def dump_source(
    source: str,
    path: str | None = None,
    include_attributes: bool = False,
    indent: int | None = 2,
) -> dict[str, Any]:
    """Parse source text and return canonical ast.dump output."""
    if not isinstance(source, str):
        raise TypeError("source must be a string")

    tree = ast.parse(source, filename=path or "<string>", mode="exec")
    dumped = ast.dump(tree, include_attributes=include_attributes, indent=indent)
    return {
        "path": path,
        "include_attributes": include_attributes,
        "indent": indent,
        "ast_dump": dumped,
    }


def dump_file(
    path: str | Path,
    encoding: str = "utf-8",
    include_attributes: bool = False,
    indent: int | None = 2,
) -> dict[str, Any]:
    """Read and parse a Python file, then return canonical ast.dump output."""
    file_path = _as_path(path)
    source = file_path.read_text(encoding=encoding)
    result = dump_source(
        source=source,
        path=str(file_path),
        include_attributes=include_attributes,
        indent=indent,
    )
    result["encoding"] = encoding
    return result


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute an ast_dump operation from a structured request payload."""
    try:
        operation, params = _parse_request(input_data)
        if operation == "dump_source":
            result = dump_source(
                source=params["source"],
                path=params.get("path"),
                include_attributes=bool(params.get("include_attributes", False)),
                indent=_parse_indent(params.get("indent", 2)),
            )
            message = "Parsed source and generated ast.dump output"
        elif operation == "dump_file":
            result = dump_file(
                path=params["path"],
                encoding=params.get("encoding", "utf-8"),
                include_attributes=bool(params.get("include_attributes", False)),
                indent=_parse_indent(params.get("indent", 2)),
            )
            message = f"Parsed file {result['path']} and generated ast.dump output"
        else:
            raise ValueError(f"unknown operation: {operation}")

        return {
            "success": True,
            "message": message,
            "result": result,
            "meta": {"operation": operation},
        }
    except Exception as exc:
        return _error_envelope(exc)


def main() -> None:
    """Read stdin JSON, execute a tool operation, and print stdout JSON."""
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
    sys.exit(0 if response.get("success") is True else 1)


def _as_path(path: str | Path) -> Path:
    if isinstance(path, Path):
        return path
    if not isinstance(path, str):
        raise TypeError("path must be a string or Path")
    return Path(path)


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

    if operation == "dump_source" and "source" not in params:
        raise ValueError("dump_source requires source")
    if operation == "dump_file" and "path" not in params:
        raise ValueError("dump_file requires path")

    return operation, params


def _parse_indent(indent: Any) -> int | None:
    if indent is None:
        return None
    if not isinstance(indent, int):
        raise TypeError("indent must be an integer or null")
    if indent < 0:
        raise ValueError("indent must be >= 0")
    return indent


def _error_envelope(exc: Exception) -> dict[str, Any]:
    message = str(exc)
    return {
        "success": False,
        "message": message,
        "error": {
            "type": exc.__class__.__name__,
            "message": message,
        },
    }


if __name__ == "__main__":
    main()
