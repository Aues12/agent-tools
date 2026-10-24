# docx_assemble

This is a write tool. Run a dry-run with the intended destination first, then
use the returned preview SHA-256 with the same plan and options when writing.
Never overwrite the source or an existing destination. Preserve
all article body text, report unsupported structure, and require a rendered
visual review of the resulting DOCX. Read the parent `AGENTS.md` and local
`SKILL.yaml` before use.
