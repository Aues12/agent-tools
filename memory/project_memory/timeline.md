# Project Memory Timeline

This index summarizes the major development milestones of `agent-tools`.

Detailed notes live in:

* [chronology/2026-05.md](./chronology/2026-05.md)
* [chronology/2026-06.md](./chronology/2026-06.md)

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
