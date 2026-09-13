"""Minimal, model-neutral graph data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional


FORMAT_NAME = "semantic_graph"
FORMAT_VERSION = "0.1.0"


def _attributes(value: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """Return a detached attribute mapping."""

    return dict(value or {})


@dataclass
class Node:
    """A graph-local entity with an automatically assigned integer identity."""

    unique_id: int
    label: str
    kind: str = "node"
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the node into the public JSON representation."""

        return {
            "unique_id": self.unique_id,
            "label": self.label,
            "kind": self.kind,
            "attributes": dict(self.attributes),
        }


@dataclass
class Edge:
    """A graph-local relation between two existing node identities.

    ``source`` and ``target`` preserve endpoint order only. The base graph does
    not interpret that order as a directed-graph constraint.
    """

    unique_id: int
    source: int
    target: int
    kind: str = "edge"
    label: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the edge into the public JSON representation."""

        result: Dict[str, Any] = {
            "unique_id": self.unique_id,
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
            "attributes": dict(self.attributes),
        }
        if self.label is not None:
            result["label"] = self.label
        return result


@dataclass
class Graph:
    """A general graph container without traversal or topology rules."""

    graph_id: str
    title: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    next_node_id: int = 1
    next_edge_id: int = 1
    revision: int = 0

    def __post_init__(self) -> None:
        """Validate the small set of invariants owned by the base graph."""

        if not isinstance(self.graph_id, str) or not self.graph_id.strip():
            raise ValueError("graph_id must be a non-empty string")
        if self.title is not None and not isinstance(self.title, str):
            raise ValueError("title must be a string or null")
        self._validate_identity_state()
        self._validate_endpoints()

    def add_node(
        self,
        label: str,
        *,
        kind: str = "node",
        attributes: Optional[Mapping[str, Any]] = None,
    ) -> Node:
        """Add a node and return the created object."""

        if not isinstance(label, str) or not label.strip():
            raise ValueError("node label must be a non-empty string")
        if not isinstance(kind, str) or not kind.strip():
            raise ValueError("node kind must be a non-empty string")

        node = Node(
            unique_id=self.next_node_id,
            label=label,
            kind=kind,
            attributes=_attributes(attributes),
        )
        self.nodes.append(node)
        self.next_node_id += 1
        self.revision += 1
        return node

    def add_edge(
        self,
        source: int,
        target: int,
        *,
        kind: str = "edge",
        label: Optional[str] = None,
        attributes: Optional[Mapping[str, Any]] = None,
    ) -> Edge:
        """Add an edge between existing nodes and return the created object."""

        node_ids = {node.unique_id for node in self.nodes}
        missing = [node_id for node_id in (source, target) if node_id not in node_ids]
        if missing:
            missing_text = ", ".join(str(node_id) for node_id in missing)
            raise ValueError(f"edge references missing node(s): {missing_text}")
        if not isinstance(kind, str) or not kind.strip():
            raise ValueError("edge kind must be a non-empty string")
        if label is not None and not isinstance(label, str):
            raise ValueError("edge label must be a string or null")

        edge = Edge(
            unique_id=self.next_edge_id,
            source=source,
            target=target,
            kind=kind,
            label=label,
            attributes=_attributes(attributes),
        )
        self.edges.append(edge)
        self.next_edge_id += 1
        self.revision += 1
        return edge

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the complete graph state."""

        return {
            "type": FORMAT_NAME,
            "version": FORMAT_VERSION,
            "graph_id": self.graph_id,
            "title": self.title,
            "attributes": dict(self.attributes),
            "revision": self.revision,
            "next_node_id": self.next_node_id,
            "next_edge_id": self.next_edge_id,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Graph":
        """Restore a graph from its public JSON representation."""

        if data.get("type") != FORMAT_NAME:
            raise ValueError(f"graph type must be {FORMAT_NAME!r}")
        if data.get("version") != FORMAT_VERSION:
            raise ValueError(f"graph version must be {FORMAT_VERSION!r}")

        nodes = [
            Node(
                unique_id=item["unique_id"],
                label=item["label"],
                kind=item.get("kind", "node"),
                attributes=_attributes(item.get("attributes")),
            )
            for item in _items(data.get("nodes"), "nodes")
        ]
        edges = [
            Edge(
                unique_id=item["unique_id"],
                source=item["source"],
                target=item["target"],
                kind=item.get("kind", "edge"),
                label=item.get("label"),
                attributes=_attributes(item.get("attributes")),
            )
            for item in _items(data.get("edges"), "edges")
        ]
        graph = cls(
            graph_id=data["graph_id"],
            title=data.get("title"),
            attributes=_attributes(data.get("attributes")),
            nodes=nodes,
            edges=edges,
            next_node_id=data.get("next_node_id", _next_id(nodes)),
            next_edge_id=data.get("next_edge_id", _next_id(edges)),
            revision=data.get("revision", 0),
        )
        graph._validate_endpoints()
        return graph

    def _validate_identity_state(self) -> None:
        """Ensure identities and counters are internally consistent."""

        node_ids = [node.unique_id for node in self.nodes]
        edge_ids = [edge.unique_id for edge in self.edges]
        _validate_ids(node_ids, "node")
        _validate_ids(edge_ids, "edge")
        if not isinstance(self.next_node_id, int) or self.next_node_id < _next_id(self.nodes):
            raise ValueError("next_node_id must be greater than every node identity")
        if not isinstance(self.next_edge_id, int) or self.next_edge_id < _next_id(self.edges):
            raise ValueError("next_edge_id must be greater than every edge identity")
        if not isinstance(self.revision, int) or self.revision < 0:
            raise ValueError("revision must be a non-negative integer")

    def _validate_endpoints(self) -> None:
        """Ensure every stored edge references nodes in this graph."""

        node_ids = {node.unique_id for node in self.nodes}
        for edge in self.edges:
            if edge.source not in node_ids or edge.target not in node_ids:
                raise ValueError(f"edge {edge.unique_id} references a missing node")


def _items(value: Any, field_name: str) -> Iterable[Mapping[str, Any]]:
    """Validate a serialized collection before constructing model objects."""

    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
        raise ValueError(f"{field_name} must be a list of objects")
    return value


def _next_id(items: Iterable[Any]) -> int:
    """Return the next monotonic identity for a node or edge collection."""

    return max((item.unique_id for item in items), default=0) + 1


def _validate_ids(values: List[int], object_name: str) -> None:
    """Validate graph-local positive integer identities."""

    if any(isinstance(value, bool) or not isinstance(value, int) or value < 1 for value in values):
        raise ValueError(f"{object_name} unique_id values must be positive integers")
    if len(values) != len(set(values)):
        raise ValueError(f"{object_name} unique_id values must be unique")
