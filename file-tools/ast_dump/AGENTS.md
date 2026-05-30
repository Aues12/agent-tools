# ast_dump Tool Instructions

This tool exposes deterministic Python `ast.dump()` output for source text or
files.

Local rules:

* Preserve Python AST fidelity; do not normalize into custom semantic nodes.
* Keep interfaces narrow and explicit.
* Validate input before parsing.
* Do not mutate project files.
