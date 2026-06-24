# AGENTS.md — semantic_dfg

## Purpose

`semantic_dfg` is a deterministic data-flow analysis tool.

Its purpose is to read Python source code and produce a simple, explicit Data Flow Graph.

The first goal is not symbolic interpretation.

The first goal is:

```txt
Source Code
    ↓
AST
    ↓
Data Flow Graph
```

The tool should answer:

```txt
Which value depends on which previous value?
Which operation produced this value?
Where does a value enter, transform, and leave the local scope?
```

This tool belongs between `semantic_ast` and `semantic_cards`.

```txt
semantic_ast
    ↓
semantic_dfg
    ↓
semantic_cards
    ↓
semantic_view
```

---

## Core Principle

Start with plain data flow.

Do not introduce phases, elements, rings, modalities, zodiacal correspondences, or archetypal operations in the first implementation.

The first version must remain technically minimal and deterministic.

```txt
Good:
path → text → tree → cards

Avoid for v1:
Earth → Fire → Air → Water → Earth
```

Symbolic and epistemic layers may be added later, after the base DFG is stable.

---

## Scope

The first version should focus on local Python function-level data flow.

Supported initially:

```txt
Function definitions
Assignments
Variable references
Function calls
Return statements
Simple expression dependencies
```

Out of scope for the first version:

```txt
Interprocedural analysis
Runtime behavior
Dynamic imports
Reflection
Class inheritance resolution
Async execution semantics
Symbolic phase inference
Type inference
Control-flow-sensitive precision
```

---

## Definitions

### Data Flow Graph

A Data Flow Graph describes how values move through code.

Example:

```python
def parse_file(path):
    text = read_file(path)
    tree = ast.parse(text)
    return tree
```

DFG:

```txt
path
  ↓ read_file
text
  ↓ ast.parse
tree
  ↓ return
return_value
```

---

## Nodes

A DFG node represents a value, binding, input, output, or intermediate object.

Recommended node kinds:

```txt
parameter
binding
literal
call_result
return_value
attribute
unknown
```

Example node:

```json
{
  "id": "parse_file:text",
  "name": "text",
  "kind": "binding",
  "scope": "parse_file",
  "flow_level": 1,
  "depth": 1,
  "lineno": 2
}
```

`flow_level` is specific to DFG output. It represents the longest upstream
value-flow distance inside the local function graph. Source-like values such as
parameters, literals, and unknown values start at `0`.

Do not confuse `flow_level` with semantic card `level`, which represents
architectural height in a relation graph.

`depth` is local structural nesting inside the analyzed function. Parameters
start at `0`, top-level function body nodes usually have `1`, and nodes created
inside nested blocks such as `if` or `for` increase from there.

---

## Edges

A DFG edge represents dependency or production.

Recommended edge kinds:

```txt
depends_on
produces
returns
passes_to_call
```

Example edge:

```json
{
  "from": "parse_file:path",
  "to": "parse_file:text",
  "kind": "depends_on",
  "operation": "read_file",
  "lineno": 2
}
```

---

## Output Schema

The tool should emit JSON.

Top-level format:

```json
{
  "success": true,
  "tool": "semantic_dfg",
  "version": "0.1.0",
  "result": {
    "file": "example.py",
    "functions": [
      {
        "name": "parse_file",
        "nodes": [],
        "edges": [],
        "returns": []
      }
    ]
  },
  "errors": []
}
```

If analysis fails, return:

```json
{
  "success": false,
  "tool": "semantic_dfg",
  "version": "0.1.0",
  "result": null,
  "errors": [
    {
      "message": "Could not parse source file.",
      "kind": "SyntaxError"
    }
  ]
}
```

Never print non-JSON diagnostic text to stdout.

---

## CLI Contract

The CLI should accept JSON through stdin and return JSON through stdout.

Example input:

```json
{
  "operation": "build_dfg_from_file",
  "path": "examples/simple_pipeline.py"
}
```

Example output:

```json
{
  "success": true,
  "result": {
    "functions": []
  },
  "errors": []
}
```

Recommended operations:

```txt
build_dfg_from_file
build_dfg_from_source
summarize_dfg
```

Do not add phase validation operations in v1.

---

## Suggested File Structure

```txt
semantic_dfg/
├── AGENTS.md
├── README.md
├── SKILL.yaml
├── semantic_dfg.py
├── tool.py
├── schema.py
├── builder.py
├── summarizer.py
├── examples/
│   ├── simple_pipeline.py
│   └── parse_file.py
└── tests/
    ├── test_builder.py
    ├── test_schema.py
    └── test_tool.py
```

---

## Module Responsibilities

### semantic_dfg.py

CLI entrypoint.

Responsibilities:

```txt
Read JSON from stdin
Dispatch operation
Print JSON to stdout
Return process exit code
```

---

### tool.py

Operation dispatcher.

Responsibilities:

```txt
Validate requested operation
Call builder or summarizer
Wrap output in standard success/error format
```

---

### schema.py

Shared data structures.

Recommended dataclasses:

```python
@dataclass
class DFGNode:
    id: str
    name: str
    kind: str
    scope: str
    flow_level: int | None = None
    depth: int | None = None
    lineno: int | None = None
    col_offset: int | None = None


@dataclass
class DFGEdge:
    source: str
    target: str
    kind: str
    operation: str | None = None
    lineno: int | None = None


@dataclass
class FunctionDFG:
    name: str
    nodes: list[DFGNode]
    edges: list[DFGEdge]
    returns: list[str]
```

Keep schema simple.

Avoid premature abstraction.

---

### builder.py

AST-to-DFG builder.

Responsibilities:

```txt
Parse source with ast
Visit function definitions
Track parameters
Track assignments
Track dependencies inside expressions
Track function call inputs
Track return dependencies
Produce FunctionDFG objects
```

The builder should be deterministic.

Do not use LLM interpretation.

Do not infer semantic phases.

---

### summarizer.py

Human-readable DFG summary.

Responsibilities:

```txt
Convert DFG JSON into a compact text or markdown summary
Show main value chain
Show unresolved or unknown dependencies
```

Example summary:

```txt
Function: parse_file

path → text via read_file
text → tree via ast.parse
tree → return_value via return
```

---

## Initial Analysis Rules

### Function Parameters

Each function parameter becomes a node.

Example:

```python
def f(path):
    ...
```

Node:

```json
{
  "name": "path",
  "kind": "parameter"
}
```

---

### Simple Assignment

Example:

```python
text = read_file(path)
```

Create:

```txt
path → text
```

with operation:

```txt
read_file
```

---

### Expression Assignment

Example:

```python
total = price * quantity
```

Create:

```txt
price → total
quantity → total
```

with operation:

```txt
BinOp
```

---

### Call Assignment

Example:

```python
tree = ast.parse(text)
```

Create:

```txt
text → tree
```

with operation:

```txt
ast.parse
```

---

### Return Statement

Example:

```python
return tree
```

Create:

```txt
tree → return_value
```

with operation:

```txt
return
```

---

### Nested Calls

Example:

```python
x = f(g(a))
```

For v1, a simplified output is acceptable:

```txt
a → x
```

with operation:

```txt
f(g(...))
```

A later version may expand this into:

```txt
a → g_result → x
```

Do not overcomplicate v1.

---

### Multiple Assignment

Example:

```python
a, b = get_pair(x)
```

For v1, either support simply or mark as partially supported.

Acceptable:

```txt
x → a
x → b
```

operation:

```txt
get_pair
```

---

### Attribute Access

Example:

```python
name = user.name
```

For v1:

```txt
user → name
```

operation:

```txt
attribute_access
```

---

### Subscript Access

Example:

```python
item = data[0]
```

For v1:

```txt
data → item
```

operation:

```txt
subscript_access
```

---

## Determinism Rules

The tool must not guess.

If a dependency cannot be resolved, mark it as unknown.

Use explicit unknown nodes:

```json
{
  "id": "unknown:external_value",
  "name": "external_value",
  "kind": "unknown"
}
```

Do not invent semantic meaning.

Do not infer intent from function names beyond using them as operation labels.

---

## Error Handling

All errors should be structured.

Examples:

```txt
SyntaxError
FileNotFoundError
UnsupportedNodeError
InvalidOperationError
```

Unsupported syntax should not crash the whole tool if partial analysis is possible.

Prefer:

```json
{
  "success": true,
  "warnings": [
    {
      "kind": "UnsupportedNode",
      "message": "With statements are not fully supported yet.",
      "lineno": 8
    }
  ]
}
```

---

## Testing Priorities

Start with small examples.

Required tests:

```txt
parameter nodes are created
simple assignment dependencies are detected
call assignment dependencies are detected
return dependencies are detected
multiple dependencies are detected
JSON output is stable
unsupported nodes do not crash unexpectedly
```

Example test input:

```python
def parse_file(path):
    text = read_file(path)
    tree = parse(text)
    return tree
```

Expected chain:

```txt
path → text → tree → return_value
```

---

## Development Stages

### Stage 1 — Plain DFG

Goal:

```txt
Extract simple function-level data flow.
```

No phases.

No elements.

No rings.

No semantic cards.

---

### Stage 2 — DFG Summary

Goal:

```txt
Produce readable summaries of value movement.
```

Example:

```txt
path enters parse_file
path produces text through read_file
text produces tree through parse
tree is returned
```

---

### Stage 3 — DFG Relations for Cards

Goal:

```txt
Prepare DFG output for semantic_cards.
```

The DFG should eventually provide relations such as:

```txt
produces
depends_on
returns
feeds
```

These can later become card edges.

---

### Stage 4 — Phase Layer

Only after plain DFG is reliable, add optional phase metadata.

Important:

```txt
Phases must be declared, not guessed.
```

A later phase contract may look like:

```json
{
  "path": "Earth",
  "text": "Air",
  "tree": "Earth"
}
```

The validator may then check visible order.

But phase validation is not part of v1.

---

### Stage 5 — Phase Order Validation

Later, the tool may validate declared phase arcs against:

```txt
Earth → Fire → Air → Water → Earth
```

Rules:

```txt
Ring closure is optional.
Visible order is mandatory.
No confidence scoring.
No probabilistic classification.
No automatic symbolic inference.
```

---

## Relationship to semantic_ast

`semantic_ast` describes code structure.

`semantic_dfg` describes value movement.

Do not duplicate all AST information.

Use only what is needed to explain data flow.

```txt
semantic_ast:
Assign
Call
Return

semantic_dfg:
path → text → tree → return_value
```

---

## Relationship to semantic_cards

`semantic_cards` should not be responsible for discovering raw data flow.

It should consume DFG output and convert important nodes and edges into navigable semantic cards.

Possible future mapping:

```txt
DFG node
    → semantic object card

DFG edge
    → semantic relation

DFG chain
    → semantic arc
```

---

## Design Philosophy

Keep the first version small.

Prefer clear partial truth over impressive but unstable analysis.

The tool should be:

```txt
deterministic
inspectable
testable
JSON-first
scope-aware
easy to extend
```

The purpose is not to understand all Python.

The purpose is to establish a reliable foundation for observing how information moves through code.

---

## Non-Goals

Do not implement these in v1:

```txt
Full Python static analysis
Complete compiler-grade SSA
Runtime tracing
Machine-learning-based inference
LLM-based classification
Automatic phase detection
Automatic symbolic interpretation
Zodiac or element classification
Visualization UI
```

---

## Final Rule

Build the riverbed before naming the waters.

First extract the plain data flow.

Only after the flow is technically stable should symbolic phase, element, ring, or semantic seal layers be added.
