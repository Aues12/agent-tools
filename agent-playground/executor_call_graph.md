# Call Graph Output: `runtime/executor.py`

Source:
- `/workspace/agent-tools/runtime/executor.py`

Generated with:
- `semantic_ast.parse_file`
- `call_graph.build_call_graph`

## Flow Tree

```text
execute_tool
├── _entrypoint_path
├── _parse_response
└── _resolve_tool
```

## Summary

- Functions: `4`
- Local call edges: `3`
- Roots: `execute_tool`
- Leaves: `_entrypoint_path`, `_parse_response`, `_resolve_tool`

## Local Edges

| Caller | Callee | Call |
| --- | --- | --- |
| `execute_tool` | `_entrypoint_path` | `_entrypoint_path` |
| `execute_tool` | `_parse_response` | `_parse_response` |
| `execute_tool` | `_resolve_tool` | `_resolve_tool` |

## External Calls

- `execute_tool`: `TypeError`, `ValueError`, `completed.stderr.decode`, `encode`, `isinstance`, `json.dumps`, `response.get`, `response.setdefault`, `step.get`, `str`, `subprocess.run`, `tool_entry.get`, `update`
- `_resolve_tool`: `ValueError`, `isinstance`, `load_registry`, `registry.get`, `tool.get`
- `_entrypoint_path`: `FileNotFoundError`, `ValueError`, `isinstance`, `resolve`, `resolved.exists`, `resolved.relative_to`, `tool_entry.get`
- `_parse_response`: `TypeError`, `isinstance`, `json.loads`, `stdout.decode`

Full JSON:
- `agent-playground/executor_call_graph.json`
