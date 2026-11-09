# repo_sync

This tool copies explicitly selected shared files in one direction. Read
`SKILL.yaml` and the manifest before use. Always inspect a `plan` result before
`apply`; never commit, push, or delete target-only files on behalf of this tool.
Review each manifest for private data. Preserve the stale-plan and symlink
safety checks when changing the implementation.

## JSON-on-stdin workflow

From the repository root, replace the example paths and request a plan:

```bash
python3 meta-tools/repo_sync/tool.py <<'JSON'
{"operation":"plan","params":{"source_root":"/path/to/source","target_root":"/path/to/target","manifest_path":"/path/to/manifest.json","include_diff":true}}
JSON
```

Inspect `success`, `result.changes`, `result.target_only`, and the diffs. After
review, use the same paths and the returned `result.plan_sha256`:

```bash
python3 meta-tools/repo_sync/tool.py <<'JSON'
{"operation":"apply","params":{"source_root":"/path/to/source","target_root":"/path/to/target","manifest_path":"/path/to/manifest.json","expected_plan_sha256":"DIGEST"}}
JSON
```

For read-only comparison use `check` with the plan parameters. `verify` runs
manifest commands and can have side effects. See [README.md](README.md) for
manifest selection, operation limits, and rollback behavior.

For implementation changes, run the local tests and
`pyright --pythonversion 3.11 meta-tools/repo_sync/tool.py` from the repository
root. Output types are declared in `tool.py`; preserve their JSON field names
and keep runtime validation for external inputs.
