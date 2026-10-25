# repo_sync

Copy shared files from one local checkout to another without copying private
data. This is a one-way file tool, not a Git merge or a publisher. It never
deletes target-only files and never commits or pushes. The caller chooses
`source_root` and `target_root`; the included paths come from a JSON manifest.

`examples/shared_code_manifest.json` selects the current shared code and
documentation in `agent-tools`. It deliberately omits the root `AGENTS.md`,
`README.md`, `.gitignore`, `memory/`, `state/`, and `study-packs/`, which can have
workspace-specific content. It also excludes the dev-only executor registry.
`repo_sync` refuses to traverse those three personal-data directories, Git
directories, build outputs, symlinks, and local
skill `preferences.md` files even if a manifest includes them.

Run `plan`, review each proposed path, then pass the returned `plan_sha256` to
`apply`. Both source and target state are rechecked during apply. A stale plan
fails before mutation; a change during copying stops the operation. The tool
does not claim to detect every secret inside allowed files, so review the diff
before publishing a public repository.

```bash
python3 meta-tools/repo_sync/tool.py <<'JSON'
{"operation":"plan","params":{"source_root":"/path/to/agent-tools","target_root":"/path/to/agent-tools-dev","manifest_path":"meta-tools/repo_sync/examples/shared_code_manifest.json"}}
JSON
```

For `apply`, use the same parameters plus `"expected_plan_sha256":"..."`.
Reverse the roots only after reviewing the manifest for that direction. The
tool does not infer which repository is public.
