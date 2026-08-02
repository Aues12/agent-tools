"""Public Python API and dispatcher for semantic_cfg."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from builder import build_cfg
from summarizer import summarize_cfg


_TOOL_DIR = Path(__file__).resolve().parent
_OPERATIONS = {
    "build_cfg",
    "build_cfg_from_source",
    "build_cfg_from_file",
    "cfg_from_source",
    "cfg_from_file",
    "summarize_cfg",
}


def _load_module(module_name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_semantic_ast = _load_module(
    "semantic_cfg_semantic_ast",
    _TOOL_DIR.parent / "semantic_ast" / "tool.py",
)


def build_cfg_from_source(
    source: str,
    path: str | None = None,
) -> dict[str, Any]:
    """Parse Python source with semantic_ast and build a CFG."""
    tree = _semantic_ast.parse_source(source=source, path=path, include_source=False)
    return build_cfg(tree)


def build_cfg_from_file(
    path: str | Path,
    encoding: str = "utf-8",
) -> dict[str, Any]:
    """Read a Python file with semantic_ast and build a CFG."""
    tree = _semantic_ast.parse_file(path=path, encoding=encoding, include_source=False)
    return build_cfg(tree)


cfg_from_source = build_cfg_from_source
cfg_from_file = build_cfg_from_file


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a semantic_cfg operation using the canonical request envelope."""
    try:
        operation, params = _parse_request(input_data)
        normalized_operation = _normalize_operation(operation)

        if normalized_operation == "build_cfg":
            result = build_cfg(params["tree"])
            message = "Built control-flow graph from semantic AST"
        elif normalized_operation == "build_cfg_from_source":
            result = build_cfg_from_source(
                source=params["source"],
                path=params.get("path"),
            )
            message = "Parsed Python source and built control-flow graph"
        elif normalized_operation == "build_cfg_from_file":
            result = build_cfg_from_file(
                path=params["path"],
                encoding=params.get("encoding", "utf-8"),
            )
            message = "Parsed Python file and built control-flow graph"
        elif normalized_operation == "summarize_cfg":
            result = summarize_cfg(params["cfg"])
            message = "Summarized control-flow graph"
        else:
            raise ValueError(f"unknown operation: {operation}")

        return {
            "success": True,
            "message": message,
            "result": result,
            "meta": {
                "operation": operation,
                "normalized_operation": normalized_operation,
            },
        }
    except Exception as exc:
        return _error_envelope(exc)


def main() -> None:
    """Read stdin JSON, execute the tool, and print stdout JSON."""
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


def _parse_request(input_data: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dictionary")

    operation = input_data.get("operation")
    if not isinstance(operation, str) or not operation:
        raise ValueError("operation must be a non-empty string")
    if operation not in _OPERATIONS:
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

    normalized_operation = _normalize_operation(operation)
    _validate_params(normalized_operation, params)
    return operation, params


def _normalize_operation(operation: str) -> str:
    if operation in {"cfg_from_source", "build_cfg_from_source"}:
        return "build_cfg_from_source"
    if operation in {"cfg_from_file", "build_cfg_from_file"}:
        return "build_cfg_from_file"
    return operation


def _validate_params(operation: str, params: dict[str, Any]) -> None:
    if operation == "build_cfg" and "tree" not in params:
        raise ValueError("build_cfg requires tree")
    if operation == "build_cfg_from_source" and "source" not in params:
        raise ValueError("build_cfg_from_source requires source")
    if operation == "build_cfg_from_file" and "path" not in params:
        raise ValueError("build_cfg_from_file requires path")
    if operation == "summarize_cfg" and "cfg" not in params:
        raise ValueError("summarize_cfg requires cfg")


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


def _exit_code(response: dict[str, Any]) -> int:
    if response.get("success") is True:
        return 0
    error = response.get("error") or {}
    if error.get("type") in {
        "TypeError",
        "ValueError",
        "FileNotFoundError",
        "NotADirectoryError",
        "SyntaxError",
        "IndentationError",
        "JSONDecodeError",
    }:
        return 2
    return 3


if __name__ == "__main__":
    main()
