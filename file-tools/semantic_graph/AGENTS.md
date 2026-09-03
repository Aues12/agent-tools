# AGENTS.md — semantic_graph

## Purpose

`semantic_graph` helps an LLM turn an already-understood process or context
into a small directed graph. It validates graph structure; it does not infer
meaning from source code or prose.

## Prototype scope

Keep the first version deliberately small:

* directed nodes and edges;
* caller-defined node and edge kinds;
* endpoint and duplicate validation;
* optional acyclic enforcement;
* JSON stdin/stdout and Python interfaces.

Do not add source parsing, graph visualization, persistence, LLM calls,
ontology management, or code analysis to this tool.

## Type policy

Kinds are open strings rather than a closed enum. Defaults exist only to make
small graph construction convenient:

```text
node kind: node
edge kind: relates_to
```

New kinds do not require a tool release. The result reports the kinds actually
used so consumers can inspect them.

## Graph policy

Graphs are directed. Cycles are accepted by default. A caller may request DAG
validation with `require_acyclic: true`; a detected cycle must then produce a
clear validation error.

The tool must remain deterministic and side-effect free. Preserve caller node
and edge order, generate no semantic claims, and never repair invalid endpoint
references silently.

## Development rule

Prefer a minimal contract over speculative graph features. Add a field or
operation only after a concrete workflow needs it.

Design exploration belongs under `research/`. Those notes are informative and
must not be treated as implemented behavior until the public metadata,
documentation, and tests are updated together.
