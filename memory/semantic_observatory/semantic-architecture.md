# Semantic Observatory — Card-Driven Architecture Notes

## Observation

A semantic card system can be used not only for observing existing code, but also for constructing new software architectures.

This introduces a second development direction:

```txt
Source Code
    ↓
AST
    ↓
Semantic Cards
    ↓
Observatory
```

and

```txt
Semantic Architecture
    ↓
Semantic Cards
    ↓
Source Synthesis
    ↓
Source Code
```

The second direction enables architecture-first development.

---

## Card-Driven Development

Instead of starting from source files, development begins with semantic units.

A card becomes the smallest architectural building block.

Cards may represent:

* Functions
* Classes
* Data Types
* Modules
* Tests
* Interfaces

Cards are semantic entities before they become source code.

---

## Function ≠ Module

A key design decision:

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

Each function can be represented by its own semantic card.

The final source file is synthesized from multiple cards.

---

## Semantic Blueprint Layer

A new architectural layer may exist above source code.

```txt
Semantic Blueprint
        ↓
Semantic Cards
        ↓
Source Synthesis
        ↓
Python Source Files
```

The blueprint represents intent and architecture.

Source code becomes an implementation artifact generated from that blueprint.

---

## Card Structure

Possible fields:

```json
{
  "id": "call_graph.build_call_graph",
  "kind": "function",
  "module": "semantic_ast/call_graph.py",
  "order": 30,
  "summary": "...",
  "dependencies": [],
  "source": "..."
}
```

The module field specifies where synthesized code should be placed.

Multiple cards may target the same module.

---

## Source Synthesis

Generation flow:

```txt
Cards
    ↓
Group by Module
    ↓
Resolve Dependencies
    ↓
Sort Cards
    ↓
Generate Source Files
```

Cards remain independent.

Source files are assembled from card collections.

---

## Quality Pipeline

Generated code should pass automated validation.

Suggested pipeline:

```txt
Semantic Blueprint
    ↓
Cards
    ↓
Source Synthesis
    ↓
ruff check
    ↓
ruff format
    ↓
pyright
    ↓
pytest
```

The final generated source files are validated, not individual cards.

---

## Large Repository Strategy

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

## Long-Term Vision

Semantic Observatory may eventually support two complementary workflows:

### Observation

```txt
Source Code
    ↓
Semantic Observatory
```

Understanding existing systems.

### Construction

```txt
Semantic Blueprint
    ↓
Semantic Observatory
    ↓
Source Code
```

Designing new systems through semantic architecture.

In this model, card ordering is not a UI problem.

Card ordering becomes architecture itself.

## Template Cards and Architectural Reuse

A semantic card is not limited to representing existing source code.

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

These patterns may be expressed as template cards.

---

## Template Card Model

A template card describes a reusable semantic structure.

Example:

```json
{
  "template": "parser_function",
  "name": "parse_source",
  "inputs": ["source"],
  "outputs": ["semantic_node"],
  "custom_logic": "..."
}
```

The implementation is generated from the template definition and card parameters.

---

## Benefits

### Reduced Boilerplate

Common structures do not need to be rewritten repeatedly.

The developer modifies intent and implementation details rather than recreating standard architecture.

---

### Improved Context Management

Instead of providing complete source files to an LLM, the system may provide:

```txt
Template
+
Parameters
+
Custom Logic
```

This significantly reduces context requirements.

---

### Reduced Token Usage

Semantic cards become compact representations of larger implementation patterns.

The model reasons about architecture rather than repeatedly generating identical source structures.

---

## Observatory as an Indexing System

Semantic Observatory serves two complementary roles:

### Observation

```txt
Source Code
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
```

Designing new systems.

---

## Semantic Index

Cards may function as a semantic index of a software system.

Instead of navigating primarily through files and directories:

```txt
Repository
    ↓
Folders
    ↓
Files
```

Users navigate through:

```txt
Roles
    ↓
Phases
    ↓
Cards
    ↓
Source
```

This creates a semantic navigation layer above the physical repository structure.

---

## Role and Phase Architecture

Role and Phase classifications become architectural metadata.

Examples:

```txt
Role
    Builder
    Validator
    Adapter
    Explorer
```

```txt
Phase
    Observation
    Understanding
    Manifestation
    Transformation
```

These classifications may be used for:

* Navigation
* Filtering
* Search
* Architecture generation
* Blueprint construction

Role and Phase are not visual tags only.

They become part of the semantic architecture model itself.

---

## Possible Product Direction

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

This creates a natural distinction between understanding software and constructing software.

---

# Semantic Architecture

## Archetypes and Semantic Cards

Not all cards exist at the same semantic level.

Some cards derive meaning from a specific implementation context.

Others possess meaning independently of any repository, module, or source code.

This introduces two complementary categories:

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

---

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

It is a semantic scene that connects both.

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

## Relationship to Role and Phase

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

Example:

```txt
Builder
    ↓
Call Graph Builder
    ↓
build_call_graph
```

Role and Phase therefore become:

* Navigation structures
* Indexing structures
* Blueprint structures
* Architecture structures

rather than simple tags.

---

## Card-Driven Architecture

Semantic cards are not limited to code inspection.

They may also function as architectural building blocks.

Two complementary workflows emerge:

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

Template cards improve context efficiency.

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

Cards may function as a semantic index of a software system.

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

Possible generation flow:

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

## Long-Term Vision

Semantic Observatory and Semantic Architecture may ultimately form a unified system.

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
