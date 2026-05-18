# ast_parsing Tool Instructions

This sub-tool parses Python source into the normalized semantic AST used by the
parent `semantic_ast` tool.

Local rules:

* Keep parsing deterministic and side-effect free.
* Preserve 1-based line numbers and inclusive end line numbers.
* Prefer compact semantic summaries over raw `ast.dump()` output.
* Keep file reads explicit and limited to the requested path.
* Do not update registry, memory, or state from this sub-tool.
* Treat `ast_parser.py` as both the executable entrypoint and core implementation.

The primary use cases are:

* code navigation
* symbol discovery
* semantic chunking
* AST-assisted refactoring
* LLM-friendly code analysis
