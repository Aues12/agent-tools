# AGENTS.md - semantic_graph_visualizer

## Purpose

`semantic_graph_visualizer` renders Semantic CPG data into a small, local HTML
debug view.

It is an inspection tool, not an analysis tool.

It should help users and agents see:

* which CPG nodes exist
* which upstream tool produced each node or edge
* how edge kinds connect the graph
* where `corresponds_to` edges appear

## Scope

The tool consumes existing Semantic CPG JSON.

It must not:

* infer new semantic relationships
* mutate source files
* replace `semantic_cpg`
* require network access or browser-side dependencies

## Output Contract

The primary output is self-contained HTML.

The HTML may be returned as a string or written to an explicit output path.

Any file write must be requested through an operation that documents
`output_path`.

## Visualization Principle

This is a graph microscope for development.

Prefer simple, inspectable rendering over aesthetic complexity.

Filters and details are more important than advanced layout.
