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
