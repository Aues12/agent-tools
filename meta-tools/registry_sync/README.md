# registry_sync

Uses each local tool's `SKILL.yaml` as the source for discoverable fields in
`registry/tool_registry.json`. `check` and `plan` are read-only. `apply`
requires the digest from a matching plan. Existing registry-only tools are
reported as `unrepresented`, never deleted. Unknown fields on existing
entries are preserved. The `check` CLI exits nonzero when drift remains.

From the repository root, run `python3 meta-tools/registry_sync/tool.py`
with the JSON in `examples/plan.json` on stdin. Requires
`pip install -e '.[meta-tools]'`.
