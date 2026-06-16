# call_graph

Extract deterministic function relationships from semantic AST structures.

## What it does

- Finds functions and methods in a semantic AST tree
- Extracts direct function calls from each function body
- Separates local calls from external calls
- Computes each local node's architectural `level`
- Produces graph nodes, edges, roots, leaves, and a readable tree

## Levels

`level` is the longest local call-path height beneath a function.

- Leaf functions have `level: 1`
- Callers have `1 + max(callee levels)`
- Cycles are grouped safely so traversal does not recurse forever

## Python usage

```python
from call_graph import build_call_graph
from tool import parse_source

tree = parse_source("def main():\n    helper()\n\ndef helper():\n    pass\n")
graph = build_call_graph(tree)

print(graph["tree"])
```

Output:

```text
main
└── helper
```

## Notes

- This module consumes semantic AST dictionaries; it does not parse source code directly.
- Dynamic dispatch and runtime behavior are intentionally out of scope.
- Local `self.method()` calls are resolved to class methods when possible.

## Validation

```bash
python3 -m unittest discover -s file-tools/semantic_ast/call_graph/tests
```
