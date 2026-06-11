"""Build semantic cards from normalized semantic AST trees.

The tool keeps cards deterministic and auditable. It uses semantic_ast for
Python parsing and call graph extraction, then turns meaningful code units into
small navigation cards with separate relation records.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from types import ModuleType
from typing import Any


_TOOL_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOL_DIR.parents[1]
_OPS = {
    "build_cards",
    "cards_from_source",
    "cards_from_file",
    "summary_view",
    "tree_view",
    "card_view",
}
_BLOCK_TYPES = {
    "if",
    "for",
    "async_for",
    "while",
    "with",
    "async_with",
    "try",
    "except_handler",
}
_BODY_FIELDS = ("body", "orelse", "finalbody")


def _load_module(module_name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_semantic_ast = _load_module(
    "semantic_cards_semantic_ast",
    _TOOL_DIR.parent / "semantic_ast" / "tool.py",
)
_semantic_view = _load_module(
    "semantic_cards_semantic_view",
    _TOOL_DIR / "semantic_view.py",
)

summary_view = _semantic_view.summary_view
tree_view = _semantic_view.tree_view
card_view = _semantic_view.card_view


def cards_from_source(
    source: str,
    path: str | None = None,
    include_statements: bool = True,
) -> dict[str, Any]:
    """Parse Python source and build semantic cards."""
    tree = _semantic_ast.parse_source(source=source, path=path, include_source=False)
    return build_cards(tree, include_statements=include_statements)


def cards_from_file(
    path: str | Path,
    encoding: str = "utf-8",
    include_statements: bool = True,
) -> dict[str, Any]:
    """Read a Python file through semantic_ast and build semantic cards."""
    tree = _semantic_ast.parse_file(path=path, encoding=encoding, include_source=False)
    return build_cards(tree, include_statements=include_statements)


def build_cards(
    tree: Mapping[str, Any],
    include_statements: bool = True,
) -> dict[str, Any]:
    """Build semantic cards and relations from a normalized semantic AST tree."""
    if not isinstance(tree, Mapping):
        raise TypeError("tree must be a dictionary")
    if tree.get("type") != "module":
        raise ValueError("tree must be a semantic_ast module node")

    builder = _CardBuilder(include_statements=include_statements)
    return builder.build(tree)


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a semantic_cards operation using the canonical request envelope."""
    try:
        operation, params = _parse_request(input_data)

        if operation == "build_cards":
            result = build_cards(
                params["tree"],
                include_statements=bool(params.get("include_statements", True)),
            )
            message = "Built semantic cards from semantic AST"
        elif operation == "cards_from_source":
            result = cards_from_source(
                source=params["source"],
                path=params.get("path"),
                include_statements=bool(params.get("include_statements", True)),
            )
            message = "Parsed Python source and built semantic cards"
        elif operation == "cards_from_file":
            result = cards_from_file(
                path=params["path"],
                encoding=params.get("encoding", "utf-8"),
                include_statements=bool(params.get("include_statements", True)),
            )
            message = "Parsed Python file and built semantic cards"
        elif operation == "summary_view":
            result = summary_view(
                params["cards"],
                max_relations=int(params.get("max_relations", 10)),
            )
            message = "Built semantic summary view"
        elif operation == "tree_view":
            result = tree_view(
                params["cards"],
                max_depth=int(params.get("max_depth", 3)),
                include_statements=bool(params.get("include_statements", False)),
            )
            message = "Built semantic tree view"
        elif operation == "card_view":
            result = card_view(
                params["cards"],
                card_id=params["card_id"],
            )
            message = "Built semantic card view"
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


class _CardBuilder:
    def __init__(self, *, include_statements: bool) -> None:
        self.include_statements = include_statements
        self.cards: list[dict[str, Any]] = []
        self.card_index: dict[str, dict[str, Any]] = {}
        self.relations: list[dict[str, Any]] = []
        self.relation_keys: set[tuple[Any, ...]] = set()
        self.id_counts: Counter[str] = Counter()
        self.module_qualified_name = "module"
        self.function_cards_by_local_name: dict[str, str] = {}

    def build(self, tree: Mapping[str, Any]) -> dict[str, Any]:
        self.module_qualified_name = _module_qualified_name(tree.get("path"))
        root_id = self._visit_module(tree)
        self._add_call_relations(tree)

        return {
            "type": "semantic_cards",
            "language": tree.get("language", "python"),
            "path": tree.get("path"),
            "root_ids": [root_id],
            "cards": self.cards,
            "relations": self.relations,
            "stats": self._stats(),
        }

    def _visit_module(self, node: Mapping[str, Any]) -> str:
        module_id = self._add_card(
            kind="module",
            title=self.module_qualified_name,
            qualified_name=self.module_qualified_name,
            level=0,
            parent_id=None,
            node=node,
            detail={
                "docstring": node.get("docstring"),
                "line_count": node.get("line_count"),
                "stats": node.get("stats"),
            },
        )
        self._visit_body(node.get("body", []), module_id, self.module_qualified_name, 1)
        return module_id

    def _visit_body(
        self,
        body: Any,
        parent_id: str,
        parent_qualified_name: str,
        level: int,
    ) -> None:
        if not isinstance(body, list):
            return
        for item in body:
            if isinstance(item, Mapping):
                self._visit_node(item, parent_id, parent_qualified_name, level)

    def _visit_node(
        self,
        node: Mapping[str, Any],
        parent_id: str,
        parent_qualified_name: str,
        level: int,
    ) -> None:
        node_type = _string(node.get("type"), "statement")

        if node_type == "class":
            self._visit_class(node, parent_id, parent_qualified_name, level)
            return
        if node_type == "function":
            self._visit_function(node, parent_id, parent_qualified_name, level)
            return
        if node_type in {"import", "import_from"}:
            self._add_import_relations(node, parent_id)
            if self.include_statements:
                self._add_statement_card(node, parent_id, parent_qualified_name, level)
            return
        if node_type in _BLOCK_TYPES:
            self._visit_block(node, parent_id, parent_qualified_name, level)
            return

        if self.include_statements:
            self._add_statement_card(node, parent_id, parent_qualified_name, level)

    def _visit_class(
        self,
        node: Mapping[str, Any],
        parent_id: str,
        parent_qualified_name: str,
        level: int,
    ) -> None:
        name = _string(node.get("name"), "anonymous_class")
        qualified_name = f"{parent_qualified_name}.{name}"
        bases = [_value_name(base) for base in _list(node.get("bases"))]
        card_id = self._add_card(
            kind="class",
            title=name,
            qualified_name=qualified_name,
            level=level,
            parent_id=parent_id,
            node=node,
            detail={
                "docstring": node.get("docstring"),
                "bases": bases,
                "decorators": [_value_name(item) for item in _list(node.get("decorators"))],
            },
        )
        for base in bases:
            if base:
                self._add_relation(
                    "inherits",
                    source_id=card_id,
                    target=base,
                    node=node,
                )
        self._visit_body(node.get("body", []), card_id, qualified_name, level + 1)

    def _visit_function(
        self,
        node: Mapping[str, Any],
        parent_id: str,
        parent_qualified_name: str,
        level: int,
    ) -> None:
        name = _string(node.get("name"), "anonymous_function")
        qualified_name = f"{parent_qualified_name}.{name}"
        args = _argument_names(node.get("args"))
        card_id = self._add_card(
            kind="function",
            title=name,
            qualified_name=qualified_name,
            level=level,
            parent_id=parent_id,
            node=node,
            detail={
                "async": bool(node.get("async", False)),
                "args": args,
                "returns": _value_name(node.get("returns")),
                "docstring": node.get("docstring"),
                "decorators": [_value_name(item) for item in _list(node.get("decorators"))],
            },
        )
        local_name = self._local_name(qualified_name)
        self.function_cards_by_local_name[local_name] = card_id
        self._visit_body(node.get("body", []), card_id, qualified_name, level + 1)

    def _visit_block(
        self,
        node: Mapping[str, Any],
        parent_id: str,
        parent_qualified_name: str,
        level: int,
    ) -> None:
        node_type = _string(node.get("type"), "block")
        line = _line(node)
        qualified_name = f"{parent_qualified_name}.{node_type}@L{line}"
        card_id = self._add_card(
            kind="block",
            title=node_type,
            qualified_name=qualified_name,
            level=level,
            parent_id=parent_id,
            node=node,
            detail={
                "node_type": node_type,
                "test": _value_name(node.get("test")),
                "target": _value_name(node.get("target")),
                "iter": _value_name(node.get("iter")),
            },
        )

        for field in _BODY_FIELDS:
            self._visit_body(node.get(field, []), card_id, qualified_name, level + 1)

        handlers = node.get("handlers")
        if isinstance(handlers, list):
            for handler in handlers:
                if isinstance(handler, Mapping):
                    self._visit_node(handler, card_id, qualified_name, level + 1)

    def _add_statement_card(
        self,
        node: Mapping[str, Any],
        parent_id: str,
        parent_qualified_name: str,
        level: int,
    ) -> str:
        node_type = _string(node.get("type"), "statement")
        line = _line(node)
        qualified_name = f"{parent_qualified_name}@L{line}"
        return self._add_card(
            kind="statement",
            title=node_type,
            qualified_name=qualified_name,
            level=level,
            parent_id=parent_id,
            node=node,
            detail={
                "node_type": node_type,
                "summary": _statement_summary(node),
            },
        )

    def _add_card(
        self,
        *,
        kind: str,
        title: str,
        qualified_name: str,
        level: int,
        parent_id: str | None,
        node: Mapping[str, Any],
        detail: Mapping[str, Any] | None = None,
    ) -> str:
        identity = self._unique_identity(kind, qualified_name)
        card_id = f"{kind}:{identity}"
        clean_detail = _clean_dict(dict(detail or {}))
        trace = _clean_dict(
            {
                "path": self._trace_path(node),
                "line": node.get("line"),
                "end_line": node.get("end_line"),
            }
        )
        card = _clean_dict(
            {
                "id": card_id,
                "kind": kind,
                "title": title,
                "level": level,
                "parent_id": parent_id,
                "children": [],
                "qualified_name": identity,
                "surface": _clean_dict(
                    {
                        "title": title,
                        "subtitle": f"{kind} · L{trace.get('line')}"
                        if trace.get("line") is not None
                        else kind,
                    }
                ),
                "detail": clean_detail,
                "trace": trace,
            }
        )
        card["children"] = []
        self.cards.append(card)
        self.card_index[card_id] = card

        if parent_id is not None and parent_id in self.card_index:
            self.card_index[parent_id]["children"].append(card_id)
            self._add_relation("contains", source_id=parent_id, target_id=card_id, node=node)

        return card_id

    def _add_import_relations(self, node: Mapping[str, Any], source_id: str) -> None:
        for target in _import_targets(node):
            self._add_relation("imports", source_id=source_id, target=target, node=node)

    def _add_call_relations(self, tree: Mapping[str, Any]) -> None:
        try:
            call_graph = _semantic_ast.build_call_graph(tree)
        except Exception:
            return

        for edge in _list(call_graph.get("edges")):
            if not isinstance(edge, Mapping):
                continue
            caller = edge.get("caller")
            callee = edge.get("callee")
            if not isinstance(caller, str) or not isinstance(callee, str):
                continue
            source_id = self.function_cards_by_local_name.get(caller)
            target_id = self.function_cards_by_local_name.get(callee)
            if source_id and target_id:
                self._add_relation(
                    "calls",
                    source_id=source_id,
                    target_id=target_id,
                    label=edge.get("call"),
                    node=None,
                )

    def _add_relation(
        self,
        kind: str,
        *,
        source_id: str,
        target_id: str | None = None,
        target: str | None = None,
        label: Any = None,
        node: Mapping[str, Any] | None,
    ) -> None:
        relation = _clean_dict(
            {
                "kind": kind,
                "source_id": source_id,
                "target_id": target_id,
                "target": target,
                "label": label,
                "trace": _clean_dict(
                    {
                        "path": self._trace_path(node) if node is not None else None,
                        "line": node.get("line") if node is not None else None,
                        "end_line": node.get("end_line") if node is not None else None,
                    }
                ),
            }
        )
        key = (
            relation.get("kind"),
            relation.get("source_id"),
            relation.get("target_id"),
            relation.get("target"),
            relation.get("label"),
            json.dumps(relation.get("trace", {}), sort_keys=True),
        )
        if key in self.relation_keys:
            return
        self.relation_keys.add(key)
        self.relations.append(relation)

    def _unique_identity(self, kind: str, qualified_name: str) -> str:
        base = _normalize_identity(qualified_name)
        key = f"{kind}:{base}"
        self.id_counts[key] += 1
        if self.id_counts[key] == 1:
            return base
        return f"{base}#{self.id_counts[key]}"

    def _trace_path(self, node: Mapping[str, Any] | None) -> str | None:
        if node is not None and isinstance(node.get("path"), str):
            return node["path"]
        for card in self.cards:
            trace = card.get("trace")
            if isinstance(trace, Mapping) and isinstance(trace.get("path"), str):
                return trace["path"]
        return None

    def _local_name(self, qualified_name: str) -> str:
        prefix = f"{self.module_qualified_name}."
        if qualified_name.startswith(prefix):
            return qualified_name[len(prefix):]
        return qualified_name

    def _stats(self) -> dict[str, Any]:
        card_kinds = Counter(card["kind"] for card in self.cards)
        relation_kinds = Counter(relation["kind"] for relation in self.relations)
        return {
            "cards": len(self.cards),
            "relations": len(self.relations),
            "card_kinds": dict(sorted(card_kinds.items())),
            "relation_kinds": dict(sorted(relation_kinds.items())),
        }


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

    if operation == "build_cards" and "tree" not in params:
        raise ValueError("build_cards requires tree")
    if operation == "cards_from_source" and "source" not in params:
        raise ValueError("cards_from_source requires source")
    if operation == "cards_from_file" and "path" not in params:
        raise ValueError("cards_from_file requires path")
    if operation in {"summary_view", "tree_view", "card_view"} and "cards" not in params:
        raise ValueError(f"{operation} requires cards")
    if operation == "card_view" and "card_id" not in params:
        raise ValueError("card_view requires card_id")

    return operation, params


def _module_qualified_name(path_value: Any) -> str:
    if not isinstance(path_value, str) or not path_value:
        return "module"

    path = Path(path_value)
    if path.is_absolute():
        try:
            path = path.relative_to(_REPO_ROOT)
        except ValueError:
            return _sanitize_part(path.stem)

    parts = list(path.with_suffix("").parts)
    if "file-tools" in parts:
        parts = parts[parts.index("file-tools") + 1:]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts:
        return "module"
    return ".".join(_sanitize_part(part) for part in parts if part)


def _sanitize_part(value: str) -> str:
    sanitized = re.sub(r"\W+", "_", value).strip("_")
    return sanitized or "module"


def _normalize_identity(value: str) -> str:
    return re.sub(r"\s+", "_", value.strip()) or "anonymous"


def _line(node: Mapping[str, Any]) -> int:
    value = node.get("line")
    return value if isinstance(value, int) else 0


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string(value: Any, fallback: str) -> str:
    return value if isinstance(value, str) and value else fallback


def _argument_names(args_node: Any) -> list[str]:
    if not isinstance(args_node, Mapping):
        return []

    names: list[str] = []
    for arg in _list(args_node.get("positional_only")):
        name = _argument_name(arg)
        if name:
            names.append(name)
    for arg in _list(args_node.get("positional_or_keyword")):
        name = _argument_name(arg)
        if name:
            names.append(name)

    vararg = _argument_name(args_node.get("vararg"))
    if vararg:
        names.append(f"*{vararg}")

    for arg in _list(args_node.get("keyword_only")):
        name = _argument_name(arg)
        if name:
            names.append(name)

    kwarg = _argument_name(args_node.get("kwarg"))
    if kwarg:
        names.append(f"**{kwarg}")

    return names


def _argument_name(node: Any) -> str | None:
    if isinstance(node, Mapping) and isinstance(node.get("name"), str):
        return node["name"]
    return None


def _value_name(node: Any) -> str | None:
    if node is None:
        return None
    if isinstance(node, str):
        return node
    if not isinstance(node, Mapping):
        return repr(node)

    node_type = node.get("type")
    if node_type == "name":
        return _string(node.get("id"), "")
    if node_type == "attribute":
        base = _value_name(node.get("value"))
        attr = _string(node.get("attr"), "")
        return f"{base}.{attr}" if base and attr else attr or base
    if node_type == "constant":
        return repr(node.get("value"))
    if node_type == "call":
        func = _value_name(node.get("func"))
        return f"{func}()" if func else "call"
    if node_type == "binop":
        left = _value_name(node.get("left"))
        right = _value_name(node.get("right"))
        operator = _string(node.get("operator"), "?")
        return f"{left} {operator} {right}"
    if node_type == "subscript":
        value = _value_name(node.get("value"))
        return f"{value}[...]" if value else "subscript"

    name = node.get("name")
    if isinstance(name, str):
        return name
    value = node.get("value")
    if value is not None:
        return _value_name(value)
    return _string(node_type, "value")


def _statement_summary(node: Mapping[str, Any]) -> str | None:
    node_type = node.get("type")
    if node_type in {"assignment", "annotated_assignment"}:
        targets = node.get("targets")
        if isinstance(targets, list):
            names = [_value_name(target) for target in targets]
            return "assigns " + ", ".join(name for name in names if name)
        target = _value_name(node.get("target"))
        return f"assigns {target}" if target else "assignment"
    if node_type == "return":
        value = _value_name(node.get("value"))
        return f"returns {value}" if value else "returns"
    if node_type in {"import", "import_from"}:
        targets = _import_targets(node)
        return "imports " + ", ".join(targets) if targets else "imports"
    if node_type == "expression_statement":
        value = _value_name(node.get("value"))
        return value
    return _string(node_type, "statement")


def _import_targets(node: Mapping[str, Any]) -> list[str]:
    node_type = node.get("type")
    names = _list(node.get("names"))
    if node_type == "import":
        return [
            _string(alias.get("name"), "")
            for alias in names
            if isinstance(alias, Mapping) and alias.get("name")
        ]
    if node_type == "import_from":
        module = "." * int(node.get("level") or 0) + _string(node.get("module"), "")
        targets = []
        for alias in names:
            if isinstance(alias, Mapping) and alias.get("name"):
                name = _string(alias.get("name"), "")
                targets.append(f"{module}.{name}" if module else name)
        return targets
    return []


def _clean_dict(data: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in data.items()
        if value is not None and value != [] and value != {}
    }


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
    if (response.get("error") or {}).get("type") in {
        "TypeError",
        "ValueError",
        "FileNotFoundError",
        "SyntaxError",
        "IndentationError",
        "JSONDecodeError",
    }:
        return 2
    return 3


if __name__ == "__main__":
    main()
