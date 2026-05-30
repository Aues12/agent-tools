# Semantic AST Raw Output: `file-tools/semantic_ast/tool.py`

Source:
- `/workspace/agent-tools/file-tools/semantic_ast/tool.py`

Tool:
- `semantic_ast`
- operation: `parse_file`

## Response

- `success`: `true`
- `message`: `Parsed Python file /workspace/agent-tools/file-tools/semantic_ast/tool.py`
- `meta.operation`: `parse_file`

## Result

- `type`: `module`
- `language`: `python`
- `path`: `/workspace/agent-tools/file-tools/semantic_ast/tool.py`
- `line`: `1`
- `end_line`: `229`
- `line_count`: `229`
- `docstring`: `Dispatcher for semantic_ast sub-tools.

The parent tool keeps a single stdin JSON interface while delegating concrete
work to focused sub-tools such as ast_parsing, compression, and call_graph.`

## Stats

- `nodes`: `773`
- `functions`: `10`
- `classes`: `0`
- `imports`: `7`
- `assignments`: `38`

## Top-level items

- `import_from` `__future__`
- `import` ``
- `import` ``
- `import` ``
- `import_from` `pathlib`
- `import_from` `types`
- `import_from` `typing`
- `assignment` `[{'type': 'name', 'line': 16, 'end_line': 16, 'id': '_TOOL_DIR', 'context': 'Store'}]`
- `function` `_load_module`
- `assignment` `[{'type': 'name', 'line': 28, 'end_line': 28, 'id': '_ast_parsing', 'context': 'Store'}]`
- `assignment` `[{'type': 'name', 'line': 32, 'end_line': 32, 'id': '_compression', 'context': 'Store'}]`
- `assignment` `[{'type': 'name', 'line': 36, 'end_line': 36, 'id': '_call_graph', 'context': 'Store'}]`
- `assignment` `[{'type': 'name', 'line': 41, 'end_line': 41, 'id': 'parse_file', 'context': 'Store'}]`
- `assignment` `[{'type': 'name', 'line': 42, 'end_line': 42, 'id': 'parse_source', 'context': 'Store'}]`
- `assignment` `[{'type': 'name', 'line': 43, 'end_line': 43, 'id': 'compress_ast', 'context': 'Store'}]`
- `assignment` `[{'type': 'name', 'line': 44, 'end_line': 44, 'id': 'build_call_graph', 'context': 'Store'}]`
- `assignment` `[{'type': 'name', 'line': 47, 'end_line': 47, 'id': '_OPERATIONS', 'context': 'Store'}]`
- `function` `run`
- `function` `main`
- `function` `_parse_request`
- `function` `_normalize_operation`
- `function` `_validate_params`
- `function` `_parse_tree_from_params`
- `function` `_subtool_for`
- `function` `_error_envelope`
- `function` `_exit_code`
- `if` ``
