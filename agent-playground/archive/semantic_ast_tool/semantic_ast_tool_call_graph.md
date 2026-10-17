# Call Graph Output: `file-tools/semantic_ast/tool.py`

Source:
- `file-tools/semantic_ast/tool.py`

Generated with:
- `semantic_ast.parse_file`
- `call_graph.build_call_graph`

## Flow Tree

```text
_load_module
main
├── _error_envelope
├── _exit_code
└── run
    ├── _error_envelope
    ├── _normalize_operation
    ├── _parse_request
    │   ├── _normalize_operation
    │   └── _validate_params
    ├── _parse_tree_from_params
    └── _subtool_for
```

## Summary

- Functions: `10`
- Local call edges: `10`
- Roots: `_load_module, main`
- Leaves: `_error_envelope, _exit_code, _load_module, _normalize_operation, _parse_tree_from_params, _subtool_for, _validate_params`

## Local Edges

| Caller | Callee | Call |
| --- | --- | --- |
| `_parse_request` | `_normalize_operation` | `_normalize_operation` |
| `_parse_request` | `_validate_params` | `_validate_params` |
| `main` | `_error_envelope` | `_error_envelope` |
| `main` | `_exit_code` | `_exit_code` |
| `main` | `run` | `run` |
| `run` | `_error_envelope` | `_error_envelope` |
| `run` | `_normalize_operation` | `_normalize_operation` |
| `run` | `_parse_request` | `_parse_request` |
| `run` | `_parse_tree_from_params` | `_parse_tree_from_params` |
| `run` | `_subtool_for` | `_subtool_for` |

## External Calls

- `_load_module`: `ImportError, importlib.util.module_from_spec, importlib.util.spec_from_file_location, spec.loader.exec_module`
- `run`: `ValueError, bool, build_call_graph, compress_ast, len, params.get, parse_file, parse_source`
- `main`: `ValueError, json.dumps, json.loads, print, strip, sys.exit, sys.stdin.read`
- `_parse_request`: `TypeError, ValueError, input_data.get, input_data.items, isinstance`
- `_normalize_operation`: `operation.rsplit`
- `_validate_params`: `ValueError`
- `_parse_tree_from_params`: `bool, params.get, parse_file, parse_source`
- `_subtool_for`: `None`
- `_error_envelope`: `str`
- `_exit_code`: `error.get, response.get`

Full JSON:
- `agent-playground/archive/semantic_ast_tool/semantic_ast_tool_call_graph.json`
