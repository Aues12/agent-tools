"""Semantic AST parsing utilities for Python source.

The tool keeps parsing deterministic and side-effect free. Public line numbers
use 1-based indexing and end lines are inclusive.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any


_OPERATIONS = {"parse_source", "parse_file"}


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a semantic_ast operation from a structured request payload."""
    try:
        operation, params = _parse_request(input_data)
        if operation == "parse_source":
            result = parse_source(
                source=params["source"],
                path=params.get("path"),
                include_source=bool(params.get("include_source", False)),
            )
            message = f"Parsed Python source with {len(result['body'])} top-level node(s)"
        else:
            result = parse_file(
                path=params["path"],
                encoding=params.get("encoding", "utf-8"),
                include_source=bool(params.get("include_source", False)),
            )
            message = f"Parsed Python file {result['path']}"

        return {
            "success": True,
            "message": message,
            "result": result,
            "meta": {"operation": operation},
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


def parse_source(
    source: str,
    path: str | Path | None = None,
    include_source: bool = False,
) -> dict[str, Any]:
    """Parse Python source text into a compact semantic AST."""
    if not isinstance(source, str):
        raise TypeError("source must be a string")

    source_path = _normalize_path(path)
    filename = str(source_path) if source_path is not None else "<source>"
    tree = ast.parse(source, filename=filename)
    return _normalize_module(tree, source, source_path, include_source)


def parse_file(
    path: str | Path,
    encoding: str = "utf-8",
    include_source: bool = False,
) -> dict[str, Any]:
    """Parse a Python file into a compact semantic AST."""
    file_path = _as_path(path)
    source = file_path.read_text(encoding=encoding)
    return parse_source(source, path=file_path, include_source=include_source)


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

    if operation == "parse_source" and "source" not in params:
        raise ValueError("parse_source requires source")
    if operation == "parse_file" and "path" not in params:
        raise ValueError("parse_file requires path")

    return operation, params


def _normalize_module(
    tree: ast.Module,
    source: str,
    path: Path | None,
    include_source: bool,
) -> dict[str, Any]:
    body = _normalize_body(tree.body, source, include_source)
    line_count = len(source.splitlines())
    end_line = max(_max_end_line(body), line_count or 1)

    result: dict[str, Any] = {
        "type": "module",
        "language": "python",
        "path": str(path) if path is not None else None,
        "line": 1,
        "end_line": end_line,
        "line_count": line_count,
        "docstring": ast.get_docstring(tree),
        "body": body,
        "stats": _summarize_stats(body),
    }

    if include_source:
        result["source"] = source

    return result


def _normalize_body(
    statements: list[ast.stmt],
    source: str,
    include_source: bool,
) -> list[dict[str, Any]]:
    items = list(statements)
    if items and _is_docstring_statement(items[0]):
        items = items[1:]
    return [_normalize_statement(node, source, include_source) for node in items]


def _normalize_statement(
    node: ast.stmt,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    if isinstance(node, ast.FunctionDef):
        return _normalize_function(node, source, include_source, is_async=False)
    if isinstance(node, ast.AsyncFunctionDef):
        return _normalize_function(node, source, include_source, is_async=True)
    if isinstance(node, ast.ClassDef):
        return _normalize_class(node, source, include_source)
    if isinstance(node, ast.Import):
        return _attach_source(
            {
                "type": "import",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "names": [_normalize_alias(alias) for alias in node.names],
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.ImportFrom):
        return _attach_source(
            {
                "type": "import_from",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "module": node.module,
                "level": node.level,
                "names": [_normalize_alias(alias) for alias in node.names],
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Assign):
        return _attach_source(
            {
                "type": "assignment",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "targets": [
                    _normalize_expr(target, source, include_source) for target in node.targets
                ],
                "value": _normalize_value(node.value, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.AnnAssign):
        return _attach_source(
            {
                "type": "annotated_assignment",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "target": _normalize_expr(node.target, source, include_source),
                "annotation": _normalize_value(node.annotation, source, include_source),
                "value": _normalize_value(node.value, source, include_source),
                "simple": bool(node.simple),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.AugAssign):
        return _attach_source(
            {
                "type": "augmented_assignment",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "target": _normalize_expr(node.target, source, include_source),
                "operator": type(node.op).__name__,
                "value": _normalize_value(node.value, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Return):
        return _attach_source(
            {
                "type": "return",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "value": _normalize_value(node.value, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Expr):
        return _attach_source(
            {
                "type": "expression_statement",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "value": _normalize_value(node.value, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.If):
        return _attach_source(
            {
                "type": "if",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "test": _normalize_value(node.test, source, include_source),
                "body": _normalize_body(node.body, source, include_source),
                "orelse": _normalize_body(node.orelse, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.For):
        return _normalize_loop("for", node, source, include_source)
    if isinstance(node, ast.AsyncFor):
        return _normalize_loop("async_for", node, source, include_source)
    if isinstance(node, ast.While):
        return _attach_source(
            {
                "type": "while",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "test": _normalize_value(node.test, source, include_source),
                "body": _normalize_body(node.body, source, include_source),
                "orelse": _normalize_body(node.orelse, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.With):
        return _normalize_with("with", node, source, include_source)
    if isinstance(node, ast.AsyncWith):
        return _normalize_with("async_with", node, source, include_source)
    if isinstance(node, ast.Try):
        return _attach_source(
            {
                "type": "try",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "body": _normalize_body(node.body, source, include_source),
                "handlers": [
                    _normalize_exception_handler(handler, source, include_source)
                    for handler in node.handlers
                ],
                "orelse": _normalize_body(node.orelse, source, include_source),
                "finalbody": _normalize_body(node.finalbody, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Raise):
        return _attach_source(
            {
                "type": "raise",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "exc": _normalize_value(node.exc, source, include_source),
                "cause": _normalize_value(node.cause, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Assert):
        return _attach_source(
            {
                "type": "assert",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "test": _normalize_value(node.test, source, include_source),
                "message": _normalize_value(node.msg, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Pass):
        return _simple_statement("pass", node, source, include_source)
    if isinstance(node, ast.Break):
        return _simple_statement("break", node, source, include_source)
    if isinstance(node, ast.Continue):
        return _simple_statement("continue", node, source, include_source)
    if isinstance(node, ast.Global):
        return _attach_source(
            {
                "type": "global",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "names": list(node.names),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Nonlocal):
        return _attach_source(
            {
                "type": "nonlocal",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "names": list(node.names),
            },
            node,
            source,
            include_source,
        )
    return _generic_node("statement", node, source, include_source)


def _normalize_function(
    node: ast.AST,
    source: str,
    include_source: bool,
    *,
    is_async: bool,
) -> dict[str, Any]:
    assert isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    result = {
        "type": "function",
        "async": is_async,
        "line": _line_number(node),
        "end_line": _end_line_number(node),
        "name": node.name,
        "decorators": [
            _normalize_value(decorator, source, include_source) for decorator in node.decorator_list
        ],
        "args": _normalize_arguments(node.args, source, include_source),
        "returns": _normalize_value(node.returns, source, include_source),
        "docstring": ast.get_docstring(node),
        "body": _normalize_body(node.body, source, include_source),
    }
    return _attach_source(result, node, source, include_source)


def _normalize_class(
    node: ast.ClassDef,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    result = {
        "type": "class",
        "line": _line_number(node),
        "end_line": _end_line_number(node),
        "name": node.name,
        "decorators": [
            _normalize_value(decorator, source, include_source) for decorator in node.decorator_list
        ],
        "bases": [_normalize_value(base, source, include_source) for base in node.bases],
        "keywords": [_normalize_keyword(keyword, source, include_source) for keyword in node.keywords],
        "docstring": ast.get_docstring(node),
        "body": _normalize_body(node.body, source, include_source),
    }
    return _attach_source(result, node, source, include_source)


def _normalize_loop(
    loop_type: str,
    node: ast.AST,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    assert isinstance(node, (ast.For, ast.AsyncFor))
    result = {
        "type": loop_type,
        "line": _line_number(node),
        "end_line": _end_line_number(node),
        "target": _normalize_expr(node.target, source, include_source),
        "iter": _normalize_value(node.iter, source, include_source),
        "body": _normalize_body(node.body, source, include_source),
        "orelse": _normalize_body(node.orelse, source, include_source),
    }
    return _attach_source(result, node, source, include_source)


def _normalize_with(
    with_type: str,
    node: ast.AST,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    assert isinstance(node, (ast.With, ast.AsyncWith))
    result = {
        "type": with_type,
        "line": _line_number(node),
        "end_line": _end_line_number(node),
        "items": [_normalize_withitem(item, source, include_source) for item in node.items],
        "body": _normalize_body(node.body, source, include_source),
    }
    return _attach_source(result, node, source, include_source)


def _normalize_exception_handler(
    node: ast.ExceptHandler,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    result = {
        "type": "except_handler",
        "line": _line_number(node),
        "end_line": _end_line_number(node),
        "name": node.name,
        "exc": _normalize_value(node.type, source, include_source),
        "body": _normalize_body(node.body, source, include_source),
    }
    return _attach_source(result, node, source, include_source)


def _normalize_withitem(
    node: ast.withitem,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    return {
        "type": "with_item",
        "context": _normalize_value(node.context_expr, source, include_source),
        "optional_vars": _normalize_value(node.optional_vars, source, include_source),
    }


def _normalize_arguments(
    node: ast.arguments,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    return {
        "type": "arguments",
        "positional_only": [
            _normalize_arg(arg, source, include_source) for arg in getattr(node, "posonlyargs", [])
        ],
        "positional_or_keyword": [
            _normalize_arg(arg, source, include_source) for arg in node.args
        ],
        "vararg": _normalize_arg(node.vararg, source, include_source) if node.vararg else None,
        "keyword_only": [_normalize_arg(arg, source, include_source) for arg in node.kwonlyargs],
        "kwarg": _normalize_arg(node.kwarg, source, include_source) if node.kwarg else None,
        "defaults": [_normalize_value(item, source, include_source) for item in node.defaults],
        "kw_defaults": [
            _normalize_value(item, source, include_source) for item in node.kw_defaults
        ],
    }


def _normalize_arg(
    node: ast.arg | None,
    source: str,
    include_source: bool,
) -> dict[str, Any] | None:
    if node is None:
        return None
    result = {
        "type": "argument",
        "line": _line_number(node),
        "end_line": _end_line_number(node),
        "name": node.arg,
        "annotation": _normalize_value(node.annotation, source, include_source),
    }
    return _attach_source(result, node, source, include_source)


def _normalize_alias(node: ast.alias) -> dict[str, Any]:
    return {
        "type": "alias",
        "name": node.name,
        "as_name": node.asname,
    }


def _normalize_keyword(
    node: ast.keyword,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    return {
        "type": "keyword",
        "arg": node.arg,
        "value": _normalize_value(node.value, source, include_source),
    }


def _normalize_expr(
    node: ast.AST,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    if isinstance(node, ast.Name):
        return _attach_source(
            {
                "type": "name",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "id": node.id,
                "context": type(node.ctx).__name__,
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Constant):
        return _attach_source(
            {
                "type": "constant",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "value": _json_safe_scalar(node.value),
                "value_type": type(node.value).__name__,
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Attribute):
        return _attach_source(
            {
                "type": "attribute",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "value": _normalize_value(node.value, source, include_source),
                "attr": node.attr,
                "context": type(node.ctx).__name__,
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Call):
        return _attach_source(
            {
                "type": "call",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "func": _normalize_value(node.func, source, include_source),
                "args": [_normalize_value(arg, source, include_source) for arg in node.args],
                "keywords": [_normalize_keyword(keyword, source, include_source) for keyword in node.keywords],
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.BinOp):
        operator = type(node.op).__name__
        return _attach_source(
            {
                "type": "binop",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "operator": operator,
                "left": _normalize_value(node.left, source, include_source),
                "right": _normalize_value(node.right, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.UnaryOp):
        operator = type(node.op).__name__
        return _attach_source(
            {
                "type": "unaryop",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "operator": operator,
                "operand": _normalize_value(node.operand, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.BoolOp):
        operator = type(node.op).__name__
        return _attach_source(
            {
                "type": "boolop",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "operator": operator,
                "values": [_normalize_value(value, source, include_source) for value in node.values],
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Compare):
        return _attach_source(
            {
                "type": "compare",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "left": _normalize_value(node.left, source, include_source),
                "ops": [type(op).__name__ for op in node.ops],
                "comparators": [
                    _normalize_value(comparator, source, include_source)
                    for comparator in node.comparators
                ],
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.List):
        return _attach_source(
            {
                "type": "list",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "elements": [_normalize_value(item, source, include_source) for item in node.elts],
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Tuple):
        return _attach_source(
            {
                "type": "tuple",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "elements": [_normalize_value(item, source, include_source) for item in node.elts],
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Set):
        return _attach_source(
            {
                "type": "set",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "elements": [_normalize_value(item, source, include_source) for item in node.elts],
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Dict):
        return _attach_source(
            {
                "type": "dict",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "items": [
                    {
                        "key": _normalize_value(key, source, include_source),
                        "value": _normalize_value(value, source, include_source),
                    }
                    for key, value in zip(node.keys, node.values)
                ],
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Subscript):
        return _attach_source(
            {
                "type": "subscript",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "value": _normalize_value(node.value, source, include_source),
                "slice": _normalize_value(node.slice, source, include_source),
                "context": type(node.ctx).__name__,
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Slice):
        return {
            "type": "slice",
            "lower": _normalize_value(node.lower, source, include_source),
            "upper": _normalize_value(node.upper, source, include_source),
            "step": _normalize_value(node.step, source, include_source),
        }
    if isinstance(node, ast.IfExp):
        return _attach_source(
            {
                "type": "if_expression",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "test": _normalize_value(node.test, source, include_source),
                "body": _normalize_value(node.body, source, include_source),
                "orelse": _normalize_value(node.orelse, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Lambda):
        return _attach_source(
            {
                "type": "lambda",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "args": _normalize_arguments(node.args, source, include_source),
                "body": _normalize_value(node.body, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.JoinedStr):
        return _attach_source(
            {
                "type": "joined_string",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "parts": [_normalize_value(part, source, include_source) for part in node.values],
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.FormattedValue):
        return _attach_source(
            {
                "type": "formatted_value",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "value": _normalize_value(node.value, source, include_source),
                "conversion": node.conversion,
                "format_spec": _normalize_value(node.format_spec, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Starred):
        return _attach_source(
            {
                "type": "starred",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "value": _normalize_value(node.value, source, include_source),
                "context": type(node.ctx).__name__,
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Await):
        return _attach_source(
            {
                "type": "await",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "value": _normalize_value(node.value, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.Yield):
        return _attach_source(
            {
                "type": "yield",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "value": _normalize_value(node.value, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.YieldFrom):
        return _attach_source(
            {
                "type": "yield_from",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "value": _normalize_value(node.value, source, include_source),
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.ListComp):
        return _comprehension_node("list_comprehension", node, source, include_source)
    if isinstance(node, ast.SetComp):
        return _comprehension_node("set_comprehension", node, source, include_source)
    if isinstance(node, ast.DictComp):
        return _attach_source(
            {
                "type": "dict_comprehension",
                "line": _line_number(node),
                "end_line": _end_line_number(node),
                "key": _normalize_value(node.key, source, include_source),
                "value": _normalize_value(node.value, source, include_source),
                "generators": [
                    _normalize_comprehension(gen, source, include_source)
                    for gen in node.generators
                ],
            },
            node,
            source,
            include_source,
        )
    if isinstance(node, ast.GeneratorExp):
        return _comprehension_node("generator_expression", node, source, include_source)
    return _generic_node("expression", node, source, include_source)


def _comprehension_node(
    node_type: str,
    node: ast.AST,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    assert isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp))
    element = node.elt
    result = {
        "type": node_type,
        "line": _line_number(node),
        "end_line": _end_line_number(node),
        "element": _normalize_value(element, source, include_source),
        "generators": [
            _normalize_comprehension(gen, source, include_source) for gen in node.generators
        ],
    }
    return _attach_source(result, node, source, include_source)


def _normalize_comprehension(
    node: ast.comprehension,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    return {
        "type": "comprehension",
        "target": _normalize_value(node.target, source, include_source),
        "iter": _normalize_value(node.iter, source, include_source),
        "ifs": [_normalize_value(item, source, include_source) for item in node.ifs],
        "is_async": bool(node.is_async),
    }


def _normalize_value(
    value: Any,
    source: str,
    include_source: bool,
) -> Any:
    if isinstance(value, ast.AST):
        if isinstance(value, ast.stmt):
            return _normalize_statement(value, source, include_source)
        return _normalize_expr(value, source, include_source)
    if isinstance(value, list):
        return [_normalize_value(item, source, include_source) for item in value]
    if isinstance(value, tuple):
        return [_normalize_value(item, source, include_source) for item in value]
    if isinstance(value, Path):
        return str(value)
    return _json_safe_scalar(value)


def _normalize_path(path: str | Path | None) -> Path | None:
    if path is None:
        return None
    return _as_path(path)


def _as_path(path: str | Path) -> Path:
    if isinstance(path, Path):
        return path.expanduser().resolve()
    if not isinstance(path, str):
        raise TypeError("path must be a string or Path")
    return Path(path).expanduser().resolve()


def _attach_source(
    node: dict[str, Any],
    ast_node: ast.AST,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    if include_source:
        segment = ast.get_source_segment(source, ast_node)
        if segment is not None:
            node["source"] = segment
    return node


def _simple_statement(
    node_type: str,
    node: ast.AST,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    return _attach_source(
        {
            "type": node_type,
            "line": _line_number(node),
            "end_line": _end_line_number(node),
        },
        node,
        source,
        include_source,
    )


def _generic_node(
    node_type: str,
    node: ast.AST,
    source: str,
    include_source: bool,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "type": node_type,
        "ast_type": type(node).__name__,
        "line": _line_number(node),
        "end_line": _end_line_number(node),
        "fields": {},
    }
    for field_name, field_value in ast.iter_fields(node):
        payload["fields"][field_name] = _normalize_value(field_value, source, include_source)
    return _attach_source(payload, node, source, include_source)


def _is_docstring_statement(node: ast.stmt) -> bool:
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )


def _line_number(node: ast.AST) -> int | None:
    return getattr(node, "lineno", None)


def _end_line_number(node: ast.AST) -> int | None:
    end_line = getattr(node, "end_lineno", None)
    if end_line is not None:
        return end_line
    return getattr(node, "lineno", None)


def _max_end_line(nodes: list[dict[str, Any]]) -> int:
    max_line = 1
    for node in nodes:
        max_line = max(max_line, _max_end_line_value(node))
    return max_line


def _max_end_line_value(value: Any) -> int:
    if isinstance(value, dict):
        max_line = 1
        end_line = value.get("end_line")
        if isinstance(end_line, int):
            max_line = max(max_line, end_line)
        for item in value.values():
            max_line = max(max_line, _max_end_line_value(item))
        return max_line
    if isinstance(value, list):
        max_line = 1
        for item in value:
            max_line = max(max_line, _max_end_line_value(item))
        return max_line
    return 1


def _summarize_stats(nodes: list[dict[str, Any]]) -> dict[str, int]:
    stats = {
        "nodes": 0,
        "functions": 0,
        "classes": 0,
        "imports": 0,
        "assignments": 0,
    }
    _walk_for_stats(nodes, stats)
    return stats


def _walk_for_stats(value: Any, stats: dict[str, int]) -> None:
    if isinstance(value, dict):
        node_type = value.get("type")
        if isinstance(node_type, str):
            stats["nodes"] += 1
            if node_type == "function":
                stats["functions"] += 1
            elif node_type == "class":
                stats["classes"] += 1
            elif node_type in {"import", "import_from"}:
                stats["imports"] += 1
            elif node_type in {
                "assignment",
                "annotated_assignment",
                "augmented_assignment",
            }:
                stats["assignments"] += 1
        for item in value.values():
            _walk_for_stats(item, stats)
    elif isinstance(value, list):
        for item in value:
            _walk_for_stats(item, stats)


def _json_safe_scalar(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return repr(value)


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
