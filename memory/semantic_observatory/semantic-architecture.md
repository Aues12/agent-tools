# Semantic Architecture

Semantic Architecture describes how semantic meaning becomes software structure.

It connects archetypes, roles, phases, cards, blueprints, and source code into a unified architecture-first model.

```txt
Archetypes
    ↓
Roles and Phases
    ↓
Semantic Cards
    ↓
Blueprints
    ↓
Source Code
    ↓
Observatory
```

The central idea is that source code is not the first layer of software architecture.

Source code is a manifestation of deeper semantic organization.

---

# Part I — Semantic Foundations

## Archetypes and Semantic Cards

Not all cards exist at the same semantic level.

Some cards derive meaning from a specific implementation context.

Others possess meaning independently of any repository, module, function, or source file.

This introduces two complementary categories.

### Archetype Cards

Archetype cards represent general semantic patterns.

Examples:

```txt
Builder
Validator
Observer
Adapter
Explorer

Observation
Understanding
Manifestation
Transformation
```

These cards function as stable semantic anchors.

They may appear across many systems and implementations.

An archetype card is not merely a reusable code template.

It is a general semantic form that may later be specialized into concrete cards.

### Context Cards

Context cards represent specific manifestations of archetypal patterns.

Examples:

```txt
build_call_graph
parse_source
compress_ast
resolve_name
```

Their meaning emerges through context and relationships.

---

## General and Particular

Semantic cards exist between the general and the particular.

Example:

```txt
Builder
    ↓
Call Graph Builder
    ↓
build_call_graph
```

or

```txt
Observation
    ↓
AST Observation
    ↓
parse_source
```

A card is neither pure abstraction nor pure implementation.

A card is a semantic scene connecting both.

---

## Role and Phase Architecture

Role and Phase classifications are not merely metadata.

They represent semantic organizing principles.

Examples:

```txt
Role
    Builder
    Validator
    Observer
    Explorer
```

```txt
Phase
    Observation
    Understanding
    Manifestation
    Transformation
```

Concrete cards may specialize these archetypal forms.

Role and Phase therefore become:

* Navigation structures
* Indexing structures
* Blueprint structures
* Architecture structures

rather than simple tags.

---

## Semantic Architecture Layers

Software may be viewed as a layered semantic structure.

```txt
Archetypes
        ↓
Roles and Phases
        ↓
Semantic Cards
        ↓
Blueprints
        ↓
Source Code
```

Source code becomes a manifestation of higher semantic structures.

---

# Part II — Card-Driven Development

## Observation and Construction

Semantic cards support two complementary workflows.

### Observation

```txt
Source Code
    ↓
AST
    ↓
Cards
    ↓
Observatory
```

Understanding existing systems.

### Construction

```txt
Blueprint
    ↓
Cards
    ↓
Source Synthesis
    ↓
Source Code
```

Constructing new systems.

Card ordering is not a UI problem.

Card ordering becomes architecture itself.

---

## Function and Module Relationship

A key architectural principle:

```txt
Function = Card
Module ≠ Card
```

A function may be represented by a single card.

A module is typically a collection of related cards.

Example:

```txt
call_graph.py

├── normalize_call
├── resolve_name
├── collect_edges
└── build_call_graph
```

The final source file is synthesized from multiple cards.

---

## Template Cards

Cards may also represent reusable architectural patterns.

Examples:

```txt
Parser Function
Validator
Repository
CLI Command
React Component
API Route
Test Case
```

Template cards reduce boilerplate and provide reusable semantic structures.

---

## Context Management

Instead of supplying complete source files:

```txt
Template
+
Parameters
+
Custom Logic
```

may be sufficient.

This reduces:

* Context size
* Token usage
* Repeated boilerplate generation

while preserving architectural consistency.

---

## Semantic Index

Traditional navigation:

```txt
Repository
    ↓
Folders
    ↓
Files
```

Semantic navigation:

```txt
Roles
    ↓
Phases
    ↓
Cards
    ↓
Source
```

This creates a semantic layer above the physical repository structure.

---

## Source Synthesis Pipeline

```txt
Semantic Blueprint
    ↓
Cards
    ↓
Group by Module
    ↓
Resolve Dependencies
    ↓
Generate Source Files
    ↓
ruff check
    ↓
ruff format
    ↓
pyright
    ↓
pytest
```

The synthesized source becomes the implementation of the semantic architecture.

---

## Repository Strategy

Raw AST should not be considered a permanent artifact.

Recommended hierarchy:

```txt
Raw AST
    ↓
Compressed AST
    ↓
Semantic Cards
    ↓
Observatory
```

Raw AST may be treated as cache.

Possible operations:

```txt
generate-cache
clear-cache
prune-cache
rebuild-cache
```

---

## Product Direction

Free Tier:

```txt
Repository Inspection
AST Analysis
Semantic Cards
Observatory Navigation
Code Indexing
```

Premium Tier:

```txt
Architecture Builder
Template Cards
Blueprint Editing
Source Synthesis
Validation Pipeline
Refactoring Assistance
```

---

# Long-Term Vision

```txt
Archetypes
    ↓
Roles and Phases
    ↓
Cards
    ↓
Blueprints
    ↓
Source Code
    ↓
Observatory
```

In this model:

* Cards become semantic building blocks.
* Blueprints become architectural descriptions.
* Source code becomes implementation.
* The Observatory becomes both an observation system and an architecture construction environment.
* Software architecture becomes a process of semantic specialization.

```

