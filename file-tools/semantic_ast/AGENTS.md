# semantic_ast Tool Instructions

This tool is the parent dispatcher for semantic AST capabilities.

Local rules:

* Keep the parent dispatcher deterministic and side-effect explicit.
* Delegate concrete behavior to focused sub-tools.
* Preserve 1-based line numbers and end line numbers.
* Keep file reads explicit and limited to requested paths.
* Do not update memory or state from this tool.
* Treat root `semantic_ast.py` as the executable dispatcher entrypoint.

Current sub-tools:

* `ast_parsing`: parse Python source or files into normalized semantic AST.
* `compression`: reduce semantic AST structures into compact LLM-friendly shapes.
* `call_graph`: extract direct local call relationships from semantic AST trees.

The parent tool should expose stable orchestration operations while keeping the
sub-tools independently testable and inspectable.
