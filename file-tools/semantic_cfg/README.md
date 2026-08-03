# semantic_cfg

`semantic_cfg` builds deterministic local control-flow graphs from Python
semantic AST trees.

It answers:

```text
Where can execution go next?
Which branches and loops shape local execution?
Which statements terminate or redirect local flow?
```

The first version intentionally avoids symbolic execution, type inference, path
feasibility proofs, SSA construction, runtime tracing, and interprocedural
analysis.

## Pipeline

```text
Python source
  -> semantic_ast
  -> semantic_cfg
  -> semantic_cards
  -> semantic_view
```

`semantic_cfg` consumes the normalized dictionaries produced by `semantic_ast`.
Convenience operations can parse source or files first.

## Operations

### build_cfg

Build a CFG from an existing semantic AST module tree.

```json
{
  "operation": "build_cfg",
  "params": {
    "tree": {
      "type": "module",
      "language": "python",
      "body": []
    }
  }
}
```

### build_cfg_from_source

Parse source through `semantic_ast`, then build a CFG.

```json
{
  "operation": "build_cfg_from_source",
  "params": {
    "source": "def choose(flag):\n    if flag:\n        return 1\n    return 0\n",
    "path": "example.py"
  }
}
```

### build_cfg_from_file

Read and parse a Python file through `semantic_ast`, then build a CFG.

### summarize_cfg

Convert a CFG result into compact human-readable summaries.

## Example

Input:

```python
def choose(flag):
    if flag:
        return 1
    return 0
```

CFG summary:

```text
entry -> if flag via next
if flag -> return via branch_true [true]
if flag -> if join via branch_false [false]
return -> exit via return
if join -> return via next
return -> exit via return
```

## Validation

```sh
python3 -m unittest discover -s file-tools/semantic_cfg/tests
```
