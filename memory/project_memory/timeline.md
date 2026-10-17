# Project Memory Timeline

This index summarizes the major development milestones of `agent-tools`.

Detailed notes live in:

* [chronology/2026-05.md](./chronology/2026-05.md)
* [chronology/2026-06.md](./chronology/2026-06.md)
* [chronology/2026-08.md](./chronology/2026-08.md)
* [chronology/2026-09.md](./chronology/2026-09.md)
* [chronology/2026-10.md](./chronology/2026-10.md)

## 2026-05-16

Repository bootstrap.

Core patterns appeared early:

* tool registry and JSON-oriented tool contracts
* first `semantic_ast` package
* initial tests, examples, and AGENTS/SKILL scaffolding
* minimal runtime orchestration core

## 2026-05-18

`semantic_ast` became layered:

* call graph extraction added
* compression artifacts added
* subtool structure introduced for parsing, compression, and call graph work

## 2026-05-19

Runtime scope was reduced.

Unused orchestration parts were removed to keep the system smaller and clearer.

## 2026-05-31

`ast_dump` landed and tool usage docs were streamlined.

## 2026-06-06

`semantic_cards` entered the repository as the next layer above
`semantic_ast`.

## 2026-06-11

The repository gained:

* stronger tool metadata standards
* `semantic_view` operations
* a large expansion of `memory/semantic_observatory/`

## 2026-06-13

The conceptual layer became more explicit:

* layered knowledge foundations
* philosophical supporting docs
* formal distinction between `depth` and `level`

## 2026-06-16

Working-note milestone:

* first `semantic_observatory_ui` prototype started
* single semantic card implemented in React/Vite
* elemental phase symbolism connected to card UI
* `project_memory` chronology method initialized

## 2026-06-24

Working-note milestone:

* `semantic_dfg` implemented as a deterministic local data-flow layer
* DFG schema, registry metadata, tests, examples, and playground artifact added
* `flow_level` introduced for value-flow distance
* DFG-local `depth` introduced for structural nesting inside function bodies

## 2026-06-28

Working-note milestone:

* Flat View v0.2 refactored into a four-column research desk layout
* `semantic_observatory_pipeline` introduced to connect AST, cards, DFG, and UI data
* local `.py` upload flow added through a small development API server
* generated Flat View data now omits statement and control-flow block cards by default

## 2026-06-30

Commit-backed milestone:

* Semantic Observatory dev runner added
* local UI iteration became easier to start and repeat

## 2026-08-02

Commit-backed milestone:

* `semantic_cfg` documented as the deterministic local control-flow layer
* `semantic_cpg` documented as the provenance-preserving merge layer over AST,
  CFG, DFG, and call graph outputs
* schema and registry metadata expanded to describe CFG and CPG as first-class
  tools
* the code-understanding pipeline became ready for projection layers over a
  unified analysis graph

## 2026-08-03

Working-note milestone:

* Semantic Observatory README and implementation map were synced with the
  current repository inventory
* document statuses were clarified as Active Core, Active Bridge, Experimental,
  and Future
* `semantic_observatory_pipeline` became CPG-aware while preserving Flat View's
  cards-plus-DFG adapter
* Function Mandala was kept deferred until construction rules and concept are
  stable enough for implementation

## 2026-09-06

Working-note milestone:

* Target, claim, basis, and symbolic interpretation boundaries were clarified
  while preserving the Observatory's ontological direction.
* Pipeline display classifications became inspectable through their rules and
  limitations; decoded-source fingerprints identify analyzed content.
* See [September notes](chronology/2026-09.md).

## 2026-10-11–12

Commit-backed milestones:

* Standalone Semantic Graph Viewer and a separate writing timeline experiment
  were added; viewer navigation was improved.
* The v0.1 graph path was distinguished from the legacy timeline, which moved
  under `experiments/`, and the repository's tool documentation was clarified.
* See [October notes](chronology/2026-10.md).

## 2026-10-17

Commit-backed milestone (`50136c6`):

* Six read-only book-editing micro-tools were added at the repository root for
  manuscript extraction and recurring editorial audits.
* See [October notes](chronology/2026-10.md).
