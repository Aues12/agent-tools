# semantic_ast Tool Instructions

This tool parses Python source into a compact semantic AST representation.

Local rules:

* Keep parsing deterministic and side-effect free.
* Preserve 1-based line numbers and end line numbers.
* Prefer compact semantic summaries over raw `ast.dump()` output.
* Keep file reads explicit and limited to the requested path.
* Do not update registry, memory, or state from this tool.
* Treat `semantic_ast.py` as the executable entrypoint and `tool.py` as the core implementation.

The primary use cases are:

* code navigation
* symbol discovery
* semantic chunking
* AST-assisted refactoring
* LLM-friendly code analysis
