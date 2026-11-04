# repo_sync

`repo_sync` compares selected files in two local checkouts and can copy changes
from the source to the target. Use it when you want a reviewed, one-way file
copy without making a Git commit. It does not merge changes or delete files
that exist only in the target.

Selection comes from a JSON manifest. The tool protects Git directories,
common build outputs, symlinks, and skill `preferences.md` files; other private
paths must be listed in the manifest's `exclude` array. Review the manifest
before copying, especially towards a public checkout.

## Start with a plan

Copy [the manifest template](examples/template.json), replace its two path
placeholders, and set `include` to the files or directories you want to share.
Set `exclude` to paths that must stay local. Relative checkout roots in the
manifest are resolved from the manifest's directory.

From the repository root, run:

```bash
python3 meta-tools/repo_sync/tool.py plan --manifest /path/to/manifest.json --include-diff
python3 meta-tools/repo_sync/tool.py apply --manifest /path/to/manifest.json --expected-plan-sha256 DIGEST
```

Read the proposed paths and diff before `apply`; replace `DIGEST` with the
`Plan SHA-256` printed by `plan`. `apply` rechecks the plan against both
checkouts before changing files. To inspect differences without a copy, use
`check` in place of `plan`. The [example request](examples/plan.json) shows
the JSON-on-stdin interface; `--json` prints the full structured result from
the terminal interface.

## Manifest and operation details

A version `0.2.0` manifest may use `"include": ["."]` for the whole checkout.
A literal directory in `exclude` also excludes its descendants. Older
manifests use the same exclusion rules. The [template](examples/template.json)
shows optional `source_root`, `target_root`, and `verify_commands`; CLI
`--source-root` and `--target-root` override the roots in the manifest. Use
an absolute manifest path when it is outside the source checkout. See the
[WordPress example](examples/wordpress_manifest.json) for a project-specific
selection.

`check` and `plan` report source-only or differing files in `changes`, and
target-only files in `target_only`. Either makes `valid` false. A text diff is
available with `--include-diff` or `include_diff: true` in a JSON request;
binary files have no text diff. Diffs may expose file contents. The plan
digest covers paths and file hashes regardless of whether a diff is requested.
In the terminal interface, `check` and `plan` exit with status 1 when the
selected files differ; `plan` still prints its digest. JSON-on-stdin `plan`
reports the difference in `result.valid` and exits successfully when the
operation itself succeeds.

`apply` can overwrite edits made independently in the target. Without a
common baseline, the tool cannot identify which side changed or infer
deletions. It stages replacements and backups before copying; if a copy fails,
it attempts to restore files already changed by that apply. This is not a
fully atomic operation: other processes can observe intermediate files, and
a crash or failed rollback can leave partial changes. Target-only files remain,
so the post-apply result can still have `valid: false`.

The optional `verify` operation runs each manifest `verify_commands` argument
list once in each checkout, without a shell. It reports output and exit codes.
These commands can change files or use the network. The JSON interface accepts
`timeout` in seconds (default 120, range 1–3600). A passing verification and
byte equality do not prove functional equivalence.
