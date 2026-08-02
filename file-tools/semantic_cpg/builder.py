"""Merge semantic AST, CFG, DFG, and call graph results into a Semantic CPG."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from schema import CPGEdge, CPGNode, CPGWarning


SemanticNode = Mapping[str, Any]


def build_cpg(
    *,
    tree: Any,
    cfg: Any | None = None,
    dfg: Any | None = None,
    call_graph: Any | None = None,
) -> dict[str, Any]:
    """Build a Semantic Code Property Graph from existing analysis outputs."""
    if not isinstance(tree, Mapping):
        raise TypeError("tree must be a dictionary")
    if tree.get("type") != "module":
        raise ValueError("tree must be a semantic_ast module node")
    if cfg is not None and (not isinstance(cfg, Mapping) or cfg.get("type") != "control_flow_graph"):
        raise ValueError("cfg must be a semantic_cfg control_flow_graph result")
    if dfg is not None and (not isinstance(dfg, Mapping) or dfg.get("type") != "data_flow_graph"):
        raise ValueError("dfg must be a semantic_dfg data_flow_graph result")
    if call_graph is not None and (not isinstance(call_graph, Mapping) or call_graph.get("type") != "call_graph"):
        raise ValueError("call_graph must be a semantic_ast call_graph result")

    builder = _CPGBuilder(path=_string_or_none(tree.get("path")))
    builder.add_ast(tree)
    if cfg is not None:
        builder.add_cfg(cfg)
    if dfg is not None:
        builder.add_dfg(dfg)
    if call_graph is not None:
        builder.add_call_graph(call_graph)
    builder.add_correspondences()
    return builder.to_result(language=_string(tree.get("language"), "python"))


class _CPGBuilder:
    """Stateful Semantic CPG merger."""

    def __init__(self, *, path: str | None) -> None:
        self.path = path
        self.nodes_by_id: dict[str, CPGNode] = {}
        self.edges: list[CPGEdge] = []
        self.edge_keys: set[tuple[str, str, str, str | None]] = set()
        self.warnings: list[CPGWarning] = []
        self.module_id: str | None = None
        self.functions: dict[str, str] = {}
        self.classes: dict[str, str] = {}
        self.ast_nodes_by_function: dict[str, list[dict[str, Any]]] = {}
        self.cfg_nodes_by_function: dict[str, list[dict[str, Any]]] = {}
        self.dfg_nodes_by_function: dict[str, list[dict[str, Any]]] = {}
        self.cfg_id_map: dict[str, str] = {}
        self.dfg_id_map: dict[str, str] = {}

    def add_ast(self, tree: SemanticNode) -> None:
        """Add semantic AST module, class, function, and statement nodes."""
        module_name = _module_name(self.path) or "module"
        self.module_id = _cpg_id("ast", "module", module_name)
        self._add_node(
            CPGNode(
                id=self.module_id,
                kind="module",
                label=module_name,
                scope=module_name,
                trace=_trace(self.path, tree.get("line"), tree.get("end_line")),
                origin={"tool": "semantic_ast", "id": module_name, "kind": "module"},
            )
        )
        self._walk_ast_body(tree.get("body", []), parent_id=self.module_id, scope=[module_name])

    def add_cfg(self, cfg: SemanticNode) -> None:
        """Add semantic_cfg nodes and control-flow edges."""
        self._carry_warnings(cfg, source="semantic_cfg")
        for function in _list(cfg.get("functions")):
            if not isinstance(function, Mapping):
                continue
            function_id = _string_or_none(function.get("qualified_name"))
            if not function_id:
                continue
            function_cpg_id = self._ensure_function(function_id, function)
            for node in _list(function.get("nodes")):
                if not isinstance(node, Mapping):
                    continue
                origin_id = _string_or_none(node.get("id"))
                if not origin_id:
                    continue
                cpg_id = _cpg_id("cfg", origin_id)
                self.cfg_id_map[origin_id] = cpg_id
                record = {
                    "id": cpg_id,
                    "origin_id": origin_id,
                    "function_id": function_id,
                    "line": _int_or_none(node.get("line")),
                    "end_line": _int_or_none(node.get("end_line")),
                }
                self.cfg_nodes_by_function.setdefault(function_id, []).append(record)
                self._add_node(
                    CPGNode(
                        id=cpg_id,
                        kind=_cfg_node_kind(node.get("kind")),
                        label=_string(node.get("label"), _string(node.get("kind"), "cfg node")),
                        scope=function_id,
                        trace=_trace(function.get("path") or self.path, node.get("line"), node.get("end_line")),
                        origin={"tool": "semantic_cfg", "id": origin_id, "kind": node.get("kind")},
                        properties=_clean_dict(
                            {
                                "original_kind": node.get("kind"),
                                "depth": node.get("depth"),
                            }
                        ),
                    )
                )
                self._add_edge(
                    function_cpg_id,
                    cpg_id,
                    "has_cfg_node",
                    origin={"tool": "semantic_cpg", "reason": "function_scope"},
                )

            for edge in _list(function.get("edges")):
                if not isinstance(edge, Mapping):
                    continue
                source = self.cfg_id_map.get(_string(edge.get("source"), ""))
                target = self.cfg_id_map.get(_string(edge.get("target"), ""))
                if not source or not target:
                    continue
                self._add_edge(
                    source,
                    target,
                    f"control_{_string(edge.get('kind'), 'edge')}",
                    condition=_string_or_none(edge.get("condition")),
                    trace=_trace(function.get("path") or self.path, edge.get("lineno"), edge.get("lineno")),
                    origin={
                        "tool": "semantic_cfg",
                        "kind": edge.get("kind"),
                    },
                )

    def add_dfg(self, dfg: SemanticNode) -> None:
        """Add semantic_dfg nodes and data-flow edges."""
        self._carry_warnings(dfg, source="semantic_dfg")
        for function in _list(dfg.get("functions")):
            if not isinstance(function, Mapping):
                continue
            function_id = _string_or_none(function.get("qualified_name"))
            if not function_id:
                continue
            function_cpg_id = self._ensure_function(function_id, function)
            for node in _list(function.get("nodes")):
                if not isinstance(node, Mapping):
                    continue
                origin_id = _string_or_none(node.get("id"))
                if not origin_id:
                    continue
                cpg_id = _cpg_id("dfg", origin_id)
                self.dfg_id_map[origin_id] = cpg_id
                record = {
                    "id": cpg_id,
                    "origin_id": origin_id,
                    "function_id": function_id,
                    "line": _int_or_none(node.get("lineno")),
                    "end_line": _int_or_none(node.get("lineno")),
                }
                self.dfg_nodes_by_function.setdefault(function_id, []).append(record)
                self._add_node(
                    CPGNode(
                        id=cpg_id,
                        kind=_dfg_node_kind(node.get("kind")),
                        label=_string(node.get("name"), _string(node.get("kind"), "dfg node")),
                        scope=function_id,
                        trace=_trace(function.get("path") or self.path, node.get("lineno"), node.get("lineno")),
                        origin={"tool": "semantic_dfg", "id": origin_id, "kind": node.get("kind")},
                        properties=_clean_dict(
                            {
                                "original_kind": node.get("kind"),
                                "flow_level": node.get("flow_level"),
                                "depth": node.get("depth"),
                            }
                        ),
                    )
                )
                self._add_edge(
                    function_cpg_id,
                    cpg_id,
                    "has_dfg_node",
                    origin={"tool": "semantic_cpg", "reason": "function_scope"},
                )

            for edge in _list(function.get("edges")):
                if not isinstance(edge, Mapping):
                    continue
                source = self.dfg_id_map.get(_string(edge.get("source"), ""))
                target = self.dfg_id_map.get(_string(edge.get("target"), ""))
                if not source or not target:
                    continue
                self._add_edge(
                    source,
                    target,
                    f"data_{_string(edge.get('kind'), 'edge')}",
                    trace=_trace(function.get("path") or self.path, edge.get("lineno"), edge.get("lineno")),
                    origin={
                        "tool": "semantic_dfg",
                        "kind": edge.get("kind"),
                        "operation": edge.get("operation"),
                    },
                )

    def add_call_graph(self, call_graph: SemanticNode) -> None:
        """Add call graph local call edges between function CPG nodes."""
        for node in _list(call_graph.get("nodes")):
            if isinstance(node, Mapping):
                function_id = _string_or_none(node.get("qualified_name")) or _string_or_none(node.get("id"))
                if function_id:
                    self._ensure_function(self._resolve_function_id(function_id), node)

        for edge in _list(call_graph.get("edges")):
            if not isinstance(edge, Mapping):
                continue
            caller = _string_or_none(edge.get("caller"))
            callee = _string_or_none(edge.get("callee"))
            if not caller or not callee:
                continue
            source = self._ensure_function(self._resolve_function_id(caller), {})
            target = self._ensure_function(self._resolve_function_id(callee), {})
            self._add_edge(
                source,
                target,
                "calls",
                origin={"tool": "call_graph", "call": edge.get("call")},
            )

    def add_correspondences(self) -> None:
        """Add cross-analysis links for nodes that share source spans."""
        function_ids = set(self.ast_nodes_by_function) | set(self.cfg_nodes_by_function) | set(self.dfg_nodes_by_function)
        for function_id in sorted(function_ids):
            ast_nodes = self.ast_nodes_by_function.get(function_id, [])
            cfg_nodes = self.cfg_nodes_by_function.get(function_id, [])
            dfg_nodes = self.dfg_nodes_by_function.get(function_id, [])

            for ast_node in ast_nodes:
                for cfg_node in cfg_nodes:
                    if _spans_overlap(ast_node, cfg_node):
                        self._add_edge(
                            ast_node["id"],
                            cfg_node["id"],
                            "corresponds_to",
                            origin={"tool": "semantic_cpg", "reason": "same_source_span"},
                        )
                for dfg_node in dfg_nodes:
                    if _spans_overlap(ast_node, dfg_node):
                        self._add_edge(
                            ast_node["id"],
                            dfg_node["id"],
                            "corresponds_to",
                            origin={"tool": "semantic_cpg", "reason": "same_source_span"},
                        )

            for cfg_node in cfg_nodes:
                for dfg_node in dfg_nodes:
                    if _spans_overlap(cfg_node, dfg_node):
                        self._add_edge(
                            cfg_node["id"],
                            dfg_node["id"],
                            "corresponds_to",
                            origin={"tool": "semantic_cpg", "reason": "same_source_span"},
                        )

    def to_result(self, *, language: str) -> dict[str, Any]:
        """Return the final Semantic CPG result."""
        nodes = sorted(
            (node.to_dict() for node in self.nodes_by_id.values()),
            key=lambda node: (node.get("trace", {}).get("line", 0), node["kind"], node["id"]),
        )
        edges = sorted(
            (edge.to_dict() for edge in self.edges),
            key=lambda edge: (
                edge.get("trace", {}).get("line", 0),
                edge["kind"],
                edge["source"],
                edge["target"],
            ),
        )
        warnings = sorted(
            (warning.to_dict() for warning in self.warnings),
            key=lambda warning: (warning.get("source", ""), warning.get("lineno", 0), warning.get("kind", "")),
        )
        return {
            "type": "semantic_code_property_graph",
            "language": language,
            "path": self.path,
            "nodes": nodes,
            "edges": edges,
            "warnings": warnings,
            "provenance": {
                "tools": [
                    "semantic_ast",
                    "semantic_cfg",
                    "semantic_dfg",
                    "call_graph",
                ],
                "merge_tool": "semantic_cpg",
            },
            "stats": {
                "nodes": len(nodes),
                "edges": len(edges),
                "functions": len(self.functions),
                "classes": len(self.classes),
                "warnings": len(warnings),
            },
        }

    def _walk_ast_body(self, body: Any, *, parent_id: str, scope: list[str]) -> None:
        for item in _list(body):
            if not isinstance(item, Mapping):
                continue
            node_type = item.get("type")
            if node_type == "class":
                name = _string(item.get("name"), "anonymous_class")
                class_id = ".".join([*scope, name])
                cpg_id = _cpg_id("ast", "class", class_id)
                self.classes[class_id] = cpg_id
                self._add_node(
                    CPGNode(
                        id=cpg_id,
                        kind="class",
                        label=name,
                        scope=".".join(scope),
                        trace=_trace(self.path, item.get("line"), item.get("end_line")),
                        origin={"tool": "semantic_ast", "id": class_id, "kind": "class"},
                    )
                )
                self._add_edge(parent_id, cpg_id, "contains", origin={"tool": "semantic_ast"})
                self._walk_ast_body(item.get("body", []), parent_id=cpg_id, scope=[*scope, name])
                continue
            if node_type == "function":
                name = _string(item.get("name"), "anonymous_function")
                function_id = ".".join([*scope, name])
                cpg_id = self._ensure_function(function_id, item)
                self._add_edge(parent_id, cpg_id, "contains", origin={"tool": "semantic_ast"})
                self._walk_statement_tree(
                    item.get("body", []),
                    parent_id=cpg_id,
                    function_id=function_id,
                    depth=1,
                )
                self._walk_ast_body(item.get("body", []), parent_id=cpg_id, scope=[*scope, name])

    def _walk_statement_tree(
        self,
        node: Any,
        *,
        parent_id: str,
        function_id: str,
        depth: int,
    ) -> None:
        for index, statement in enumerate(_list(node), start=1):
            if not isinstance(statement, Mapping):
                continue
            if statement.get("type") in {"function", "class"}:
                continue
            ast_id = _cpg_id(
                "ast",
                function_id,
                _string(statement.get("type"), "statement"),
                str(_int_or_none(statement.get("line")) or 0),
                str(index),
            )
            self._add_node(
                CPGNode(
                    id=ast_id,
                    kind="ast_statement",
                    label=_string(statement.get("type"), "statement"),
                    scope=function_id,
                    trace=_trace(self.path, statement.get("line"), statement.get("end_line")),
                    origin={"tool": "semantic_ast", "kind": statement.get("type")},
                    properties={"depth": depth},
                )
            )
            self.ast_nodes_by_function.setdefault(function_id, []).append(
                {
                    "id": ast_id,
                    "function_id": function_id,
                    "line": _int_or_none(statement.get("line")),
                    "end_line": _int_or_none(statement.get("end_line")),
                }
            )
            self._add_edge(parent_id, ast_id, "contains", origin={"tool": "semantic_ast"})
            self._walk_statement_tree(
                statement.get("body", []),
                parent_id=ast_id,
                function_id=function_id,
                depth=depth + 1,
            )
            self._walk_statement_tree(
                statement.get("orelse", []),
                parent_id=ast_id,
                function_id=function_id,
                depth=depth + 1,
            )
            self._walk_statement_tree(
                statement.get("finalbody", []),
                parent_id=ast_id,
                function_id=function_id,
                depth=depth + 1,
            )
            for handler in _list(statement.get("handlers")):
                if isinstance(handler, Mapping):
                    self._walk_statement_tree(
                        handler.get("body", []),
                        parent_id=ast_id,
                        function_id=function_id,
                        depth=depth + 1,
                    )

    def _ensure_function(self, function_id: str, source: Mapping[str, Any]) -> str:
        existing = self.functions.get(function_id)
        if existing:
            return existing
        cpg_id = _cpg_id("ast", "function", function_id)
        self.functions[function_id] = cpg_id
        self._add_node(
            CPGNode(
                id=cpg_id,
                kind="function",
                label=_string(source.get("name"), function_id.rsplit(".", 1)[-1]),
                scope=function_id.rsplit(".", 1)[0] if "." in function_id else None,
                trace=_trace(source.get("path") or self.path, source.get("line"), source.get("end_line")),
                origin={"tool": "semantic_ast", "id": function_id, "kind": "function"},
            )
        )
        return cpg_id

    def _resolve_function_id(self, function_id: str) -> str:
        if function_id in self.functions:
            return function_id
        matches = [
            existing
            for existing in self.functions
            if existing == function_id or existing.endswith(f".{function_id}")
        ]
        if len(matches) == 1:
            return matches[0]
        return function_id

    def _add_node(self, node: CPGNode) -> None:
        if node.id not in self.nodes_by_id:
            self.nodes_by_id[node.id] = node

    def _add_edge(
        self,
        source: str,
        target: str,
        kind: str,
        *,
        origin: dict[str, Any],
        trace: dict[str, Any] | None = None,
        condition: str | None = None,
        properties: dict[str, Any] | None = None,
    ) -> None:
        key = (source, target, kind, condition)
        if key in self.edge_keys:
            return
        self.edge_keys.add(key)
        self.edges.append(
            CPGEdge(
                source=source,
                target=target,
                kind=kind,
                condition=condition,
                trace=trace,
                origin=_clean_dict(origin),
                properties=properties or {},
            )
        )

    def _carry_warnings(self, analysis: SemanticNode, *, source: str) -> None:
        for warning in _list(analysis.get("warnings")):
            if not isinstance(warning, Mapping):
                continue
            self.warnings.append(
                CPGWarning(
                    kind=_string(warning.get("kind"), "Warning"),
                    message=_string(warning.get("message"), "Analysis warning"),
                    source=source,
                    lineno=_int_or_none(warning.get("lineno")),
                )
            )


def _cfg_node_kind(kind: Any) -> str:
    value = _string(kind, "node")
    if value == "entry":
        return "control_entry"
    if value == "exit":
        return "control_exit"
    if value == "branch":
        return "control_branch"
    if value == "loop":
        return "control_loop"
    if value == "join":
        return "control_join"
    if value == "return":
        return "control_return"
    if value == "raise":
        return "control_raise"
    if value in {"break", "continue"}:
        return "control_jump"
    return "control_statement"


def _dfg_node_kind(kind: Any) -> str:
    value = _string(kind, "value")
    if value == "parameter":
        return "value_parameter"
    if value == "binding":
        return "value_binding"
    if value == "return_value":
        return "value_return"
    if value == "literal":
        return "value_literal"
    if value == "call_result":
        return "value_call_result"
    if value == "unknown":
        return "value_unknown"
    return "value"


def _trace(path: Any, line: Any, end_line: Any) -> dict[str, Any]:
    return _clean_dict(
        {
            "path": path if isinstance(path, str) and path else None,
            "line": _int_or_none(line),
            "end_line": _int_or_none(end_line),
        }
    )


def _spans_overlap(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    left_line = _int_or_none(left.get("line"))
    right_line = _int_or_none(right.get("line"))
    if left_line is None or right_line is None:
        return False
    left_end = _int_or_none(left.get("end_line")) or left_line
    right_end = _int_or_none(right.get("end_line")) or right_line
    return left_line <= right_end and right_line <= left_end


def _module_name(path: str | None) -> str | None:
    if not path:
        return None
    name = path.rsplit("/", 1)[-1]
    if name.endswith(".py"):
        name = name[:-3]
    return name.replace("-", "_") or None


def _cpg_id(*parts: str) -> str:
    return "cpg:" + ":".join(_safe_id(part) for part in parts if part)


def _safe_id(value: str) -> str:
    result = []
    for character in value:
        if character.isalnum() or character in {"_", "."}:
            result.append(character)
        else:
            result.append("_")
    return "".join(result).strip("_") or "node"


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string(value: Any, default: str) -> str:
    return value if isinstance(value, str) and value else default


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    return value if isinstance(value, int) else None


def _clean_dict(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: item
        for key, item in value.items()
        if item is not None and item != [] and item != {}
    }
