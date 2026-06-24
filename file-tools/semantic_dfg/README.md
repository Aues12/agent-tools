# semantic_dfg

`semantic_dfg` builds deterministic local data-flow graphs from Python semantic
AST trees.

It answers:

```text
Which value depends on which previous value?
Which operation produced this value?
Where does a value enter, transform, and leave a local function scope?
```

The first version intentionally avoids symbolic phase inference, type inference,
runtime tracing, SSA, and interprocedural analysis.

## Pipeline

```text
Python source
  -> semantic_ast
  -> semantic_dfg
  -> semantic_cards
  -> semantic_view
```

`semantic_dfg` consumes the normalized dictionaries produced by
`semantic_ast`. Convenience operations can parse source or files first.

## Operations

### build_dfg

Build a DFG from an existing semantic AST module tree.

```json
{
  "operation": "build_dfg",
  "params": {
    "tree": {
      "type": "module",
      "language": "python",
      "body": []
    }
  }
}
```

### build_dfg_from_source

Parse source through `semantic_ast`, then build a DFG.

```json
{
  "operation": "build_dfg_from_source",
  "params": {
    "source": "def main(path):\n    text = read_file(path)\n    return text\n",
    "path": "example.py"
  }
}
```

### build_dfg_from_file

Read a Python file through `semantic_ast`, then build a DFG.

### summarize_dfg

Convert a DFG result into compact human-readable summaries.

## Example

Input:

```python
def parse_file(path):
    text = read_file(path)
    tree = ast.parse(text)
    return tree
```

DFG summary:

```text
path -> text via read_file
text -> tree via ast.parse
tree -> return_value via return
```

The generated nodes also include `flow_level`, a DFG-specific value-flow
distance:

```text
path          flow_level 0
text          flow_level 1
tree          flow_level 2
return_value  flow_level 3
```

`flow_level` should not be confused with semantic card `level`, which describes
architectural height from relation analysis.

Nodes also include `depth`, a local structural nesting value:

```text
function parameters  depth 0
top-level body nodes depth 1
nested block nodes   depth 2+
```

## Validation

```sh
python3 -m unittest discover -s file-tools/semantic_dfg/tests
```
