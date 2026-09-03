"""Persistent, line-oriented terminal session for building graphs."""

from __future__ import annotations

import json
import os
import shlex
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, TextIO

from model import Graph


HELP_TEXT = """semantic_graph terminal commands

  new --graph-id ID [--title TITLE]
      Create an empty graph and make it the active graph.

  add-node --label LABEL [--kind KIND]
  add-node @params.json
      Add a node to the active graph. The tool assigns its unique_id.
      A packet may contain: label, kind, attributes.

  add-edge --source NODE_ID --target NODE_ID [--kind KIND] [--label LABEL]
  add-edge @params.json
      Connect two existing nodes. The tool assigns the edge unique_id.
      A packet may contain: source, target, kind, label, attributes.

  show
      Show graph_id, revision, and node/edge counts.

  show json
      Print the complete active graph as JSON.

  save PATH
      Atomically save the active graph as a JSON file.

  open PATH
      Load a saved graph and make it the active graph.

  help
      Show this guide.

  exit
      Close the terminal session.

Notes:
  - Run new or open before commands that require an active graph.
  - Node and edge IDs use separate counters, both starting at 1.
  - Quote values that contain spaces: --label "Validate ISBN".
  - @params.json must contain one JSON object."""


class GraphSession:
    """Hold one active graph across multiple terminal commands."""

    def __init__(self) -> None:
        self.graph: Optional[Graph] = None

    def execute(self, line: str) -> Optional[str]:
        """Execute one command and return a compact response.

        ``None`` signals that the caller should close the session.
        """

        tokens = shlex.split(line)
        if not tokens:
            return ""

        command, args = tokens[0], tokens[1:]
        if command in {"exit", "quit"}:
            return None
        if command == "help":
            return HELP_TEXT
        if command == "new":
            values = _options(args)
            _reject_unknown(values, {"graph_id", "title"})
            self.graph = Graph(
                graph_id=_required(values, "graph_id"),
                title=values.get("title"),
            )
            return f"ok graph {self.graph.graph_id}"
        if command == "open":
            path = _single_path(args, "open")
            self.graph = load_graph(path)
            return f"ok graph {self.graph.graph_id} revision {self.graph.revision}"
        if command == "save":
            graph = self._active_graph()
            path = _single_path(args, "save")
            save_graph(graph, path)
            return f"ok saved {path}"
        if command == "show":
            graph = self._active_graph()
            if not args:
                return (
                    f"graph {graph.graph_id} revision {graph.revision} "
                    f"nodes {len(graph.nodes)} edges {len(graph.edges)}"
                )
            if args == ["json"]:
                return json.dumps(graph.to_dict(), ensure_ascii=False, indent=2)
            raise ValueError("usage: show [json]")
        if command == "add-node":
            graph = self._active_graph()
            values = _parameters(args)
            _reject_unknown(values, {"label", "kind", "attributes"})
            node = graph.add_node(
                _required(values, "label"),
                kind=values.get("kind", "node"),
                attributes=_mapping(values.get("attributes"), "attributes"),
            )
            return f"ok node {node.unique_id} revision {graph.revision}"
        if command == "add-edge":
            graph = self._active_graph()
            values = _parameters(args)
            _reject_unknown(values, {"source", "target", "kind", "label", "attributes"})
            edge = graph.add_edge(
                _integer(_required(values, "source"), "source"),
                _integer(_required(values, "target"), "target"),
                kind=values.get("kind", "edge"),
                label=values.get("label"),
                attributes=_mapping(values.get("attributes"), "attributes"),
            )
            return f"ok edge {edge.unique_id} revision {graph.revision}"

        raise ValueError(f"unknown command: {command}")

    def _active_graph(self) -> Graph:
        """Return the active graph or explain how to create one."""

        if self.graph is None:
            raise ValueError("no active graph; use new or open first")
        return self.graph


def run_session(
    input_stream: TextIO = sys.stdin,
    output_stream: TextIO = sys.stdout,
    *,
    show_prompt: bool = False,
) -> int:
    """Run commands until EOF or an explicit exit command."""

    session = GraphSession()
    if show_prompt:
        output_stream.write("semantic_graph 0.1.0; type help for commands\n")
        output_stream.flush()

    while True:
        if show_prompt:
            output_stream.write("semantic-graph> ")
            output_stream.flush()
        line = input_stream.readline()
        if line == "":
            return 0
        try:
            response = session.execute(line)
        except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as error:
            output_stream.write(f"error {error}\n")
            output_stream.flush()
            continue
        if response is None:
            return 0
        if response:
            output_stream.write(f"{response}\n")
            output_stream.flush()


def save_graph(graph: Graph, path: Path) -> None:
    """Persist a graph atomically as UTF-8 JSON."""

    destination = Path(path)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=str(destination.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(graph.to_dict(), handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary_name, destination)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def load_graph(path: Path) -> Graph:
    """Load and validate a graph JSON file."""

    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, Mapping):
        raise ValueError("graph file must contain a JSON object")
    return Graph.from_dict(data)


def _parameters(args: Sequence[str]) -> Dict[str, Any]:
    """Read parameters from command options or one ``@file.json`` packet."""

    if len(args) == 1 and args[0].startswith("@"):
        packet_path = Path(args[0][1:])
        with packet_path.open("r", encoding="utf-8") as handle:
            packet = json.load(handle)
        if not isinstance(packet, dict):
            raise ValueError("parameter packet must contain a JSON object")
        return packet
    return _options(args)


def _options(args: Sequence[str]) -> Dict[str, Any]:
    """Parse a deliberately small ``--name value`` option set."""

    if len(args) % 2:
        raise ValueError("options must be --name value pairs")
    values: Dict[str, Any] = {}
    for index in range(0, len(args), 2):
        option = args[index]
        if not option.startswith("--") or len(option) == 2:
            raise ValueError("options must use --name value pairs")
        name = option[2:].replace("-", "_")
        if name in values:
            raise ValueError(f"duplicate option: --{name.replace('_', '-')}")
        values[name] = args[index + 1]
    return values


def _required(values: Mapping[str, Any], name: str) -> Any:
    """Return a required parameter with a concise error."""

    if name not in values:
        raise ValueError(f"missing parameter: {name}")
    return values[name]


def _reject_unknown(values: Mapping[str, Any], allowed: set[str]) -> None:
    """Reject misspelled or unsupported parameters instead of ignoring them."""

    unknown = sorted(set(values) - allowed)
    if unknown:
        raise ValueError(f"unknown parameter(s): {', '.join(unknown)}")


def _integer(value: Any, name: str) -> int:
    """Convert a command or packet value to a positive integer."""

    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive integer")
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a positive integer") from error
    if result < 1:
        raise ValueError(f"{name} must be a positive integer")
    return result


def _mapping(value: Any, name: str) -> Dict[str, Any]:
    """Normalize an optional JSON object parameter."""

    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be a JSON object; use a parameter packet")
    return dict(value)


def _single_path(args: Sequence[str], command: str) -> Path:
    """Parse a command that accepts exactly one path."""

    if len(args) != 1:
        raise ValueError(f"usage: {command} PATH")
    return Path(args[0])
