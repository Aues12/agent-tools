# AGENTS.md

## semantic_architecture

### Purpose

`semantic_architecture` is the architecture construction layer of Semantic Observatory.

Its responsibility is to transform semantic structures into executable software structures.

It operates above source code and below semantic architecture.

```txt
Archetypes
    ↓
Roles and Phases
    ↓
Semantic Cards
    ↓
Blueprints
    ↓
semantic_architecture
    ↓
Source Code
```

---

## Scope

This tool does not parse source code.

This tool does not generate semantic cards.

Those responsibilities belong to:

```txt
semantic_ast
    ↓
semantic_cards
```

Instead, this tool consumes semantic cards and blueprints.

Its responsibility is synthesis.

---

## Core Principle

Source code is an implementation artifact.

Semantic architecture is the source of truth.

The primary goal is to preserve semantic intent while generating executable structures.

---

## Responsibilities

### Module Synthesis

Transform card collections into source modules.

Example:

```txt
Cards
    ↓
Group by Module
    ↓
Generate Module
```

Multiple cards may belong to the same module.

A module is a synthesis target.

A card is a semantic unit.

```txt
Function = Card
Module ≠ Card
```

---

### Blueprint Construction

Support architecture-first development.

```txt
Blueprint
    ↓
Cards
    ↓
Source Code
```

Blueprints describe architecture.

Source code implements architecture.

---

### Dependency Resolution

Cards may depend on other cards.

The synthesis pipeline must:

* Resolve dependencies
* Order cards
* Generate valid module structures

Card ordering is architecture.

---

### Source Mapping

Generated code must remain traceable.

Produce source maps linking:

```txt
Generated Source
        ↓
Semantic Card
```

Example:

```json
{
  "card_id": "call_graph.build_call_graph",
  "start_line": 31,
  "end_line": 74
}
```

Source maps enable diagnostics and navigation.

---

### Module Metadata

Deferred.

Module-level semantic profiling is outside the scope of v0.1.

Examples:

- dominant role
- dominant phase
- architectural intent
- semantic summaries

These concepts require higher-level semantic inference and should not be implemented until deterministic foundations are stable.

---

## Initial Version (v0.1)

Focus only on:

```txt
Cards
    ↓
Module Synthesis
    ↓
Source Maps
```

Do not implement:

* diagnostics
* refactoring
* architecture editing
* LLM orchestration

until module synthesis is stable.

---

## Future Version (v0.2)

Add:

```txt
Source Maps
    ↓
Diagnostics
```

Potential tools:

```txt
ruff
pyright
pytest
```

Diagnostics should be mapped back to cards.

Example:

```txt
line 42
    ↓
build_call_graph
    ↓
card diagnostics
```

The user should reason about cards rather than line numbers.

---

## Future Version (v0.3)

Support:

```txt
Blueprint Editing
    ↓
Architecture Updates
    ↓
Source Regeneration
```

This enables architecture-first software development.

---

## Architectural Layers

```txt
Archetypes
        ↓
Roles and Phases
        ↓
Semantic Cards
        ↓
Blueprints
        ↓
semantic_architecture
        ↓
Source Code
```

The tool operates only between blueprints and source code.

---

## Design Constraints

### Deterministic

The same input must produce the same output.

### Auditable

Generated code must remain traceable to cards.

### Reversible

Users should be able to navigate:

```txt
Source
    ↓
Card
```

and

```txt
Card
    ↓
Source
```

without losing context.

### Semantic First

Semantic intent is more important than source layout.

Module structure should emerge from architecture rather than filesystem conventions.

---

## Long-Term Vision

Semantic Observatory should eventually support:

### Observation

```txt
Source Code
    ↓
Semantic Cards
    ↓
Observatory
```

### Construction

```txt
Blueprint
    ↓
Semantic Cards
    ↓
semantic_architecture
    ↓
Source Code
```

In this model, software development becomes a process of semantic specialization.

Architecture precedes implementation.
