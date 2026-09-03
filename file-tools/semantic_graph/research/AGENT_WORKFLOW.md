# Agent workflow research

## Goal

Explore how an agent can build a graph incrementally while repeatedly
inspecting the artifact it is creating. The workflow should minimize repeated
context without hiding graph state or weakening validation.

## Proposed interaction modes

### One-shot JSON

One complete request is sent through stdin and one structured response is
returned. This remains useful for runtimes, reproducible automation, and small
graphs.

```text
request JSON -> operation -> response JSON
```

### Persistent terminal session

A process starts once, keeps one graph workspace loaded, and accepts short
commands until the agent saves or exits.

```text
start session
    -> open or create graph
    -> add-node
    -> inspect
    -> add-edge
    -> validate
    -> save
    -> exit
```

Illustrative interaction:

```text
semantic-graph> create bookbarcode-flow
created graph bookbarcode-flow at revision 0

semantic-graph> add-node --kind input --label "ISBN input"
added node 1; revision 1

semantic-graph> add-node --kind step --label "Validate ISBN"
added node 2; revision 2

semantic-graph> add-edge --source 1 --target 2 --kind next
added edge 1; revision 3

semantic-graph> show compact
[1:input] ISBN input -[1:next]-> [2:step] Validate ISBN

semantic-graph> validate --model dag
valid DAG; 2 nodes, 1 edge; revision 3
```

The exact command grammar is undecided. The session should be easy for an LLM
to operate and still offer machine-readable responses when requested.

## Inspection operations

An agent needs bounded views rather than only a full JSON dump:

```text
show compact
show json
inspect-node <id>
inspect-edge <id>
neighbors <node-id>
stats
validate
```

These views should read current state without modifying it. Compact output must
remain deterministic so the agent can compare revisions reliably.

## Parameter packets

Long or reusable parameters can live in JSON files and be applied inside a
session:

```text
semantic-graph> apply packets/add-input-node.json
semantic-graph> apply packets/dag-validation.json
```

Potential packet scopes:

* one command and its parameters;
* a reusable node or edge template;
* model configuration;
* profile constraints;
* a protocol step sequence.

Packets should declare their purpose explicitly. A command packet should not be
mistaken for a profile or a complete graph.

## Protocols

A protocol is a reusable agent workflow over graph operations. An authoring
protocol might say:

```text
1. create or open graph
2. declare intended model
3. add a small group of nodes
4. inspect unconnected nodes
5. add relationships
6. validate structure
7. summarize unresolved questions
8. checkpoint
```

Other possible protocols include review, evidence attachment, merge, and
profile conformance. Protocols should compose tool capabilities rather than
duplicate graph logic.

## Session state

A session may need to track:

```text
active graph
graph revision
dirty/saved state
next node ID
next edge ID
active model or profile
response format
```

The graph file remains the durable artifact. A process session should not be
the only place where important state exists.

## Mutation safety

Each mutating command should follow:

```text
parse -> validate request -> copy current state -> mutate copy
      -> validate result -> commit state -> report revision
```

Saving to disk should use an atomic replacement. If multiple agents may edit
the same graph, an `expected_revision` check can reject stale mutations.

## Modularity boundary

Suggested separation:

```text
Graph model
    pure in-memory entities and invariants

Graph operations
    add, update, remove, inspect, validate

Graph store
    load, save, revision, atomic replacement

Session shell
    command parsing and active workspace

Protocols
    reusable sequences over operations
```

The terminal session should be an interface over the same operations exposed
to stdin JSON and Python callers, not a second implementation.

## Questions to test

* Does a persistent session materially reduce agent tokens and tool latency?
* Is shell-like syntax or newline-delimited JSON more reliable for agents?
* Should every command return JSON, compact text, or a configurable format?
* When should a mutation auto-save versus wait for an explicit checkpoint?
* How should an interrupted dirty session recover?
* Can parameter packets be composed without creating an implicit programming
  language?
* Where do protocols live: tool metadata, skills, or a separate registry?
