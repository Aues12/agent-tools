"""Dispatcher for semantic_ast sub-tools.

The parent tool keeps a single stdin JSON interface while delegating concrete
work to focused sub-tools such as ast_parsing, compression, and call_graph.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

_TOOL_DIR = Path(__file__).resolve().parent


def _load_module(module_name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_ast_parsing = _load_module(
    "semantic_ast_ast_parser",
    _TOOL_DIR / "ast_parsing" / "ast_parser.py",
)
_compression = _load_module(
    "semantic_ast_compression_tool",
    _TOOL_DIR / "compression" / "compression.py",
)
_call_graph = _load_module(
    "semantic_ast_call_graph_tool",
    _TOOL_DIR / "call_graph" / "call_graph.py",
)

parse_file = _ast_parsing.parse_file
parse_source = _ast_parsing.parse_source
compress_ast = _compression.compress_ast
build_call_graph = _call_graph.build_call_graph


_OPERATIONS = {
    "parse_source",
    "parse_file",
    "ast_parsing.parse_source",
    "ast_parsing.parse_file",
    "compress_ast",
    "compression.compress_ast",
    "build_call_graph",
    "call_graph.build_call_graph",
    "parse_and_compress",
    "parse_and_build_call_graph",
}


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a semantic_ast operation using the canonical request envelope."""
    try:
        operation, params = _parse_request(input_data)
        normalized_operation = _normalize_operation(operation)

        if normalized_operation == "parse_source":
            result = parse_source(
                source=params["source"],
                path=params.get("path"),
                include_source=bool(params.get("include_source", False)),
            )
            message = f"Parsed Python source with {len(result['body'])} top-level node(s)"
        elif normalized_operation == "parse_file":
            result = parse_file(
                path=params["path"],
                encoding=params.get("encoding", "utf-8"),
                include_source=bool(params.get("include_source", False)),
            )
            message = f"Parsed Python file {result['path']}"
        elif normalized_operation == "compress_ast":
            result = compress_ast(params["tree"])
            message = "Compressed semantic AST"
        elif normalized_operation == "build_call_graph":
            result = build_call_graph(params["tree"])
            message = "Built semantic AST call graph"
        elif normalized_operation == "parse_and_compress":
            tree = _parse_tree_from_params(params)
            result = compress_ast(tree)
            message = "Parsed and compressed Python source"
        elif normalized_operation == "parse_and_build_call_graph":
            tree = _parse_tree_from_params(params)
            result = build_call_graph(tree)
            message = "Parsed Python source and built call graph"
        else:
            raise ValueError(f"unknown operation: {operation}")

        return {
            "success": True,
            "message": message,
            "result": result,
            "meta": {
                "operation": operation,
                "normalized_operation": normalized_operation,
                "subtool": _subtool_for(normalized_operation),
            },
        }
    except Exception as exc:
        return _error_envelope(exc)


def main() -> None:
    """Read stdin JSON, execute the dispatcher, and print stdout JSON."""
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
    return operation.rsplit(".", 1)[-1]


def _validate_params(operation: str, params: dict[str, Any]) -> None:
    if operation == "parse_source" and "source" not in params:
        raise ValueError("parse_source requires source")
    if operation == "parse_file" and "path" not in params:
        raise ValueError("parse_file requires path")
    if operation in {"compress_ast", "build_call_graph"} and "tree" not in params:
        raise ValueError(f"{operation} requires tree")
    if operation in {"parse_and_compress", "parse_and_build_call_graph"}:
        if "source" not in params and "path" not in params:
            raise ValueError(f"{operation} requires source or path")


def _parse_tree_from_params(params: dict[str, Any]) -> dict[str, Any]:
    if "source" in params:
        return parse_source(
            source=params["source"],
            path=params.get("path"),
            include_source=bool(params.get("include_source", False)),
        )

    return parse_file(
        path=params["path"],
        encoding=params.get("encoding", "utf-8"),
        include_source=bool(params.get("include_source", False)),
    )


def _subtool_for(operation: str) -> str:
    if operation in {"parse_source", "parse_file"}:
        return "ast_parsing"
    if operation in {"compress_ast", "parse_and_compress"}:
        return "compression"
    if operation in {"build_call_graph", "parse_and_build_call_graph"}:
        return "call_graph"
    return "semantic_ast"


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
