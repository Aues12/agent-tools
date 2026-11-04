# Meta-tools

These tools maintain the repository's tool contracts and discovery data.
They require Python 3.11+ and PyYAML (`pip install -e '.[meta-tools]'`).

| Need | Tool |
| --- | --- |
| Check one tool's metadata, entrypoints, and examples without executing it | [contract_validator](contract_validator/README.md) |
| Compare local metadata with the tool registry, then apply a reviewed plan | [registry_sync](registry_sync/README.md) |
| Compare selected files in two checkouts and copy reviewed changes | [repo_sync](repo_sync/README.md) |

For a new tool, validate its package first, then run `registry_sync plan`.
Its `apply` operation requires the matching `plan_sha256`. The validator and
registry sync do not rewrite the root README or silently remove old registry
entries. See each tool's local README for its own side effects.
