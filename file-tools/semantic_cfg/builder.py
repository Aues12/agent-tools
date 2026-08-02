"""Build local control-flow graphs from semantic AST dictionaries."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from schema import CFGEdge, CFGNode, CFGWarning, FunctionCFG


SemanticNode = Mapping[str, Any]


@dataclass(frozen=True)
class _LoopTargets:
    break_target: str
    continue_target: str


def build_cfg(tree: Any) -> dict[str, Any]:
    """Build deterministic local function-level CFGs from a semantic AST tree."""
    if not isinstance(tree, Mapping):
        raise TypeError("tree must be a dictionary")
    if tree.get("type") != "module":
        raise ValueError("tree must be a semantic_ast module node")

    functions = _collect_functions(tree)
    builder = _CFGBuilder(path=_string_or_none(tree.get("path")))
    function_graphs = [builder.build_function(function) for function in functions]
    warnings = [warning for graph in function_graphs for warning in graph.warnings]

    return {
        "type": "control_flow_graph",
        "language": tree.get("language", "python"),
        "path": tree.get("path"),
        "functions": [graph.to_dict() for graph in function_graphs],
        "warnings": [warning.to_dict() for warning in warnings],
        "stats": {
            "functions": len(function_graphs),
            "nodes": sum(len(graph.nodes) for graph in function_graphs),
            "edges": sum(len(graph.edges) for graph in function_graphs),
            "warnings": len(warnings),
        },
    }


class _CFGBuilder:
    """Stateful builder for one module analysis run."""

    def __init__(self, *, path: str | None) -> None:
        self.path = path
        self.function_id = ""
        self.function_name = ""
        self.graph: FunctionCFG | None = None
        self.node_count = 0
        self.edge_keys: set[tuple[str, str, str, str | None, int | None]] = set()
        self.loop_stack: list[_LoopTargets] = []

    def build_function(self, function: SemanticNode) -> FunctionCFG:
        """Build a CFG for one normalized semantic AST function node."""
        self.function_id = _string(function.get("id"), _string(function.get("name"), "function"))
        self.function_name = _string(function.get("name"), self.function_id.rsplit(".", 1)[-1])
        self.node_count = 0
        self.edge_keys = set()
        self.loop_stack = []

        entry_id = self._fixed_node_id("entry")
        exit_id = self._fixed_node_id("exit")
        self.graph = FunctionCFG(
            id=f"function:{self.function_id}",
            name=self.function_name,
            qualified_name=self.function_id,
            entry=entry_id,
            exit=exit_id,
            path=self.path,
            line=_int_or_none(function.get("line")),
            end_line=_int_or_none(function.get("end_line")),
        )
        entry = CFGNode(id=entry_id, kind="entry", label="entry", scope=self.function_id, depth=0)
        exit_node = CFGNode(id=exit_id, kind="exit", label="exit", scope=self.function_id, depth=0)
        self._graph().nodes.extend([entry, exit_node])

        fallthrough = self._visit_body(
            function.get("body", []),
            incoming=[entry_id],
            depth=1,
            first_edge_kind="next",
            first_condition=None,
        )
        for node_id in fallthrough:
            self._add_edge(node_id, exit_id, "next", None, None)

        self._graph().exits = sorted({exit_id})
        self._sort_graph()
        return self._graph()

    def _visit_body(
        self,
        body: Any,
        *,
        incoming: list[str],
        depth: int,
        first_edge_kind: str,
        first_condition: str | None,
    ) -> list[str]:
        if not isinstance(body, list) or not body:
            return incoming

        current = incoming
        edge_kind = first_edge_kind
        condition = first_condition
        for statement in body:
            if not isinstance(statement, Mapping):
                continue
            current = self._visit_statement(
                statement,
                incoming=current,
                depth=depth,
                incoming_edge_kind=edge_kind,
                incoming_condition=condition,
            )
            edge_kind = "next"
            condition = None
        return current

    def _visit_statement(
        self,
        statement: SemanticNode,
        *,
        incoming: list[str],
        depth: int,
        incoming_edge_kind: str,
        incoming_condition: str | None,
    ) -> list[str]:
        node_type = _string(statement.get("type"), "statement")
        if node_type == "if":
            return self._handle_if(statement, incoming, depth, incoming_edge_kind, incoming_condition)
        if node_type in {"for", "async_for", "while"}:
            return self._handle_loop(statement, incoming, depth, incoming_edge_kind, incoming_condition)
        if node_type == "try":
            return self._handle_try(statement, incoming, depth, incoming_edge_kind, incoming_condition)
        if node_type == "return":
            return self._handle_terminal(statement, incoming, depth, incoming_edge_kind, incoming_condition, "return", "return")
        if node_type == "raise":
            return self._handle_terminal(statement, incoming, depth, incoming_edge_kind, incoming_condition, "raise", "exception")
        if node_type == "break":
            return self._handle_jump(statement, incoming, depth, incoming_edge_kind, incoming_condition, "break")
        if node_type == "continue":
            return self._handle_jump(statement, incoming, depth, incoming_edge_kind, incoming_condition, "continue")
        if node_type in {"function", "class"}:
            return incoming

        node = self._add_statement_node(statement, depth)
        self._connect_many(incoming, node.id, incoming_edge_kind, incoming_condition, statement)
        return [node.id] if incoming else []

    def _handle_if(
        self,
        statement: SemanticNode,
        incoming: list[str],
        depth: int,
        incoming_edge_kind: str,
        incoming_condition: str | None,
    ) -> list[str]:
        branch = self._add_node(
            kind="branch",
            label=f"if {_condition_label(statement.get('test'))}",
            depth=depth,
            statement=statement,
        )
        join = self._add_node(
            kind="join",
            label="if join",
            depth=depth,
            statement=statement,
        )
        self._connect_many(incoming, branch.id, incoming_edge_kind, incoming_condition, statement)

        if not incoming:
            return []

        join_reachable = False
        true_fallthrough = self._visit_body(
            statement.get("body", []),
            incoming=[branch.id],
            depth=depth + 1,
            first_edge_kind="branch_true",
            first_condition="true",
        )
        orelse = statement.get("orelse", [])
        if isinstance(orelse, list) and orelse:
            false_fallthrough = self._visit_body(
                orelse,
                incoming=[branch.id],
                depth=depth + 1,
                first_edge_kind="branch_false",
                first_condition="false",
            )
        else:
            self._add_edge(branch.id, join.id, "branch_false", "false", statement)
            join_reachable = True
            false_fallthrough = []

        for node_id in [*true_fallthrough, *false_fallthrough]:
            if node_id != branch.id:
                self._add_edge(node_id, join.id, "next", None, statement)
                join_reachable = True
        if true_fallthrough == [branch.id]:
            self._add_edge(branch.id, join.id, "branch_true", "true", statement)
            join_reachable = True
        if false_fallthrough == [branch.id]:
            self._add_edge(branch.id, join.id, "branch_false", "false", statement)
            join_reachable = True

        return [join.id] if join_reachable else []

    def _handle_loop(
        self,
        statement: SemanticNode,
        incoming: list[str],
        depth: int,
        incoming_edge_kind: str,
        incoming_condition: str | None,
    ) -> list[str]:
        node_type = _string(statement.get("type"), "loop")
        if node_type == "async_for":
            self._warn("PartialAnalysis", "async_for is modeled like for without async runtime semantics.", statement)

        loop = self._add_node(
            kind="loop",
            label=_loop_label(statement),
            depth=depth,
            statement=statement,
        )
        after_loop = self._add_node(
            kind="join",
            label="loop exit",
            depth=depth,
            statement=statement,
        )
        self._connect_many(incoming, loop.id, incoming_edge_kind, incoming_condition, statement)
        if not incoming:
            return []

        self.loop_stack.append(_LoopTargets(break_target=after_loop.id, continue_target=loop.id))
        body_fallthrough = self._visit_body(
            statement.get("body", []),
            incoming=[loop.id],
            depth=depth + 1,
            first_edge_kind="loop_body",
            first_condition="body",
        )
        self.loop_stack.pop()

        if body_fallthrough == [loop.id]:
            self._add_edge(loop.id, loop.id, "loop_back", "body", statement)
        else:
            for node_id in body_fallthrough:
                self._add_edge(node_id, loop.id, "loop_back", None, statement)

        orelse = statement.get("orelse", [])
        if isinstance(orelse, list) and orelse:
            else_fallthrough = self._visit_body(
                orelse,
                incoming=[loop.id],
                depth=depth + 1,
                first_edge_kind="loop_exit",
                first_condition="false",
            )
            for node_id in else_fallthrough:
                self._add_edge(node_id, after_loop.id, "next", None, statement)
        else:
            self._add_edge(loop.id, after_loop.id, "loop_exit", "false", statement)

        return [after_loop.id]

    def _handle_try(
        self,
        statement: SemanticNode,
        incoming: list[str],
        depth: int,
        incoming_edge_kind: str,
        incoming_condition: str | None,
    ) -> list[str]:
        self._warn("PartialAnalysis", "try is modeled with normal and handler paths only.", statement)
        try_node = self._add_node(kind="statement", label="try", depth=depth, statement=statement)
        after_try = self._add_node(kind="join", label="try join", depth=depth, statement=statement)
        self._connect_many(incoming, try_node.id, incoming_edge_kind, incoming_condition, statement)
        if not incoming:
            return []

        normal = self._visit_body(
            statement.get("body", []),
            incoming=[try_node.id],
            depth=depth + 1,
            first_edge_kind="next",
            first_condition=None,
        )
        handler_fallthrough: list[str] = []
        handlers = statement.get("handlers", [])
        if isinstance(handlers, list):
            for handler in handlers:
                if not isinstance(handler, Mapping):
                    continue
                handler_fallthrough.extend(
                    self._visit_body(
                        handler.get("body", []),
                        incoming=[try_node.id],
                        depth=depth + 1,
                        first_edge_kind="exception",
                        first_condition=_handler_label(handler),
                    )
                )

        orelse = statement.get("orelse", [])
        if isinstance(orelse, list) and orelse:
            normal = self._visit_body(
                orelse,
                incoming=normal,
                depth=depth + 1,
                first_edge_kind="next",
                first_condition=None,
            )

        combined = [*normal, *handler_fallthrough]
        finalbody = statement.get("finalbody", [])
        if isinstance(finalbody, list) and finalbody:
            combined = self._visit_body(
                finalbody,
                incoming=combined,
                depth=depth + 1,
                first_edge_kind="next",
                first_condition=None,
            )

        after_try_reachable = False
        for node_id in combined:
            if node_id != try_node.id:
                self._add_edge(node_id, after_try.id, "next", None, statement)
                after_try_reachable = True
        return [after_try.id] if after_try_reachable else []

    def _handle_terminal(
        self,
        statement: SemanticNode,
        incoming: list[str],
        depth: int,
        incoming_edge_kind: str,
        incoming_condition: str | None,
        node_kind: str,
        exit_edge_kind: str,
    ) -> list[str]:
        node = self._add_node(
            kind=node_kind,
            label=node_kind,
            depth=depth,
            statement=statement,
        )
        self._connect_many(incoming, node.id, incoming_edge_kind, incoming_condition, statement)
        if incoming:
            self._add_edge(node.id, self._graph().exit, exit_edge_kind, None, statement)
        return []

    def _handle_jump(
        self,
        statement: SemanticNode,
        incoming: list[str],
        depth: int,
        incoming_edge_kind: str,
        incoming_condition: str | None,
        jump_kind: str,
    ) -> list[str]:
        node = self._add_node(kind=jump_kind, label=jump_kind, depth=depth, statement=statement)
        self._connect_many(incoming, node.id, incoming_edge_kind, incoming_condition, statement)
        if not incoming:
            return []

        if not self.loop_stack:
            self._warn("InvalidJump", f"{jump_kind} is outside a loop.", statement)
            return []

        targets = self.loop_stack[-1]
        target = targets.break_target if jump_kind == "break" else targets.continue_target
        self._add_edge(node.id, target, jump_kind, None, statement)
        return []

    def _add_statement_node(self, statement: SemanticNode, depth: int) -> CFGNode:
        return self._add_node(
            kind="statement",
            label=_statement_label(statement),
            depth=depth,
            statement=statement,
        )

    def _add_node(
        self,
        *,
        kind: str,
        label: str,
        depth: int,
        statement: SemanticNode | None,
    ) -> CFGNode:
        self.node_count += 1
        node = CFGNode(
            id=self._node_id(kind, self.node_count),
            kind=kind,
            label=label,
            scope=self.function_id,
            depth=depth,
            line=_int_or_none(statement.get("line")) if isinstance(statement, Mapping) else None,
            end_line=_int_or_none(statement.get("end_line")) if isinstance(statement, Mapping) else None,
        )
        self._graph().nodes.append(node)
        return node

    def _connect_many(
        self,
        sources: list[str],
        target: str,
        kind: str,
        condition: str | None,
        statement: SemanticNode,
    ) -> None:
        for source in sources:
            self._add_edge(source, target, kind, condition, statement)

    def _add_edge(
        self,
        source: str,
        target: str,
        kind: str,
        condition: str | None,
        statement: SemanticNode | None,
    ) -> None:
        lineno = _int_or_none(statement.get("line")) if isinstance(statement, Mapping) else None
        key = (source, target, kind, condition, lineno)
        if key in self.edge_keys:
            return
        self.edge_keys.add(key)
        self._graph().edges.append(
            CFGEdge(
                source=source,
                target=target,
                kind=kind,
                condition=condition,
                lineno=lineno,
            )
        )

    def _warn(self, kind: str, message: str, node: SemanticNode | None) -> None:
        lineno = _int_or_none(node.get("line")) if isinstance(node, Mapping) else None
        self._graph().warnings.append(CFGWarning(kind=kind, message=message, lineno=lineno))

    def _sort_graph(self) -> None:
        graph = self._graph()
        graph.nodes.sort(key=lambda node: (node.line is None, node.line or 0, node.depth or 0, node.id))
        graph.edges.sort(key=lambda edge: (edge.lineno is None, edge.lineno or 0, edge.source, edge.target, edge.kind))
        graph.warnings.sort(key=lambda warning: (warning.lineno is None, warning.lineno or 0, warning.kind, warning.message))

    def _fixed_node_id(self, kind: str) -> str:
        return f"function:{self.function_id}:{kind}"

    def _node_id(self, kind: str, index: int) -> str:
        return f"function:{self.function_id}:{kind}:{index}"

    def _graph(self) -> FunctionCFG:
        if self.graph is None:
            raise RuntimeError("CFG builder is not initialized")
        return self.graph


def _collect_functions(tree: Any) -> list[dict[str, Any]]:
    functions: list[dict[str, Any]] = []
    module_path = _string_or_none(tree.get("path")) if isinstance(tree, Mapping) else None
    module_name = _module_name(module_path)
    _walk_functions(tree, functions, scope=[module_name] if module_name else [])
    return sorted(functions, key=lambda item: (_int_or_none(item.get("line")) or 0, item["id"]))


def _walk_functions(node: Any, functions: list[dict[str, Any]], scope: list[str]) -> None:
    if isinstance(node, list):
        for item in node:
            _walk_functions(item, functions, scope)
        return
    if not isinstance(node, Mapping):
        return

    node_type = node.get("type")
    if node_type == "module":
        _walk_functions(node.get("body", []), functions, scope)
        return
    if node_type == "class":
        name = _string(node.get("name"), "anonymous_class")
        _walk_functions(node.get("body", []), functions, [*scope, name])
        return
    if node_type == "function":
        name = _string(node.get("name"), "anonymous_function")
        function_scope = [*scope, name]
        item = dict(node)
        item["id"] = ".".join(function_scope)
        functions.append(item)
        _walk_functions(node.get("body", []), functions, function_scope)
        return
    _walk_functions(node.get("body", []), functions, scope)


def _statement_label(statement: SemanticNode) -> str:
    node_type = _string(statement.get("type"), "statement")
    if node_type == "assignment":
        return "assign"
    if node_type == "annotated_assignment":
        return "annotated assign"
    if node_type == "augmented_assignment":
        return "augmented assign"
    if node_type == "expression_statement":
        value = statement.get("value")
        if isinstance(value, Mapping) and value.get("type") == "call":
            return f"call {_call_label(value)}"
        return "expression"
    return node_type


def _loop_label(statement: SemanticNode) -> str:
    node_type = _string(statement.get("type"), "loop")
    if node_type in {"for", "async_for"}:
        return node_type
    return f"while {_condition_label(statement.get('test'))}"


def _condition_label(node: Any) -> str:
    if not isinstance(node, Mapping):
        return "condition"
    node_type = node.get("type")
    if node_type == "name":
        return _string(node.get("id"), "condition")
    if node_type == "constant":
        return repr(node.get("value"))
    if node_type == "call":
        return _call_label(node)
    if node_type == "attribute":
        value = _condition_label(node.get("value"))
        attr = _string(node.get("attr"), "attr")
        return f"{value}.{attr}"
    if node_type == "compare":
        return "compare"
    if node_type == "boolop":
        return _string(node.get("operator"), "boolop")
    if node_type == "unaryop":
        return _string(node.get("operator"), "unaryop")
    return _string(node_type, "condition")


def _call_label(node: SemanticNode) -> str:
    return _condition_label(node.get("func"))


def _handler_label(handler: SemanticNode) -> str:
    exc = handler.get("exc")
    if exc is None:
        return "except"
    return f"except {_condition_label(exc)}"


def _module_name(path: str | None) -> str | None:
    if not path:
        return None
    name = path.rsplit("/", 1)[-1]
    if name.endswith(".py"):
        name = name[:-3]
    return name.replace("-", "_") or None


def _string(value: Any, default: str) -> str:
    return value if isinstance(value, str) and value else default


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    return value if isinstance(value, int) else None
