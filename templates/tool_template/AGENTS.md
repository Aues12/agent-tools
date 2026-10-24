# Tool Template Instructions

Use this directory as the starting point for a new deterministic tool.

Before marking a tool ready:

* replace placeholder metadata in `SKILL.yaml`.
* expose a narrow interface in `tool.py`.
* document all file writes and side effects.
* add tests for normal, invalid, and boundary behavior.
* add at least one example.
* run `contract_validator`, then use `registry_sync` to review and apply its registry entry.
