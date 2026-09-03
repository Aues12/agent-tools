# Graph models

## Purpose

Study structural graph models from the simplest and least constrained form
toward more specialized forms. Inclusion here does not imply implementation.

## Initial sequence

### Ordinary graph

The baseline model: identifiable nodes connected by edges. Research questions:

* Is direction graph-wide, edge-local, or absent?
* Are self-loops allowed?
* Are parallel edges allowed?
* Do edges require their own identity?

### Directed graph

Every edge has a source and target. Useful for process, dependency, state, and
causal descriptions.

### Undirected graph

An edge represents a symmetric relation. Useful for association, similarity,
and peer networks.

### Directed acyclic graph

A directed graph with no directed cycle. Adds cycle validation and enables
topological ordering. Potential profiles include dependency graphs, build
pipelines, and approval workflows.

### Tree and forest

Acyclic hierarchical structures with stronger root and parent constraints.

### Multigraph

Allows multiple distinguishable edges between the same endpoints. This model
makes stable edge identity important.

## Models to examine later

* bipartite graph;
* property graph;
* state-transition graph;
* knowledge graph;
* weighted graph;
* temporal graph;
* hypergraph.

These categories overlap. Research should identify which concepts are true
models, which are cross-cutting policies, and which are better represented as
profiles.

## Evaluation template

For each model, record:

```text
definition
additional invariants
capabilities enabled
minimum schema impact
compatible profiles
composition conflicts
example agent workflow
reasons to defer implementation
```
