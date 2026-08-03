# AGENTS.md - semantic_cpg

## Purpose

`semantic_cpg` is a deterministic analysis-merging tool.

Its purpose is to combine existing semantic analysis outputs into one Semantic
Code Property Graph without replacing the source analyses.

The first goal is not to infer new program meaning.

The first goal is:

```txt
semantic_ast
semantic_cfg
semantic_dfg
call_graph
    ↓
Semantic CPG
```

The tool should answer:

```txt
Which analysis nodes describe the same source region?
How do structural, control-flow, data-flow, and call relations coexist?
Which graph can projection layers consume consistently?
```

## Core Principle

Merge analysis outputs; do not erase provenance.

Every CPG node and edge should identify where it came from through `origin`.
Cross-analysis links created by this tool should use explicit reasons such as
`same_source_span` or `function_scope`.

## Scope

The first version should focus on local Python code analysis.

Supported initially:

```txt
semantic_ast module/class/function/statement containment
semantic_cfg control-flow nodes and edges
semantic_dfg value-flow nodes and edges
call_graph local function calls
cross-analysis source-span correspondences
```

Out of scope for the first version:

```txt
New type inference
Symbolic execution
Path feasibility proofs
Runtime tracing
Rewriting source analysis schemas
Replacing projection/view layers
```

## Definitions

### Semantic CPG

A Semantic Code Property Graph is a unified graph surface over multiple
deterministic analyses.

It is not the source code itself.

It is not meant to be rendered directly as the only UI.

It is the shared analysis model that projection layers can consume.

## Nodes

A CPG node wraps an analysis node or a structural unit.

Required fields:

```txt
id
kind
label
origin
```

Common fields:

```txt
scope
trace
properties
```

## Edges

A CPG edge represents structural containment, control flow, data flow, calls, or
cross-analysis correspondence.

Common edge kinds:

```txt
contains
has_cfg_node
has_dfg_node
calls
control_next
control_branch_true
control_branch_false
control_loop_body
control_loop_exit
control_loop_back
data_depends_on
data_produces
data_returns
data_passes_to_call
corresponds_to
```

## Line Numbers

Line numbers are 1-based. `end_line` values are inclusive.

## Validation

Run:

```sh
python3 -m unittest discover -s file-tools/semantic_cpg/tests
```
