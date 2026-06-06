# AGENTS.md — file-tools

This directory contains local file-oriented tools used by agents to inspect, transform, and summarize project files.

The tools in this directory should remain small, deterministic, composable, and easy to call through a JSON stdin/stdout interface.

## General Design Principles

Prefer simple tools over large applications.

Each tool should do one clear job and return structured data that another tool, agent, or UI can consume.

Avoid hidden side effects. A read/analyze tool should not modify user files unless its purpose is explicitly to write or transform files.

Prefer deterministic extraction before LLM interpretation.

The usual order should be:

```text
source file
↓
deterministic parser
↓
structured representation
↓
optional compression
↓
optional LLM annotation
↓
visualization or UI
```

The file-tools layer should provide reliable ground truth. Higher layers may add meaning, labels, summaries, or visual metaphors.

## Semantic AST Direction

The `semantic_ast` tool is the foundation for code understanding.

Its primary responsibility is not to make a beautiful graph. Its primary responsibility is to produce a faithful, navigable, structured representation of source code.

The preferred pipeline is:

```text
Python source
↓
normalized semantic AST
↓
compressed semantic AST
↓
semantic cards
↓
semantic relations
↓
semantic universe / visualization
```

The visual layer should come after the semantic structure is stable.

Do not rush toward graph layouts, force simulations, star maps, or UI effects before the underlying tree and relation model are clear.

## Tree First, Graph Second

Preserve the containment tree.

The general-to-specific navigation depends on parent-child structure:

```text
project
↓
module
↓
class / function
↓
block
↓
statement
↓
expression
```

This tree should remain stable even when graph relations are added later.

Call graphs, semantic similarity, conceptual clusters, and force relations should be represented as separate relations.

Do not mix containment with call edges.

Containment answers:

```text
What is inside what?
```

Relations answer:

```text
What is connected to what?
```

Both are needed, but they should remain distinct.

## Semantic Cards

A semantic card is a bounded observation unit.

Not every AST node should become a card.

A node should become a card only when it is meaningful to inspect it as its own unit.

Good early card types:

```text
project
module
class
function
block
statement
```

Expression-level cards may be added later, but should not be part of the first version unless needed.

A card should support general-to-specific and specific-to-general navigation.

Each card should have at least:

```json
{
  "id": "function:package.module.name",
  "kind": "function",
  "title": "name",
  "level": 3,
  "parent_id": "module:package.module",
  "children": [],
  "source": {
    "path": "package/module.py",
    "line": 10,
    "end_line": 42
  }
}
```

## Card Layers

Cards should be designed in layers.

The visible card surface should stay simple.

Suggested layers:

```text
surface
detail
trace
```

### Surface

The surface is what appears first in the UI.

It should be short and calm.

### Detail

The detail layer is shown when the card is opened.

It should work like a technical docstring for the card.

It should explain the unit in a concise, useful way without overwhelming the user.

Good detail docs are:

```text
short
specific
neutral
technical
useful
```

### Trace

Trace connects the card back to source code.

It should make the card auditable.

By default, avoid embedding large source excerpts. Use line ranges unless the caller explicitly asks for source text.

## Relations

Relations should be stored separately from cards.

Early relation kinds:

```text
contains
calls
imports
inherits
uses
returns
similar_to
```

Containment may be duplicated as a relation for graph consumers, but the canonical containment model should remain `parent_id` and `children`.

## Quality Bar

A tool is good when:

```text
it is easy to call
its output is predictable
its schema is stable
its errors are clear
its result can be inspected by a human
its result can be consumed by another tool
```

When in doubt, prefer a smaller deterministic structure over a larger impressive one.

The goal is not to produce many nodes.

The goal is to produce the right observation units.
