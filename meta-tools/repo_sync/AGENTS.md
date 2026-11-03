# repo_sync

This tool copies explicitly selected shared files in one direction. Read
`SKILL.yaml` and the manifest before use. Always inspect a `plan` result before
`apply`; never commit, push, or delete target-only files on behalf of this tool.
Review each manifest before copying author notes or private data. Preserve the stale-plan and symlink
safety checks when changing the implementation.
