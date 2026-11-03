# repo_sync

Copy shared files from one local checkout to another without copying private
data. This is a one-way file tool, not a Git merge or a publisher. It never
deletes target-only files and never commits or pushes. The caller chooses
`source_root` and `target_root`; the included paths come from a JSON manifest.

`examples/shared_code_manifest.json` selects the current shared code and
documentation in `agent-tools`. It deliberately omits the root `AGENTS.md`,
`README.md`, `.gitignore`, `memory/`, `state/`, and `study-packs/`, which can have
workspace-specific content. It also excludes the dev-only executor registry.
With version 0.1.0 manifests, `repo_sync` refuses to traverse those three
personal-data directories. All manifest versions protect Git directories, build
outputs, symlinks, and local skill `preferences.md` files.

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

## General project manifests (version 0.2.0)

A v0.2.0 manifest can select the whole checkout with `"include": ["."]`.
List project-specific private paths in `exclude`; a literal directory excludes
its descendants. Existing v0.1.0 manifests retain their original private-path
rules. Version 0.2.0 treats `memory`, `state`, and `study-packs` as ordinary
shared paths unless excluded. Always review exclusions before copying towards a
public checkout; matching paths and unknown secrets are not automatically found.

`check` reports differing or source-only paths in `changes`, and destination-only
paths in `target_only`. In v0.2.0 either makes `valid` false. `include_diff: true`
adds a target-to-source unified diff for UTF-8 files (binary files return null).
A diff can expose file contents and may be large. The plan digest covers file
hashes and paths, independently of whether the optional diff is requested.

`apply` still copies only source files, never removes destination-only files,
and can overwrite independent edits. Review both versions and resolve conflicts
before applying: without a common baseline the tool cannot identify which side
changed or infer deletions. The post-apply result remains invalid if target-only
shared files exist. Byte equality is not proof of functional equivalence.

The optional `verify` operation explicitly runs each `verify_commands` argument
list once in each checkout, without a shell, and reports output and exit codes.
Commands are trusted project code and can modify files or use the network; review
and run them only when appropriate. Pass an optional timeout in seconds. A passing
verification does not prove that all behavior is identical.

See `examples/wordpress_manifest.json` for a starting point; review its private
paths and whether the same test command is applicable to both checkouts. Both
checkouts may have different dependencies or test suites. Use an absolute
manifest path when it is outside the source checkout.
