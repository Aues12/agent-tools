# First notes

## Intent

`semantic_graph` should be a conceptually scalable graph workspace for agents.
It is not limited to software analysis. The same small foundation should be
able to represent coding workflows, research maps, decisions, organizations,
states, dependencies, and other domains without embedding those meanings in
the core.

The tool helps an LLM author, inspect, and validate a graph. The LLM supplies
semantic judgment; the tool supplies identity, structure, mutation, and
deterministic checks.

## Layering

Keep these responsibilities separate:

```text
graph model
    structural possibilities and invariants

profile
    domain-oriented constraints and vocabulary applied to a model

protocol
    an agent procedure for authoring, reviewing, or transforming a graph

interface
    stdin JSON, Python API, or an interactive terminal session

storage
    serialization, revision control, and atomic file replacement
```

A protocol may coordinate several graph operations, but it should not become a
new graph model. A profile may constrain a model, but it should not own storage
or agent interaction.

## Conceptual scalability

The primary scalability goal is conceptual rather than large-data processing:

```text
simple and general
    -> structurally specialized
    -> domain-oriented
    -> workflow-integrated
```

New graph kinds should normally add constraints or capabilities without
invalidating the core node/edge representation.

## Core graph direction

The least constrained ordinary graph should be the base. Directed graphs,
DAGs, and trees are possible structural specializations. Cross-cutting traits
such as parallel edges, weights, properties, or temporal metadata do not fit a
single inheritance tree cleanly and may be represented by policies or options.

A likely implementation shape is therefore hybrid:

```text
Graph
├── common identity, node/edge storage, and validation
├── DirectedGraph
│   └── DAG
└── optional policies
    ├── parallel edges
    ├── self-loops
    ├── properties
    └── weights or temporal data
```

This is a research direction, not yet a commitment to a Python class hierarchy.

## Identity

Every persisted graph should have a stable `graph_id`. A separate `title` is
preferable because a human-readable title may change while identity remains
stable. If no title is supplied, an interface may display `graph_id` as the
fallback title.

Nodes and edges should have separate graph-local integer identity spaces:

```text
node unique_id: 1, 2, 3, ...
edge unique_id: 1, 2, 3, ...
```

Provisional identity rules:

* IDs are unique within their entity type and graph.
* Node and edge counters are independent.
* IDs are assigned monotonically in creation order.
* Deleted IDs are not reused.
* Reordering does not change identity.
* Serialization preserves the next available IDs.
* A cross-graph address can use `graph_id` plus graph-local `unique_id`.

An optional symbolic `key` may later help an LLM refer to an entity by a stable
readable name. It must not replace the system-managed integer identity without
a demonstrated need.

## Open type vocabulary

Node and edge `kind` values should remain open strings. The core should not
require a release whenever an agent needs a new semantic type.

```json
{
  "unique_id": 3,
  "kind": "validation_step",
  "label": "Validate input"
}
```

Profiles may recommend or constrain kinds, but the ordinary graph model should
not own a closed ontology.

## Incremental agent authoring

An agent should not need to rewrite a complete JSON graph after every change.
A persistent terminal session could load a graph once and accept short
commands:

```text
create
add-node
add-edge
show
inspect-node
validate
save
```

This supports a tight feedback loop:

```text
author -> inspect -> revise -> validate
```

The session is intended to reduce repeated command paths, request envelopes,
and whole-graph serialization. Token efficiency should eventually be measured
rather than assumed.

## JSON parameter packets

Short interactive commands and reusable JSON parameter packets should coexist.
A packet can describe one operation or a reusable group of parameters:

```json
{
  "command": "add-node",
  "params": {
    "kind": "input",
    "label": "ISBN input"
  }
}
```

Packets may later be composed with profiles or protocols. They should remain
plain data and should not contain executable code.

## Protocol direction

Protocols can make graph work part of a modular agent architecture. Examples
worth researching include:

* incremental authoring;
* review and correction;
* evidence attachment;
* profile-guided validation;
* checkpoint and resume;
* graph comparison or merge.

A protocol describes an ordered interaction with capabilities; it does not
change the meaning of the underlying graph.

## Safety and persistence

Any future file-backed mutation should use:

* validation before mutation is committed;
* temporary-file plus atomic replacement;
* monotonically increasing graph revision;
* optional expected-revision checks;
* structured responses;
* no silent endpoint repair or ID renumbering.

The in-memory graph model should not depend directly on terminal or filesystem
behavior.

## Present boundary

The existing prototype remains intentionally smaller than these notes. The
research phase should precede changes to identity, persistence, graph model
inheritance, session handling, profiles, and protocols.
