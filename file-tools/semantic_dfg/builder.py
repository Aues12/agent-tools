"""Build local data-flow graphs from semantic AST dictionaries."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from schema import DFGEdge, DFGNode, DFGWarning, FunctionDFG


SemanticNode = Mapping[str, Any]

_BODY_FIELDS = ("body", "orelse", "finalbody")
_PARTIAL_CONTAINER_TYPES = {
    "if",
    "for",
    "async_for",
    "while",
    "with",
    "async_with",
    "try",
    "except_handler",
}


def build_dfg(tree: Any) -> dict[str, Any]:
    """Build deterministic local function-level DFGs from a semantic AST tree."""
    if not isinstance(tree, Mapping):
        raise TypeError("tree must be a dictionary")
    if tree.get("type") != "module":
        raise ValueError("tree must be a semantic_ast module node")

    functions = _collect_functions(tree)
    builder = _DFGBuilder(path=_string_or_none(tree.get("path")))
    function_graphs = [builder.build_function(function) for function in functions]
    warnings = [warning for graph in function_graphs for warning in graph.warnings]

    return {
        "type": "data_flow_graph",
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


class _DFGBuilder:
    """Stateful builder for one module analysis run."""

    def __init__(self, *, path: str | None) -> None:
        self.path = path
        self.function: SemanticNode | None = None
        self.function_id = ""
        self.function_name = ""
        self.graph: FunctionDFG | None = None
        self.nodes_by_id: dict[str, DFGNode] = {}
        self.edge_keys: set[tuple[str, str, str, str | None, int | None]] = set()
        self.return_count = 0
        self.current_depth = 1

    def build_function(self, function: SemanticNode) -> FunctionDFG:
        """Build a DFG for one normalized semantic AST function node."""
        self.function = function
        self.function_id = _string(function.get("id"), _string(function.get("name"), "function"))
        self.function_name = _string(function.get("name"), self.function_id.rsplit(".", 1)[-1])
        self.graph = FunctionDFG(
            id=f"function:{self.function_id}",
            name=self.function_name,
            qualified_name=self.function_id,
            path=self.path,
            line=_int_or_none(function.get("line")),
            end_line=_int_or_none(function.get("end_line")),
        )
        self.nodes_by_id = {}
        self.edge_keys = set()
        self.return_count = 0
        self.current_depth = 1

        self._add_parameters(function.get("args"))
        self._visit_body(function.get("body", []), depth=1)
        self._assign_flow_levels()
        self._sort_graph()
        return self.graph

    def _add_parameters(self, args: Any) -> None:
        if not isinstance(args, Mapping):
            return

        fields = (
            "positional_only",
            "positional_or_keyword",
            "keyword_only",
        )
        for field in fields:
            values = args.get(field, [])
            if isinstance(values, list):
                for item in values:
                    self._add_parameter(item)

        self._add_parameter(args.get("vararg"))
        self._add_parameter(args.get("kwarg"))

    def _add_parameter(self, node: Any) -> None:
        if not isinstance(node, Mapping):
            return
        name = _string_or_none(node.get("name"))
        if not name:
            return
        self._add_node(
            name=name,
            kind="parameter",
            depth=0,
            lineno=_int_or_none(node.get("line")),
        )

    def _visit_body(self, body: Any, *, depth: int) -> None:
        if not isinstance(body, list):
            return
        previous_depth = self.current_depth
        self.current_depth = depth
        for statement in body:
            if isinstance(statement, Mapping):
                self._visit_statement(statement)
        self.current_depth = previous_depth

    def _visit_statement(self, statement: SemanticNode) -> None:
        node_type = _string(statement.get("type"), "statement")
        if node_type == "assignment":
            self._handle_assignment(statement)
            return
        if node_type == "annotated_assignment":
            self._handle_annotated_assignment(statement)
            return
        if node_type == "augmented_assignment":
            self._handle_augmented_assignment(statement)
            return
        if node_type == "return":
            self._handle_return(statement)
            return
        if node_type in _PARTIAL_CONTAINER_TYPES:
            self._warn(
                "PartialAnalysis",
                f"{node_type} is analyzed by visiting contained statements only.",
                statement,
            )
            self._visit_nested_bodies(statement)
            return
        if node_type in {"function", "class"}:
            return
        if node_type == "expression_statement":
            self._handle_expression_statement(statement)
            return
        self._warn("UnsupportedNode", f"{node_type} is not analyzed by semantic_dfg v1.", statement)

    def _visit_nested_bodies(self, statement: SemanticNode) -> None:
        for field in _BODY_FIELDS:
            self._visit_body(statement.get(field, []), depth=self.current_depth + 1)
        handlers = statement.get("handlers", [])
        if isinstance(handlers, list):
            for handler in handlers:
                if isinstance(handler, Mapping):
                    self._visit_statement(handler)

    def _handle_assignment(self, statement: SemanticNode) -> None:
        targets = statement.get("targets", [])
        if not isinstance(targets, list):
            return
        value = statement.get("value")
        operation = _operation_name(value)
        dependencies = self._dependencies(value)

        for target in self._target_names(targets):
            self._add_binding_flow(target, dependencies, operation, statement)

    def _handle_annotated_assignment(self, statement: SemanticNode) -> None:
        target = statement.get("target")
        targets = [target] if isinstance(target, Mapping) else []
        value = statement.get("value")
        if value is None:
            return
        operation = _operation_name(value)
        dependencies = self._dependencies(value)

        for target_name in self._target_names(targets):
            self._add_binding_flow(target_name, dependencies, operation, statement)

    def _handle_augmented_assignment(self, statement: SemanticNode) -> None:
        target = statement.get("target")
        if not isinstance(target, Mapping):
            return
        target_name = _target_name(target)
        if not target_name:
            self._warn("UnsupportedTarget", "Unsupported augmented assignment target.", statement)
            return

        target_node = self._add_node(name=target_name, kind="binding", lineno=_int_or_none(statement.get("line")))
        dependencies = [target_name, *self._dependencies(statement.get("value"))]
        operation = _string(statement.get("operator"), "AugAssign")
        for dependency in _dedupe(dependencies):
            source = self._node_for_dependency(dependency, statement)
            self._add_edge(source.id, target_node.id, "depends_on", operation, statement)

    def _handle_return(self, statement: SemanticNode) -> None:
        self.return_count += 1
        return_name = "return_value" if self.return_count == 1 else f"return_value_{self.return_count}"
        return_node = self._add_node(
            name=return_name,
            kind="return_value",
            depth=self.current_depth,
            lineno=_int_or_none(statement.get("line")),
        )
        self._graph().returns.append(return_node.id)

        value = statement.get("value")
        dependencies = self._dependencies(value)
        if not dependencies and value is not None:
            literal = self._add_node(
                name=f"{return_name}_literal",
                kind="literal",
                depth=self.current_depth,
                lineno=_int_or_none(statement.get("line")),
            )
            self._add_edge(literal.id, return_node.id, "returns", "return", statement)
            return

        for dependency in dependencies:
            source = self._node_for_dependency(dependency, statement)
            self._add_edge(source.id, return_node.id, "returns", "return", statement)

    def _handle_expression_statement(self, statement: SemanticNode) -> None:
        value = statement.get("value")
        if not isinstance(value, Mapping) or value.get("type") != "call":
            return
        call_node = self._add_node(
            name=_operation_name(value),
            kind="call_result",
            depth=self.current_depth,
            lineno=_int_or_none(statement.get("line")),
        )
        for dependency in self._dependencies(value):
            source = self._node_for_dependency(dependency, statement)
            self._add_edge(source.id, call_node.id, "passes_to_call", _operation_name(value), statement)

    def _add_binding_flow(
        self,
        target: str,
        dependencies: list[str],
        operation: str,
        statement: SemanticNode,
    ) -> None:
        binding = self._add_node(
            name=target,
            kind="binding",
            depth=self.current_depth,
            lineno=_int_or_none(statement.get("line")),
        )
        if not dependencies:
            literal = self._add_node(
                name=f"{target}_literal",
                kind="literal",
                depth=self.current_depth,
                lineno=_int_or_none(statement.get("line")),
            )
            self._add_edge(literal.id, binding.id, "produces", operation, statement)
            return

        for dependency in dependencies:
            source = self._node_for_dependency(dependency, statement)
            self._add_edge(source.id, binding.id, "depends_on", operation, statement)

    def _target_names(self, targets: list[Any]) -> list[str]:
        names: list[str] = []
        for target in targets:
            names.extend(_target_names(target))
        if not names:
            self._warn("UnsupportedTarget", "Assignment target is not supported by semantic_dfg v1.", None)
        return _dedupe(names)

    def _dependencies(self, node: Any) -> list[str]:
        dependencies: list[str] = []
        _collect_dependencies(node, dependencies)
        return _dedupe(dependencies)

    def _node_for_dependency(self, dependency: str, statement: SemanticNode) -> DFGNode:
        existing = self.nodes_by_id.get(self._node_id("binding", dependency))
        if existing is not None:
            return existing
        existing = self.nodes_by_id.get(self._node_id("parameter", dependency))
        if existing is not None:
            return existing
        return self._add_node(
            name=dependency,
            kind="unknown",
            lineno=_int_or_none(statement.get("line")),
        )

    def _add_node(
        self,
        *,
        name: str,
        kind: str,
        depth: int | None = None,
        lineno: int | None = None,
        col_offset: int | None = None,
    ) -> DFGNode:
        node_id = self._node_id(kind, name)
        existing = self.nodes_by_id.get(node_id)
        if existing is not None:
            return existing

        node = DFGNode(
            id=node_id,
            name=name,
            kind=kind,
            scope=self.function_id,
            depth=depth if depth is not None else self.current_depth,
            lineno=lineno,
            col_offset=col_offset,
        )
        self.nodes_by_id[node_id] = node
        self._graph().nodes.append(node)
        return node

    def _replace_node(self, node: DFGNode) -> None:
        self.nodes_by_id[node.id] = node
        graph = self._graph()
        for index, existing in enumerate(graph.nodes):
            if existing.id == node.id:
                graph.nodes[index] = node
                return
        graph.nodes.append(node)

    def _node_id(self, kind: str, name: str) -> str:
        safe_name = name.replace(":", "_")
        return f"function:{self.function_id}:{kind}:{safe_name}"

    def _add_edge(
        self,
        source: str,
        target: str,
        kind: str,
        operation: str | None,
        statement: SemanticNode,
    ) -> None:
        lineno = _int_or_none(statement.get("line"))
        key = (source, target, kind, operation, lineno)
        if key in self.edge_keys:
            return
        self.edge_keys.add(key)
        self._graph().edges.append(
            DFGEdge(
                source=source,
                target=target,
                kind=kind,
                operation=operation,
                lineno=lineno,
            )
        )

    def _warn(
        self,
        kind: str,
        message: str,
        node: SemanticNode | None,
    ) -> None:
        lineno = _int_or_none(node.get("line")) if isinstance(node, Mapping) else None
        self._graph().warnings.append(DFGWarning(kind=kind, message=message, lineno=lineno))

    def _sort_graph(self) -> None:
        graph = self._graph()
        graph.nodes.sort(key=lambda node: (node.lineno is None, node.lineno or 0, node.kind, node.id))
        graph.edges.sort(key=lambda edge: (edge.lineno is None, edge.lineno or 0, edge.source, edge.target, edge.kind))
        graph.returns[:] = sorted(set(graph.returns))
        graph.warnings.sort(key=lambda warning: (warning.lineno is None, warning.lineno or 0, warning.kind, warning.message))

    def _assign_flow_levels(self) -> None:
        graph = self._graph()
        levels = _compute_flow_levels(graph.nodes, graph.edges)
        for node in list(graph.nodes):
            self._replace_node(
                DFGNode(
                    id=node.id,
                    name=node.name,
                    kind=node.kind,
                    scope=node.scope,
                    flow_level=levels.get(node.id, 0),
                    depth=node.depth,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                )
            )

    def _graph(self) -> FunctionDFG:
        if self.graph is None:
            raise RuntimeError("DFG builder is not initialized")
        return self.graph


def _collect_functions(tree: Any) -> list[dict[str, Any]]:
    functions: list[dict[str, Any]] = []
    module_path = _string_or_none(tree.get("path")) if isinstance(tree, Mapping) else None
    module_name = _module_name(module_path)
    _walk_functions(tree, functions, scope=[module_name] if module_name else [])
    return sorted(functions, key=lambda item: (_int_or_none(item.get("line")) or 0, item["id"]))


def _compute_flow_levels(nodes: list[DFGNode], edges: list[DFGEdge]) -> dict[str, int]:
    """Compute longest upstream value-flow distance for each DFG node."""
    node_ids = {node.id for node in nodes}
    levels = {node.id: 0 for node in nodes}
    relevant_edges = [
        edge
        for edge in edges
        if edge.source in node_ids and edge.target in node_ids and edge.source != edge.target
    ]

    for _ in range(max(len(nodes), 1)):
        changed = False
        for edge in relevant_edges:
            candidate = levels[edge.source] + 1
            if candidate > levels[edge.target]:
                levels[edge.target] = candidate
                changed = True
        if not changed:
            break

    return levels


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


def _target_names(node: Any) -> list[str]:
    if not isinstance(node, Mapping):
        return []
    node_type = node.get("type")
    if node_type == "name":
        name = _string_or_none(node.get("id"))
        return [name] if name else []
    if node_type == "tuple":
        names: list[str] = []
        elements = node.get("elements", [])
        if isinstance(elements, list):
            for item in elements:
                names.extend(_target_names(item))
        return names
    if node_type == "attribute":
        name = _value_name(node)
        return [name] if name else []
    if node_type == "subscript":
        name = _value_name(node)
        return [name] if name else []
    return []


def _target_name(node: Any) -> str | None:
    names = _target_names(node)
    return names[0] if names else None


def _collect_dependencies(node: Any, dependencies: list[str]) -> None:
    if not isinstance(node, Mapping):
        return
    node_type = node.get("type")
    if node_type == "name":
        name = _string_or_none(node.get("id"))
        if name:
            dependencies.append(name)
        return
    if node_type == "attribute":
        base = node.get("value")
        _collect_dependencies(base, dependencies)
        return
    if node_type == "subscript":
        _collect_dependencies(node.get("value"), dependencies)
        _collect_dependencies(node.get("slice"), dependencies)
        return
    if node_type == "call":
        for arg in _list(node.get("args")):
            _collect_dependencies(arg, dependencies)
        for keyword in _list(node.get("keywords")):
            if isinstance(keyword, Mapping):
                _collect_dependencies(keyword.get("value"), dependencies)
        return
    if node_type in {"constant", "slice"}:
        return

    for value in node.values():
        if isinstance(value, Mapping):
            _collect_dependencies(value, dependencies)
        elif isinstance(value, list):
            for item in value:
                _collect_dependencies(item, dependencies)


def _operation_name(node: Any) -> str:
    if not isinstance(node, Mapping):
        return "unknown"
    node_type = _string(node.get("type"), "unknown")
    if node_type == "call":
        return _value_name(node.get("func")) or "call"
    if node_type == "binop":
        return _string(node.get("operator"), "BinOp")
    if node_type == "unaryop":
        return _string(node.get("operator"), "UnaryOp")
    if node_type == "boolop":
        return _string(node.get("operator"), "BoolOp")
    if node_type == "compare":
        ops = node.get("ops")
        if isinstance(ops, list) and ops:
            return "Compare:" + ",".join(str(op) for op in ops)
        return "Compare"
    if node_type == "attribute":
        return "attribute_access"
    if node_type == "subscript":
        return "subscript_access"
    if node_type == "constant":
        return "literal"
    return node_type


def _value_name(node: Any) -> str | None:
    if not isinstance(node, Mapping):
        return None
    node_type = node.get("type")
    if node_type == "name":
        return _string_or_none(node.get("id"))
    if node_type == "attribute":
        base = _value_name(node.get("value"))
        attr = _string_or_none(node.get("attr"))
        if base and attr:
            return f"{base}.{attr}"
        return attr
    if node_type == "subscript":
        base = _value_name(node.get("value"))
        return f"{base}[]" if base else None
    return None


def _module_name(path: str | None) -> str | None:
    if not path:
        return None
    name = path.rsplit("/", 1)[-1]
    if name.endswith(".py"):
        name = name[:-3]
    return name or None


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string(value: Any, default: str) -> str:
    return value if isinstance(value, str) and value else default


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _int_or_none(value: Any) -> int | None:
    return value if isinstance(value, int) else None
