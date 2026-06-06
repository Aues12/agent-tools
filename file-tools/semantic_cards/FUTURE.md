# Future Improvement Ideas

## LLM Annotation Layer

LLM annotation should be optional and should come after deterministic extraction.

The LLM may add:

```text
summary
doc
concept
role
semantic_cluster
importance
complexity_hint
semantic_strength
```

The LLM should not be the source of truth for facts that can be extracted deterministically.

For example:

```text
function name
argument names
line range
parent-child containment
direct local calls
```

should come from AST or static analysis.

The LLM may estimate:

```text
what the function is for
which conceptual cluster it belongs to
how central it appears
how similar it is to another card
```

When LLM annotations are added, include confidence and evidence where practical.

## Star Map Direction

The long-term vision may include star maps, constellations, force fields, clusters, and observatory-style navigation.

These should be treated as visualization layers over the semantic model.

Do not encode UI-specific layout too early into the core semantic data.

A good semantic structure should survive a change of frontend.

## Development Priorities

Recommended order:

```text
1. Keep semantic AST parser reliable.
2. Improve compression without losing important structure.
3. Add semantic_cards.py.
4. Preserve parent-child containment.
5. Add deterministic relations from call_graph.py.
6. Add optional LLM annotation.
7. Add visual layout and star-map metaphors later.
```
