# tool_discovery

This tool reads the repository registry and local `SKILL.yaml` metadata. Keep
its results deterministic and read-only. Do not rank tools or infer task fit.
Registry entries define membership and entrypoints; local metadata supplies
operation parameters, purpose, and side effects. Report disagreements instead
of silently choosing one source.
