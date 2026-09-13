# semantic_graph research

This directory is the design notebook for `semantic_graph`. It exists so graph
models, agent workflows, and protocol ideas can be explored before they become
tool contracts or implementation constraints.

Research documents are informative, not normative. Stable behavior belongs in
the tool's `README.md`, `SKILL.yaml`, tests, and the repository standards.

## Reading order

1. [FIRST_NOTES.md](FIRST_NOTES.md) — current shared context and provisional direction
2. [GRAPH_MODELS.md](GRAPH_MODELS.md) — working composable model taxonomy
3. [USE_CASES.md](USE_CASES.md) — coding and non-coding pressure tests
4. [AGENT_WORKFLOW.md](AGENT_WORKFLOW.md) — incremental authoring and inspection
5. [PROFILES.md](PROFILES.md) — domain-oriented constraints over models
6. [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) — unresolved decisions
7. [DECISIONS.md](DECISIONS.md) — decisions promoted from research

## Research order

The initial emphasis is graph models, beginning with the least constrained
ordinary graph. Profiles and protocols should be studied only far enough to
ensure that the core model does not block them later.

```text
ordinary graph
    -> structural axes: direction, multiplicity, loops
    -> shape constraints: DAG, tree, bipartite, connected
    -> enrichments: properties, weight, time, confidence
    -> profiles
    -> agent protocols and higher-level workflows
```

Do not expand the prototype merely because a model appears in these notes. A
feature should enter the tool only when a concrete workflow needs it.
