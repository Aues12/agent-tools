# Compressed Semantic AST Output: `runtime/executor.py`

Source:
- `runtime/executor.py`

Applied on:
- previously generated `executor_semantic_ast_raw.json` (removed)

Compression result:
- `type`: `module`
- `name`: `n/a`
- `args`: `None`
- `calls`: `None`

Representative compressed node:
- `execute_tool`
  - `type`: `function`
  - `args`: `["step"]`
  - `calls`: `["TypeError", "ValueError", "_entrypoint_path", "_parse_response", "_resolve_tool", "completed.stderr.decode", "encode", "isinstance", "json.dumps", "response.get", "response.setdefault", "step.get", "str", "subprocess.run", "tool_entry.get", "update"]`
  - `returns`: compressed recursively into a compact type/value form

Notes:
- The compressor keeps high-signal fields and removes verbose AST detail.
- Names are collapsed to plain strings when possible.
- Nested expression trees are recursively compressed to keep the output LLM-friendly.
