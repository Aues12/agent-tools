# Meta-tools

These tools maintain the repository's tool contracts and discovery data.
They require Python 3.11+ and PyYAML (`pip install -e '.[meta-tools]'`).

| Need | Tool |
| --- | --- |
| Check one tool's metadata, entrypoints, and examples without executing it | [contract_validator](contract_validator/README.md) |
| Compare local metadata with the tool registry, then apply a reviewed plan | [registry_sync](registry_sync/README.md) |

For a new tool, validate its package first, then run registry_sync `plan`.
Only `apply` writes; it requires the matching `plan_sha256`. Neither tool
rewrites the root README or silently removes old registry entries.
