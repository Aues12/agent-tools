# Schema Specification

## Purpose

This document defines the stable semantic data shapes used by agent-tools.

It is a data contract, not a philosophical model. Conceptual background belongs
in `memory/semantic_observatory/`; this file describes the JSON-compatible
structures that tools and agents may rely on.

The schema standard covers the current code-understanding pipeline:

```text
Python source
  ↓
semantic_ast
  ↓
call_graph
  ↓
semantic_cards
  ↓
semantic_view
```

## General Rules

Semantic data should be:

* JSON-compatible.
* deterministic where practical.
* explicit about source location.
* stable enough for smaller models and runtimes to consume.
* narrow enough to avoid exposing incidental implementation details.

Line numbers are 1-based and `end_line` is inclusive.

Tools may omit empty values such as `null`, `[]`, and `{}` when their local
contract allows it.

Source text should not be embedded unless explicitly requested by the caller.

Schemas describe the stable minimum surface. Tools may include additional fields
when documented locally.

## Pipeline Semantics

Each pipeline stage is a localization of the same underlying code artifact:

```text
source text      = textual localization
semantic_ast     = structural localization
call_graph       = relation localization
semantic_cards   = card/interface localization
semantic_view    = presentation localization
```

The expected transformations are:

```text
source path                 -> semantic_ast.path
semantic_ast.path           -> semantic_card.trace.path
semantic_ast line/end_line  -> semantic_card.trace.line/end_line
semantic_card.trace         -> semantic_view.location
semantic AST containment    -> card.parent_id and card.children
semantic AST containment    -> contains relations
call_graph edges            -> calls relations
call_graph node.level       -> function card.level
AST traversal depth         -> card.depth
```

`depth` and `level` must not be collapsed:

```text
depth = structural nesting in a containment tree
level = architectural height in a relation graph
```

## Source Input

Source input is usually not a schema result, but tools should represent it with
explicit fields when needed.

Common fields:

```text
source   string  Python source text
path     string  Optional source path
encoding string  File encoding, default utf-8 when applicable
```

## semantic_ast Result

A semantic AST result represents parsed source structure.

Required fields:

```text
type      string  Usually "module" for root results
language  string  Source language, currently "python"
body      array   Child semantic AST nodes
stats     object  Summary counts
```

Common fields:

```text
path        string|null
line        integer
end_line    integer
line_count  integer
docstring   string|null
```

Minimum example:

```json
{
  "type": "module",
  "language": "python",
  "path": "example.py",
  "line": 1,
  "end_line": 10,
  "body": [],
  "stats": {}
}
```

## semantic_ast Node

A semantic AST node represents one parsed structural unit.

Required fields:

```text
type  string
```

Common fields:

```text
name       string
line       integer
end_line   integer
body       array
docstring  string|null
```

Node-specific fields are allowed. For example, function nodes may include
`args`, class nodes may include `bases`, and import-from nodes may include
Python's relative import `level`.

## call_graph Result

A call graph result represents direct local function-call relationships.

Required fields:

```text
type    string  Must be "call_graph"
nodes   array   Call graph nodes
edges   array   Call graph edges
roots   array   Node ids with no incoming local calls
leaves  array   Node ids with no outgoing local calls
stats   object  Summary counts
```

Common fields:

```text
path  string|null
tree  string
```

## call_graph Node

A call graph node represents one local function or method.

Required fields:

```text
id              string
name            string
qualified_name  string
calls           array
external_calls  array
level           integer
```

Common fields:

```text
scope     string|null
path      string|null
line      integer
end_line  integer
```

`level` is the longest local call-path height beneath the node. Leaf nodes have
`level: 1`.

## call_graph Edge

A call graph edge represents one resolved local call.

Required fields:

```text
caller  string  Source function id
callee  string  Target function id
call    string  Original call surface
```

Edges should refer only to local/internal calls already resolved by the call
graph tool. External calls belong in `external_calls` on the node.

## semantic_cards Result

A semantic cards result represents navigable cards and separate relation
records.

Required fields:

```text
type       string  Must be "semantic_cards"
language   string
root_ids   array
cards      array
relations  array
stats      object
```

Common fields:

```text
path  string|null
```

## Semantic Card

A Semantic Card is a localized interface to an observation target such as a
module, class, function, block, or statement.

Required fields:

```text
id              string
kind            string
title           string
depth           integer
level           integer
parent_id       string|null
children        array
qualified_name  string
trace           object
```

Common fields:

```text
surface  object
detail   object
```

`depth` comes from structural traversal.

`level` comes from relation analysis where available. For function cards, it
should come from call graph height. Non-function container cards may lift level
from their children.

Minimum example:

```json
{
  "id": "function:example.main",
  "kind": "function",
  "title": "main",
  "depth": 1,
  "level": 3,
  "parent_id": "module:example",
  "children": [],
  "qualified_name": "example.main",
  "trace": {
    "path": "example.py",
    "line": 1,
    "end_line": 5
  }
}
```

## Semantic Relation

A semantic relation connects cards or links a card to an external target.

Required fields:

```text
kind       string
source_id  string
```

Target fields:

```text
target_id  string  Internal card target
target     string  External named target
```

At least one target field should normally be present.

Common fields:

```text
label  string
trace  object
```

Common relation kinds:

```text
contains
imports
inherits
calls
```

## semantic_view Outputs

Semantic views are presentation localizations over existing semantic card
results. They should not replace canonical `semantic_cards` output.

### summary_view

Required fields:

```text
type       string  Must be "semantic_summary_view"
source     string|null
counts     object
top_level  array
relations  array
```

### tree_view

Required fields:

```text
type    string  Must be "semantic_tree_view"
format  string  Usually "text"
tree    string
```

### card_view

Required fields:

```text
type       string  Must be "semantic_card_view"
card_id    string
kind       string
title      string
depth      integer|null
level      integer|null
location   string|null
parent_id  string|null
children   array
relations  object
summary    string
```

## Compatibility Rules

Schema changes should be treated as compatibility-sensitive.

Additive fields are preferred.

Renaming or removing stable fields requires updating:

* local README files
* relevant tests
* registry metadata when applicable
* this schema specification

When conceptual terminology changes, implementation schemas should change only
after the data contract is clear.
