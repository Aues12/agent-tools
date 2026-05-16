# rename_files Tool Instructions

This tool provides deterministic file-renaming primitives within a single
directory boundary.

Local rules:

* Keep rename scope inside the provided directory.
* Validate targets before mutating any file names.
* Report conflicts instead of silently overwriting files.
* Prefer dry runs before applying renames in agent workflows.
* Do not update registry, memory, or state from this tool.
