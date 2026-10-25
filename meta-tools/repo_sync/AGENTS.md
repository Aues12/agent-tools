# repo_sync

This tool copies explicitly selected shared files in one direction. Read
`SKILL.yaml` and the manifest before use. Always inspect a `plan` result before
`apply`; never commit, push, delete target-only files, or traverse personal
data directories on behalf of this tool. Preserve the stale-plan and symlink
safety checks when changing the implementation.
