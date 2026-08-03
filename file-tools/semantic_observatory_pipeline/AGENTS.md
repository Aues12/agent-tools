# AGENTS.md — semantic_observatory_pipeline

## Purpose

`semantic_observatory_pipeline` orchestrates existing semantic analysis tools
into one UI-ready analysis payload.

It does not replace upstream tools.

It coordinates:

```txt
Python source
    ↓
semantic_ast
    ↓
semantic_cards
    ↓
semantic_dfg
    ↓
semantic_cpg
    ↓
Semantic Observatory UI data
```

## Scope

The first version supports one Python source file at a time.

It should:

* parse Python source into semantic AST
* build semantic cards
* build local function-level DFGs
* build a provenance-preserving Semantic CPG for projection layers
* adapt generated artifacts into the Flat View card shape

It should not:

* infer symbolic meaning beyond deterministic display metadata
* mutate source files
* write artifacts unless a future operation explicitly documents that behavior
* perform repository-wide analysis

## UI Adapter Principle

The UI adapter may derive presentation metadata such as `role` and `phase`.

Derived metadata is not semantic truth.

Canonical semantic artifacts remain:

* semantic AST
* semantic cards
* data flow graph
* semantic CPG

## Line Numbers

All line numbers are 1-based and inclusive.
