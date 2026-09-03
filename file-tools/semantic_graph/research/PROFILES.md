# Profiles

## Working distinction

A graph model defines structural possibilities and invariants. A profile
applies a model to a recognizable domain or workflow and may add vocabulary or
constraints.

```text
DAG model
├── dependency graph profile
├── build pipeline profile
└── approval workflow profile
```

Profiles are not the current research priority. This document exists to keep
the distinction visible while graph models are studied.

## Model composition before profile meaning

A profile should name its required structure explicitly. For example:

```text
dependency graph profile
    orientation: directed
    cycles: forbidden unless profile says otherwise
    likely edge kind: depends_on

approval workflow profile
    orientation: directed
    cycles: allowed for revision/rework
    likely node kinds: activity, decision, outcome

assignment profile
    partitioning: bipartite
    optional enrichment: weight
    likely edge kind: eligible_for
```

The examples show why a domain name is insufficient as a structural model.
`Workflow`, for instance, does not imply DAG: retry and revision paths may be
valid cycles.

See [GRAPH_MODELS.md](GRAPH_MODELS.md) for the structural taxonomy and
[USE_CASES.md](USE_CASES.md) for candidate domains.

## Possible profile contents

A future profile may declare:

* required or recommended graph model;
* allowed, required, or recommended node kinds;
* allowed, required, or recommended edge kinds;
* additional validation constraints;
* default attributes;
* reusable parameter packets;
* compatible agent protocols;
* summary or inspection preferences.

The ordinary graph must remain usable without a profile. Profiles should be
data rather than executable code unless a concrete requirement proves that
insufficient.

## Deferred questions

* Can multiple profiles be composed?
* Are profile kinds recommendations or closed vocabularies?
* How are conflicting constraints reported?
* Should profiles be registered centrally or remain local artifacts?
* Does a protocol select a profile, or does the graph declare one?
