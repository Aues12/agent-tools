# Agent playground

Small, inspectable examples remain in `semantic_graph/`, `semantic_cfg/`, and
`semantic_dfg/`. The `semantic_graph` BookBarcode JSON is also copied into the
viewer because the viewer serves its own static assets and a research note
links to the playground copy. Both copies are intentionally kept.

[`archive/`](archive/) contains historical markdown summaries for earlier AST
and executor runs. Their large generated JSON outputs were removed from the
working tree because they are reproducible, stale, and carried absolute local
paths. A separate `forex_checker` analysis and the older book-reference graph
were removed because they derived from external source material. Their exact
pre-cleanup state is preserved in the private `agent-tools-dev` repository.
