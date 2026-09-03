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
semantic_cfg / semantic_dfg
  ↓
call_graph
  ↓
semantic_cpg
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
semantic_cfg     = control-flow localization
semantic_dfg     = value-flow localization
call_graph       = relation localization
semantic_cpg     = unified analysis localization
semantic_cards   = card/interface localization
semantic_view    = presentation localization
```

`semantic_graph` is separate from this extraction pipeline. It validates a
small, caller-authored directed graph and does not infer graph meaning from
source code.

## semantic_graph Result

A semantic graph represents caller-supplied concepts and directed relations.
Only structural fields are standardized; `kind` values remain open strings so
an LLM or workflow can introduce vocabulary as needed.

Required graph fields:

```text
type      string   Must be "semantic_graph"
directed  boolean  Must be true
acyclic   boolean  Computed from the supplied edges
nodes     array
edges     array
kinds     object   Distinct node and edge kinds used
stats     object   Node and edge counts
```

Required node fields:

```text
id     string
label  string
kind   string
```

Required edge fields:

```text
source  string  Existing node id
target  string  Existing node id
kind    string
```

Nodes and edges may include an `attributes` object. Graphs permit directed
cycles by default. Callers may request acyclic validation when their intended
graph is a DAG.

The expected transformations are:

```text
source path                 -> semantic_ast.path
semantic_ast.path           -> semantic_card.trace.path
semantic_ast line/end_line  -> semantic_card.trace.line/end_line
semantic_card.trace         -> semantic_view.location
semantic AST containment    -> card.parent_id and card.children
semantic AST containment    -> contains relations
semantic AST statements      -> semantic_cfg nodes and edges
semantic AST expressions    -> semantic_dfg nodes and edges
call_graph edges            -> calls relations
call_graph node.level       -> function card.level
semantic_cfg node.depth      -> local structural depth for CFG consumers
semantic_dfg node.flow_level -> value-flow distance for DFG consumers
semantic_dfg node.depth      -> local structural depth for DFG consumers
semantic_cpg origin          -> analysis provenance for projection consumers
semantic_cpg corresponds_to  -> source-span links between analysis nodes
AST traversal depth         -> card.depth
```

`depth` and `level` must not be collapsed:

```text
depth = structural nesting in a containment tree
level = architectural height in a relation graph
```

DFG value-flow position uses `flow_level` instead of `level` so it is not
confused with call graph or card architectural height.

DFG nodes may also expose `depth`, which is local structural nesting inside the
function DFG. Parameters usually have `depth: 0`; top-level statements inside a
function usually produce nodes with `depth: 1`; nested block statements increase
that value.

CFG nodes may also expose `depth`, which is local structural nesting inside the
function CFG. Entry and exit nodes usually have `depth: 0`; top-level statements
inside a function usually have `depth: 1`; nested branch and loop body nodes
increase that value.

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

## semantic_dfg Result

A semantic DFG result represents local function-level value dependencies.

Required fields:

```text
type       string  Must be "data_flow_graph"
language   string  Source language, currently "python"
functions  array   Function-level DFG records
stats      object  Summary counts
```

Common fields:

```text
path      string|null
warnings  array
```

`semantic_dfg` is intentionally local and deterministic. It does not perform
type inference, interprocedural analysis, runtime tracing, SSA construction, or
symbolic phase inference.

## semantic_dfg Function

A semantic DFG function record describes value movement inside one local
function or method.

Required fields:

```text
id              string
name            string
qualified_name  string
nodes           array
edges           array
returns         array
```

Common fields:

```text
path      string|null
line      integer
end_line  integer
warnings  array
```

## semantic_dfg Node

A semantic DFG node represents a value, binding, input, output, literal, call
result, attribute, or unknown dependency.

Required fields:

```text
id     string
name   string
kind   string
scope  string
```

Common fields:

```text
flow_level  integer
depth       integer
lineno      integer
col_offset  integer
```

`flow_level` is the longest upstream value-flow distance inside the local
function DFG. Source-like nodes such as parameters, literals, and unresolved
unknown values usually have `flow_level: 0`. A node produced from upstream
values has `1 + max(source.flow_level)` across incoming DFG edges.

Common node kinds:

```text
parameter
binding
literal
call_result
return_value
attribute
unknown
```

An `attribute` node should preserve the complete statically identifiable path,
such as `self.width_mm` or `config.output.path`. If the receiver cannot be
identified deterministically, producers must not invent a complete path.

## semantic_dfg Edge

A semantic DFG edge represents dependency or production.

Required fields:

```text
source  string  Source DFG node id
target  string  Target DFG node id
kind    string
```

Common fields:

```text
operation  string|null
lineno     integer
```

Common edge kinds:

```text
depends_on
produces
returns
passes_to_call
```

## semantic_cfg Result

A semantic CFG result represents local function-level control flow.

Required fields:

```text
type       string  Must be "control_flow_graph"
language   string  Source language, currently "python"
functions  array   Function-level CFG records
stats      object  Summary counts
```

Common fields:

```text
path      string|null
warnings  array
```

`semantic_cfg` is intentionally local and deterministic. It does not perform
type inference, interprocedural analysis, runtime tracing, symbolic execution,
path feasibility proofs, or SSA construction.

## semantic_cfg Function

A semantic CFG function record describes possible execution transitions inside
one local function or method.

Required fields:

```text
id              string
name            string
qualified_name  string
entry           string
exit            string
nodes           array
edges           array
```

Common fields:

```text
path      string|null
line      integer
end_line  integer
exits     array
warnings  array
```

## semantic_cfg Node

A semantic CFG node represents an entry point, exit point, statement, branch,
loop, jump, return, raise, or join point.

Required fields:

```text
id     string
kind   string
label  string
scope  string
```

Common fields:

```text
depth     integer
line      integer
end_line  integer
```

Common node kinds:

```text
entry
exit
statement
branch
loop
return
raise
break
continue
join
```

## semantic_cfg Edge

A semantic CFG edge represents a possible transfer of control.

Required fields:

```text
source  string  Source CFG node id
target  string  Target CFG node id
kind    string
```

Common fields:

```text
condition  string|null
lineno     integer
```

Common edge kinds:

```text
next
branch_true
branch_false
loop_body
loop_exit
loop_back
break
continue
return
exception
```

## semantic_cpg Result

A semantic CPG result represents a unified graph surface over semantic AST, CFG,
DFG, and call graph outputs.

Required fields:

```text
type    string  Must be "semantic_code_property_graph"
nodes   array   Unified CPG nodes
edges   array   Unified CPG edges
stats   object  Summary counts
```

Common fields:

```text
language    string
path        string|null
warnings    array
provenance  object
```

`semantic_cpg` is intentionally a merger and provenance-preserving analysis
surface. It does not replace the source analysis schemas and does not perform
type inference, symbolic execution, runtime tracing, or path feasibility
proofs.

## semantic_cpg Node

A semantic CPG node wraps a structural unit or a node from an upstream analysis.

Required fields:

```text
id      string
kind    string
label   string
origin  object
```

Common fields:

```text
scope       string|null
trace       object
properties  object
```

`origin.tool` identifies the upstream source, such as `semantic_ast`,
`semantic_cfg`, `semantic_dfg`, `call_graph`, or `semantic_cpg` for merge-created
links.

Common node kinds:

```text
module
class
function
ast_statement
control_entry
control_exit
control_statement
control_branch
control_loop
control_join
control_return
control_raise
control_jump
value_parameter
value_binding
value_literal
value_call_result
value_return
value_unknown
```

## semantic_cpg Edge

A semantic CPG edge represents containment, local control flow, local data flow,
local calls, or cross-analysis correspondence.

Required fields:

```text
source  string
target  string
kind    string
origin  object
```

Common fields:

```text
condition   string|null
trace       object
properties  object
```

Common edge kinds:

```text
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
control_break
control_continue
control_return
control_exception
data_depends_on
data_produces
data_returns
data_passes_to_call
corresponds_to
```

`corresponds_to` edges should include an origin reason such as
`same_source_span`. They connect related upstream analysis nodes without
collapsing them into a single node.

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
