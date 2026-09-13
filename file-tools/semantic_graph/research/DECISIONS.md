# Research decisions

Only decisions that have been explicitly accepted should be recorded here.
Proposals and unresolved alternatives belong in `FIRST_NOTES.md` or
`OPEN_QUESTIONS.md`.

## Accepted direction

### Research before expansion

The graph model and agent workflow were researched before the v0.1.0 session
and persistence contract was implemented. Profiles and additional graph models
still require an explicit promotion from research.

### Conceptual scalability first

The initial scalability goal is supporting evolution from general graph models
to specialized models and profiles. Large-data optimization is deferred until
a concrete requirement exists.

### Separate identity spaces

Nodes and edges use independent graph-local integer identity spaces. A graph
also has a stable `graph_id`; a separate display title may default to that ID.

### Models before profiles

Structural graph models are the first research priority. Profiles remain a
separate documented concept and will be explored after the core model is
clearer.

### Composable model taxonomy

The research taxonomy proceeds from general to specialized but does not assume
that every graph feature belongs in one inheritance tree. Carrier structure,
orientation, multiplicity, shape constraints, and enrichments are studied as
composable dimensions. Convenience classes may later expose common
combinations without hiding the underlying structural choices.

### v0.1.0 implementation boundary

The first implementation contains only the general `Graph`, `Node`, and `Edge`
records plus a persistent terminal session. It assigns separate graph-local
integer identities to nodes and edges and supports `new`, `add-node`,
`add-edge`, `show`, `save`, `open`, `help`, and `exit`.

The v0.1.0 interface uses shell-like line commands, compact text responses, one
active graph, explicit saves, and raw JSON objects as node/edge parameter
packets.

Graph-model subclasses, profiles, topology algorithms, deletion, and mutation
remain outside v0.1.0. The base graph accepts cycles, self-loops, and parallel
edges; endpoint order is stored but not interpreted as a direction rule.
