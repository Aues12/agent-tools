"""Public Python API and dispatcher for semantic_cpg."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from builder import build_cpg as merge_cpg
from summarizer import summarize_cpg


_TOOL_DIR = Path(__file__).resolve().parent
_OPERATIONS = {
    "build_cpg",
    "build_cpg_from_source",
    "build_cpg_from_file",
    "cpg_from_source",
    "cpg_from_file",
    "summarize_cpg",
}


def _load_module(module_name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load module from {path}")
    shadowed_names = ("builder", "schema", "summarizer")
    shadowed_modules = {
        name: sys.modules.pop(name)
        for name in shadowed_names
        if name in sys.modules
    }
    path_parent = str(path.parent)
    sys.path.insert(0, path_parent)
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if sys.path and sys.path[0] == path_parent:
            sys.path.remove(path_parent)
        else:
            try:
                sys.path.remove(path_parent)
            except ValueError:
                pass
        for name in shadowed_names:
            sys.modules.pop(name, None)
        sys.modules.update(shadowed_modules)


_semantic_ast = _load_module(
    "semantic_cpg_semantic_ast",
    _TOOL_DIR.parent / "semantic_ast" / "tool.py",
)
_semantic_cfg = _load_module(
    "semantic_cpg_semantic_cfg",
    _TOOL_DIR.parent / "semantic_cfg" / "tool.py",
)
_semantic_dfg = _load_module(
    "semantic_cpg_semantic_dfg",
    _TOOL_DIR.parent / "semantic_dfg" / "tool.py",
)


def build_cpg(
    *,
    tree: dict[str, Any],
    cfg: dict[str, Any] | None = None,
    dfg: dict[str, Any] | None = None,
    call_graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge existing analysis outputs into a Semantic CPG."""
    if cfg is None:
        cfg = _semantic_cfg.build_cfg(tree)
    if dfg is None:
        dfg = _semantic_dfg.build_dfg(tree)
    if call_graph is None:
        call_graph = _semantic_ast.build_call_graph(tree)
    return merge_cpg(tree=tree, cfg=cfg, dfg=dfg, call_graph=call_graph)


def build_cpg_from_source(
    source: str,
    path: str | None = None,
) -> dict[str, Any]:
    """Parse Python source and build a Semantic CPG."""
    tree = _semantic_ast.parse_source(source=source, path=path, include_source=False)
    return build_cpg(tree=tree)


def build_cpg_from_file(
    path: str | Path,
    encoding: str = "utf-8",
) -> dict[str, Any]:
    """Read a Python file and build a Semantic CPG."""
    tree = _semantic_ast.parse_file(path=path, encoding=encoding, include_source=False)
    return build_cpg(tree=tree)


cpg_from_source = build_cpg_from_source
cpg_from_file = build_cpg_from_file


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a semantic_cpg operation using the canonical request envelope."""
    try:
        operation, params = _parse_request(input_data)
        normalized_operation = _normalize_operation(operation)

        if normalized_operation == "build_cpg":
            result = build_cpg(
                tree=params["tree"],
                cfg=params.get("cfg"),
                dfg=params.get("dfg"),
                call_graph=params.get("call_graph"),
            )
            message = "Built Semantic CPG from analysis outputs"
        elif normalized_operation == "build_cpg_from_source":
            result = build_cpg_from_source(
                source=params["source"],
                path=params.get("path"),
            )
            message = "Parsed Python source and built Semantic CPG"
        elif normalized_operation == "build_cpg_from_file":
            result = build_cpg_from_file(
                path=params["path"],
                encoding=params.get("encoding", "utf-8"),
            )
            message = "Parsed Python file and built Semantic CPG"
        elif normalized_operation == "summarize_cpg":
            result = summarize_cpg(params["cpg"])
            message = "Summarized Semantic CPG"
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
    if operation in {"cpg_from_source", "build_cpg_from_source"}:
        return "build_cpg_from_source"
    if operation in {"cpg_from_file", "build_cpg_from_file"}:
        return "build_cpg_from_file"
    return operation


def _validate_params(operation: str, params: dict[str, Any]) -> None:
    if operation == "build_cpg" and "tree" not in params:
        raise ValueError("build_cpg requires tree")
    if operation == "build_cpg_from_source" and "source" not in params:
        raise ValueError("build_cpg_from_source requires source")
    if operation == "build_cpg_from_file" and "path" not in params:
        raise ValueError("build_cpg_from_file requires path")
    if operation == "summarize_cpg" and "cpg" not in params:
        raise ValueError("summarize_cpg requires cpg")


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
