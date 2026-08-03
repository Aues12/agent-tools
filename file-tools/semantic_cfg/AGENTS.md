# AGENTS.md - semantic_cfg

## Purpose

`semantic_cfg` is a deterministic control-flow analysis tool.

Its purpose is to read Python source code and produce a simple, explicit
Control Flow Graph for each local function.

The first goal is not compiler-grade path proof.

The first goal is:

```txt
Source Code
    ↓
semantic_ast
    ↓
Control Flow Graph
```

The tool should answer:

```txt
Where can execution go next?
Which branches and loops shape local execution?
Which statements terminate or redirect local flow?
```

This tool belongs beside `semantic_dfg` in the code-understanding layer.

```txt
semantic_ast
    ↓
semantic_cfg / semantic_dfg
    ↓
semantic_cards
    ↓
semantic_view
```

## Core Principle

Start with plain local control flow.

Do not introduce path feasibility, symbolic execution, type inference, runtime
state, or interprocedural behavior in the first implementation.

The first version must remain technically minimal and deterministic.

## Scope

The first version should focus on local Python function-level control flow.

Supported initially:

```txt
Function definitions
Sequential statements
if / else
for / while loops
return
raise
break / continue
try / except / else / finally with partial-analysis warnings
```

Out of scope for the first version:

```txt
Interprocedural analysis
Runtime behavior
Dynamic dispatch
Exception semantics beyond simple handler paths
Path feasibility proofs
SSA construction
Type inference
Async runtime semantics
```

## Definitions

### Control Flow Graph

A Control Flow Graph describes possible execution transitions.

Example:

```python
def choose(flag):
    if flag:
        return 1
    return 0
```

CFG:

```txt
entry
  ↓
if flag
  ├─ true  → return → exit
  └─ false → return → exit
```

## Nodes

A CFG node represents an entry point, exit point, statement, branch, loop, jump,
return, raise, or join point.

Recommended node kinds:

```txt
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

Example node:

```json
{
  "id": "function:example.choose:branch:1",
  "kind": "branch",
  "label": "if flag",
  "scope": "example.choose",
  "depth": 1,
  "line": 2,
  "end_line": 3
}
```

`depth` is local structural nesting inside the analyzed function. Function entry
and exit nodes start at `0`; top-level body statements usually have `1`.

## Edges

A CFG edge represents a possible transfer of control.

Recommended edge kinds:

```txt
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

Example edge:

```json
{
  "source": "function:example.choose:branch:1",
  "target": "function:example.choose:return:2",
  "kind": "branch_true",
  "condition": "true",
  "lineno": 2
}
```

## Output Schema

The tool should emit the standard tool envelope through `tool.py` and
`semantic_cfg.py`.

Result format:

```json
{
  "type": "control_flow_graph",
  "language": "python",
  "path": "example.py",
  "functions": [
    {
      "id": "function:example.choose",
      "name": "choose",
      "qualified_name": "example.choose",
      "entry": "function:example.choose:entry",
      "exit": "function:example.choose:exit",
      "nodes": [],
      "edges": []
    }
  ],
  "warnings": [],
  "stats": {}
}
```

If analysis is partial, emit structured warnings instead of guessing.

## Line Numbers

Line numbers are 1-based. `end_line` values are inclusive.

## Validation

Run:

```sh
python3 -m unittest discover -s file-tools/semantic_cfg/tests
```
