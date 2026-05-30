# Semantic AST Raw Output: `runtime/executor.py`

Source:
- `/workspace/agent-tools/runtime/executor.py`

Tool:
- `semantic_ast`
- operation: `parse_file`

## Response

- `success`: `true`
- `message`: `Parsed Python file /workspace/agent-tools/runtime/executor.py`
- `meta.operation`: `parse_file`

## Result

- `type`: `module`
- `language`: `python`
- `path`: `/workspace/agent-tools/runtime/executor.py`
- `line`: `1`
- `end_line`: `117`
- `line_count`: `117`
- `docstring`: `Tool execution through registry-backed stdin/stdout JSON transport.`

## Stats

- `nodes`: `453`
- `functions`: `4`
- `classes`: `0`
- `imports`: `7`
- `assignments`: `15`

## Top-level items

- `import_from` `__future__` -> `annotations`
- `import` `json`
- `import` `subprocess`
- `import` `sys`
- `import_from` `pathlib` -> `Path`
- `import_from` `typing` -> `Any`
- `import_from` `registry.loader` -> `load_registry`
- `assignment` `REPO_ROOT`
- `function` `execute_tool`
- `function` `_resolve_tool`
- `function` `_entrypoint_path`
- `function` `_parse_response`

## Function list

- `execute_tool(step: dict[str, Any]) -> dict[str, Any]`
- `_resolve_tool(name: Any) -> dict[str, Any]`
- `_entrypoint_path(tool_entry: dict[str, Any]) -> Path`
- `_parse_response(stdout: bytes) -> dict[str, Any]`

## Notes

- This file contains only the parsed structure summary.
- No additional interpretation or review comments are included.
