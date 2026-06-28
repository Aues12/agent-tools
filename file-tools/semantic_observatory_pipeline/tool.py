"""Orchestrate semantic analysis artifacts for Semantic Observatory UI."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from types import ModuleType
from typing import Any


_TOOL_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TOOL_DIR.parents[1]
_OPERATIONS = {"analyze_source", "analyze_file", "adapt_for_ui"}

PHASE_SYMBOLS = {
    "Discovery": "🜁",
    "Understanding": "▽",
    "Transformation": "△",
    "Manifestation": "🜃",
}

PHASE_BY_ROLE = {
    "Explorer": "Discovery",
    "Locator": "Discovery",
    "Parser": "Understanding",
    "Analyzer": "Understanding",
    "Validator": "Understanding",
    "Container": "Understanding",
    "Transformer": "Transformation",
    "Aggregator": "Transformation",
    "Builder": "Manifestation",
    "Renderer": "Manifestation",
    "Executor": "Manifestation",
    "Statement": "Manifestation",
}


def _load_module(module_name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        try:
            sys.path.remove(str(path.parent))
        except ValueError:
            pass
    return module


_semantic_ast = _load_module(
    "semantic_observatory_pipeline_semantic_ast",
    _TOOL_DIR.parent / "semantic_ast" / "tool.py",
)
_semantic_cards = _load_module(
    "semantic_observatory_pipeline_semantic_cards",
    _TOOL_DIR.parent / "semantic_cards" / "tool.py",
)
_semantic_dfg = _load_module(
    "semantic_observatory_pipeline_semantic_dfg",
    _TOOL_DIR.parent / "semantic_dfg" / "tool.py",
)


def analyze_source(
    source: str,
    path: str | None = None,
    display_path: str | None = None,
    include_statements: bool = False,
    include_blocks: bool = False,
) -> dict[str, Any]:
    """Analyze Python source and return artifacts plus Flat View UI data."""
    if not isinstance(source, str) or not source.strip():
        raise ValueError("source must be a non-empty string")

    tree = _semantic_ast.parse_source(
        source=source,
        path=path,
        include_source=False,
    )
    cards = _semantic_cards.build_cards(
        tree,
        include_statements=include_statements,
        include_blocks=include_blocks,
    )
    dfg = _semantic_dfg.build_dfg(tree)
    return _analysis_payload(
        source_name=path,
        display_path=display_path,
        tree=tree,
        cards=cards,
        dfg=dfg,
    )


def analyze_file(
    path: str | Path,
    encoding: str = "utf-8",
    include_statements: bool = False,
    include_blocks: bool = False,
) -> dict[str, Any]:
    """Analyze a Python file and return artifacts plus Flat View UI data."""
    source_path = Path(path)
    source = source_path.read_text(encoding=encoding)
    return analyze_source(
        source=source,
        path=str(source_path),
        include_statements=include_statements,
        include_blocks=include_blocks,
    )


def adapt_for_ui(
    semantic_cards: Mapping[str, Any],
    data_flow_graph: Mapping[str, Any] | None = None,
    display_path: str | None = None,
) -> dict[str, Any]:
    """Adapt semantic cards and optional DFG output to Flat View UI data."""
    if not isinstance(semantic_cards, Mapping):
        raise TypeError("semantic_cards must be a dictionary")
    if semantic_cards.get("type") != "semantic_cards":
        raise ValueError("semantic_cards must be a semantic_cards artifact")
    dfg = data_flow_graph if isinstance(data_flow_graph, Mapping) else {}

    relation_index = _relations_by_source(semantic_cards.get("relations", []))
    dfg_index = _dfg_by_function(dfg)
    source_cards = [
        card
        for card in _list(semantic_cards.get("cards"))
        if isinstance(card, Mapping)
    ]
    visible_card_ids = {
        card.get("id")
        for card in source_cards
        if isinstance(card.get("id"), str)
    }
    cards = [
        _adapt_card(
            card,
            _visible_relations(relation_index.get(card.get("id"), []), visible_card_ids),
            dfg_index,
            display_path=display_path,
        )
        for card in source_cards
    ]

    return {
        "type": "semantic_observatory_ui_data",
        "phaseSymbols": PHASE_SYMBOLS,
        "semanticCards": cards,
        "filterOptions": _filter_options(cards),
        "stats": {
            "cards": len(cards),
            "relations": sum(len(card.get("relations", [])) for card in cards),
            "dfgFunctions": len(_list(dfg.get("functions"))),
        },
    }


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a semantic_observatory_pipeline operation."""
    try:
        operation, params = _parse_request(input_data)
        if operation == "analyze_source":
            result = analyze_source(
                source=params["source"],
                path=params.get("path"),
                display_path=params.get("display_path"),
                include_statements=bool(params.get("include_statements", False)),
                include_blocks=bool(params.get("include_blocks", False)),
            )
            message = "Analyzed Python source for Semantic Observatory"
        elif operation == "analyze_file":
            result = analyze_file(
                path=params["path"],
                encoding=params.get("encoding", "utf-8"),
                include_statements=bool(params.get("include_statements", False)),
                include_blocks=bool(params.get("include_blocks", False)),
            )
            message = "Analyzed Python file for Semantic Observatory"
        elif operation == "adapt_for_ui":
            result = adapt_for_ui(
                semantic_cards=params["semantic_cards"],
                data_flow_graph=params.get("data_flow_graph"),
                display_path=params.get("display_path"),
            )
            message = "Adapted semantic artifacts for Semantic Observatory UI"
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


def _analysis_payload(
    *,
    source_name: str | None,
    display_path: str | None,
    tree: Mapping[str, Any],
    cards: Mapping[str, Any],
    dfg: Mapping[str, Any],
) -> dict[str, Any]:
    ui = adapt_for_ui(cards, dfg, display_path=display_path)
    display_name = display_path or Path(str(tree.get("path") or source_name or "uploaded.py")).name
    return {
        "type": "semantic_observatory_analysis",
        "language": tree.get("language", "python"),
        "source": {
            "path": display_path or tree.get("path") or source_name,
            "displayName": display_name,
        },
        "artifacts": {
            "semantic_ast": tree,
            "semantic_cards": cards,
            "data_flow_graph": dfg,
        },
        "ui": ui,
        "stats": {
            "semanticAstNodes": _int(tree.get("stats", {}).get("nodes"), 0)
            if isinstance(tree.get("stats"), Mapping)
            else 0,
            "cards": ui["stats"]["cards"],
            "relations": ui["stats"]["relations"],
            "dfgFunctions": ui["stats"]["dfgFunctions"],
        },
    }


def _adapt_card(
    card: Mapping[str, Any],
    relations: list[Mapping[str, Any]],
    dfg_index: dict[str, Mapping[str, Any]],
    display_path: str | None = None,
) -> dict[str, Any]:
    role = _infer_role(card)
    phase = PHASE_BY_ROLE.get(role, "Understanding")
    trace = card.get("trace") if isinstance(card.get("trace"), Mapping) else {}
    path = _string(trace.get("path"), "")
    qualified_name = _string(card.get("qualified_name"), _string(card.get("id"), "card"))
    dfg = _adapt_dfg(
        dfg_index.get(_string(card.get("id"), ""))
        or dfg_index.get(qualified_name)
        or dfg_index.get(_line_function_key(card))
    )

    adapted = {
        "id": _string(card.get("id"), qualified_name),
        "kind": _string(card.get("kind"), "card"),
        "title": _string(card.get("title"), qualified_name.rsplit(".", 1)[-1]),
        "depth": _int(card.get("depth"), _int(card.get("level"), 0)),
        "level": _int(card.get("level"), 0),
        "summary": _summary(card),
        "role": role,
        "phase": phase,
        "module": _module_name(card, path),
        "source": {
            "path": display_path or path,
            "displayPath": display_path or _display_path(path),
            "line": _int(trace.get("line"), 1),
            "endLine": _int(trace.get("end_line"), _int(trace.get("line"), 1)),
        },
        "relations": [_adapt_relation(relation) for relation in relations],
    }
    if dfg is not None:
        adapted["dfg"] = dfg
    return adapted


def _adapt_dfg(graph: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if not graph:
        return None
    nodes = _list(graph.get("nodes"))
    name_by_id = {
        _string(node.get("id"), ""): _string(node.get("name"), _string(node.get("id"), "value"))
        for node in nodes
        if isinstance(node, Mapping)
    }
    return {
        "nodes": [
            {
                "id": _string(node.get("id"), ""),
                "name": _string(node.get("name"), "value"),
                "kind": _string(node.get("kind"), "unknown"),
                "flowLevel": _int(node.get("flow_level"), _int(node.get("flowLevel"), 0)),
                "depth": _int(node.get("depth"), 0),
            }
            for node in nodes
            if isinstance(node, Mapping)
        ],
        "edges": [
            {
                "source": name_by_id.get(_string(edge.get("source"), ""), _string(edge.get("source"), "")),
                "target": name_by_id.get(_string(edge.get("target"), ""), _string(edge.get("target"), "")),
                "operation": _string(edge.get("operation"), _string(edge.get("kind"), "depends_on")),
            }
            for edge in _list(graph.get("edges"))
            if isinstance(edge, Mapping)
        ],
    }


def _adapt_relation(relation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "kind": _string(relation.get("kind"), "related"),
        "target": _string(
            relation.get("target_id"),
            _string(relation.get("target"), "unknown"),
        ),
        "label": _string(relation.get("label"), ""),
    }


def _dfg_by_function(dfg: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for graph in _list(dfg.get("functions")):
        if not isinstance(graph, Mapping):
            continue
        graph_id = _string(graph.get("id"), "")
        qualified_name = _string(graph.get("qualified_name"), "")
        if graph_id:
            result[graph_id] = graph
        if qualified_name:
            result[qualified_name] = graph
            result[f"function:{qualified_name}"] = graph
        line_key = _line_function_key(graph)
        if line_key:
            result[line_key] = graph
    return result


def _line_function_key(item: Mapping[str, Any]) -> str:
    name = _string(item.get("name"), _string(item.get("title"), ""))
    line = item.get("line")
    if not isinstance(line, int):
        trace = item.get("trace")
        line = trace.get("line") if isinstance(trace, Mapping) else None
    if not name or not isinstance(line, int):
        return ""
    return f"{name}@L{line}"


def _relations_by_source(relations: Any) -> dict[str, list[Mapping[str, Any]]]:
    result: dict[str, list[Mapping[str, Any]]] = {}
    for relation in _list(relations):
        if not isinstance(relation, Mapping):
            continue
        source_id = relation.get("source_id")
        if isinstance(source_id, str):
            result.setdefault(source_id, []).append(relation)
    return result


def _visible_relations(
    relations: list[Mapping[str, Any]],
    visible_card_ids: set[Any],
) -> list[Mapping[str, Any]]:
    visible: list[Mapping[str, Any]] = []
    for relation in relations:
        target_id = relation.get("target_id")
        if isinstance(target_id, str) and target_id not in visible_card_ids:
            continue
        visible.append(relation)
    return visible


def _summary(card: Mapping[str, Any]) -> str:
    detail = card.get("detail") if isinstance(card.get("detail"), Mapping) else {}
    for key in ("summary", "docstring", "test"):
        value = detail.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().splitlines()[0]
    kind = _string(card.get("kind"), "card")
    title = _string(card.get("title"), kind)
    return f"{title} semantic {kind} card."


def _infer_role(card: Mapping[str, Any]) -> str:
    kind = _string(card.get("kind"), "card")
    title = _string(card.get("title"), "").lower()
    if kind in {"module", "class", "block"}:
        return "Container"
    if kind == "statement":
        if title in {"import", "import_from"}:
            return "Locator"
        return "Statement"
    if any(word in title for word in ("find", "search", "scan", "locate", "list")):
        return "Explorer"
    if any(word in title for word in ("parse", "read", "load", "extract", "collect", "get")):
        return "Parser"
    if any(word in title for word in ("validate", "check", "assert", "verify")):
        return "Validator"
    if any(word in title for word in ("transform", "convert", "normalize", "compress", "map", "calculate", "compute", "process", "apply")):
        return "Transformer"
    if any(word in title for word in ("render", "view", "display", "show", "summarize")):
        return "Renderer"
    if any(word in title for word in ("run", "execute", "main", "dispatch")):
        return "Executor"
    if any(word in title for word in ("build", "create", "generate", "make", "emit", "write", "save", "export")):
        return "Builder"
    return "Analyzer" if kind == "function" else "Container"


def _module_name(card: Mapping[str, Any], path: str) -> str:
    qualified_name = _string(card.get("qualified_name"), "")
    if "." in qualified_name:
        return qualified_name.rsplit(".", 1)[0]
    if path:
        return Path(path).stem
    return "module"


def _display_path(path: str) -> str:
    if not path:
        return "uploaded.py"
    try:
        return str(Path(path).resolve().relative_to(_REPO_ROOT))
    except Exception:
        return path


def _filter_options(cards: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {
        "kind": ["all", *_unique(card.get("kind") for card in cards)],
        "role": ["all", *_unique(card.get("role") for card in cards)],
        "phase": ["all", *_unique(card.get("phase") for card in cards)],
        "module": ["all", *_unique(card.get("module") for card in cards)],
    }


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
    if operation == "analyze_source" and "source" not in params:
        raise ValueError("analyze_source requires source")
    if operation == "analyze_file" and "path" not in params:
        raise ValueError("analyze_file requires path")
    if operation == "adapt_for_ui" and "semantic_cards" not in params:
        raise ValueError("adapt_for_ui requires semantic_cards")
    return operation, params


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
        "SyntaxError",
        "IndentationError",
        "JSONDecodeError",
    }:
        return 2
    return 3


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string(value: Any, default: str) -> str:
    return value if isinstance(value, str) and value else default


def _int(value: Any, default: int) -> int:
    return value if isinstance(value, int) else default


def _unique(values: Any) -> list[str]:
    return sorted({value for value in values if isinstance(value, str) and value})


if __name__ == "__main__":
    main()
