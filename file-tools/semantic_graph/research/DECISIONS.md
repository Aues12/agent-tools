# Research decisions

Only decisions that have been explicitly accepted should be recorded here.
Proposals and unresolved alternatives belong in `FIRST_NOTES.md` or
`OPEN_QUESTIONS.md`.

## Accepted direction

### Research before expansion

The graph model and agent workflow will be researched before the prototype is
expanded with persistence, sessions, profiles, or additional graph classes.

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

### Interactive authoring is a research target

A persistent terminal session, short graph commands, reusable JSON parameter
packets, and modular agent protocols will be evaluated as an authoring model.
No session command contract has been finalized yet.
