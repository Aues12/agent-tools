# AGENTS.md — semantic_graph

## Purpose

`semantic_graph` gives an agent a small, persistent terminal workspace for
constructing a graph incrementally. The agent supplies the meaning; the tool
owns identities, basic structural integrity, serialization, and session state.

## v0.1.0 scope

Keep this version deliberately small:

* one general `Graph` class;
* basic `Node` and `Edge` records;
* graph-local monotonic integer identities;
* separate node and edge counters;
* a persistent line-oriented terminal session;
* node and edge creation through flags or JSON parameter packets;
* JSON save/open support.

Do not add graph-model subclasses, profiles, traversal algorithms, source
parsing, visualization, LLM calls, deletion, mutation, or ontology management.

## Model policy

The base graph imposes no directed, acyclic, simple-graph, or domain-specific
rules. `source` and `target` preserve endpoint order without claiming what that
order means. Later models or profiles may interpret or restrict it.

Node and edge `kind` values are open strings. Defaults exist only for
convenience and do not form an ontology.

## Identity policy

`graph_id` identifies the graph. Each node and edge also receives a positive
integer `unique_id` within that graph. Node and edge namespaces are separate,
both begin at 1, and counters move monotonically. IDs are not caller-assigned.

## Session policy

The session keeps one active graph in process memory. Mutating commands report
the created identity and resulting revision. Command errors must not terminate
the session. `save` is the only graph mutation that writes to disk; it uses an
atomic replacement. `open` and `@packet.json` are explicit reads.

## Development rule

Prefer a minimal contract over speculative graph features. Design exploration
belongs under `research/` and is not implemented behavior until code, public
metadata, documentation, and tests change together.
