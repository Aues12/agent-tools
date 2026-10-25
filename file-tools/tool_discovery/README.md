# tool_discovery

Read-only discovery over `registry/tool_registry.json` and registered tools'
`SKILL.yaml` files. Results retain registry order; no relevance ranking or
task-to-tool recommendation is performed. Registry entries define the catalog
and access surfaces. Local metadata supplies purpose, parameter contracts, and
side effects. Disagreements appear in `issues`.

Requires PyYAML (declared in the project dependencies). Run from any working
directory:

```bash
printf '%s' '{"operation":"list_tools","params":{}}' | python3 file-tools/tool_discovery/tool_discovery.py
```

## Operations

- `list_tools`: no parameters; returns all registered tool summaries.
- `search_tools`: `query` or exact `capability` (at least one required). The
  search ignores common connector words, punctuation, case, and simple plural
  endings. It compares the remaining words with each tool's name, capability,
  purpose, operations, and optional local `search_terms`. Every tool in the
  chosen capability appears, including zero-match tools. Results include
  `matched_terms` and `match_ratio` (matched query words / all meaningful query
  words), sorted by that ratio. Ties keep registry order. With only a capability
  filter, `match_ratio` is null and registry order is retained. This is lexical
  coverage, not a judgment that a tool is suitable for the task.
- `inspect_tool`: required exact `name`; returns interfaces, entrypoint,
  operation parameters, side effects, and metadata issues.

Requests and responses use the standard `operation`/`params` JSON envelope.
The Python API accepts an optional `root` path for testing or inspecting
another checkout; the stdin interface always uses this repository.

```bash
printf '%s' '{"operation":"search_tools","params":{"query":"call graph"}}' | python3 file-tools/tool_discovery/tool_discovery.py
printf '%s' '{"operation":"search_tools","params":{"query":"Extract functions and their call relationships from Python code"}}' | python3 file-tools/tool_discovery/tool_discovery.py
printf '%s' '{"operation":"inspect_tool","params":{"name":"call_graph"}}' | python3 file-tools/tool_discovery/tool_discovery.py
```

Run tests with `python3 -m unittest discover -s file-tools/tool_discovery/tests`.
