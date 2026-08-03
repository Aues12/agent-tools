# [EPR] Epistemic Phases and Roles

## Index

[EPR-001] Introduction

[EPR-002] Roles and Phases

[EPR-003] The Four Epistemic Phases

[EPR-004] Elemental Correspondence

[EPR-005] Technical Roles

[EPR-006] Semantic Cards

[EPR-007] Principles

[EPR-008] Fractal Phase Dynamics

[EPR-009] Semantic Rings and Semantic Seals

[EPR-010] Elements, Modalities, and Archetypal Operations

[EPR-011] Archetypal Operations in Code

[EPR-012] Ring Visibility and Partial Arcs

[EPR-013] Semantic CPG and the Projection Layer

[EPR-014] Geometric Cohesion and Edge Integrity

---

# [EPR-001] Introduction

Knowledge work is not a single activity.

Understanding emerges through multiple kinds of movement.

A programmer, researcher, analyst, or explorer may perform many different technical tasks, yet these tasks often belong to a smaller set of epistemic movements.

This document distinguishes between:

* Roles
* Phases

Roles describe what a component does.

Phases describe where that component participates within the process of knowledge.

---

# [EPR-002] Roles and Phases

Role and Phase are different.

Role answers:

"What does this component do?"

Phase answers:

"Where does this component belong within the process of knowledge?"

Examples:

Role:

* Parser
* Builder
* Validator
* Renderer

Phase:

* Discovery
* Understanding
* Transformation
* Manifestation

Many roles may belong to the same phase.

A phase is therefore more general than a role.

---

# [EPR-003] The Four Epistemic Phases

The current model uses four primary phases.

## Discovery

The phase of observation and exploration.

Questions:

* What exists?
* What should be examined?
* Where should attention move?

Activities:

* Searching
* Exploring
* Scanning
* Locating

---

## Understanding

The phase of interpretation.

Questions:

* What does this mean?
* How do these things relate?

Activities:

* Parsing
* Analysis
* Classification
* Validation

---

## Transformation

The phase of reorganization.

Questions:

* How can this be changed?
* How can this be compressed, translated, or mapped?

Activities:

* Transformation
* Aggregation
* Compression
* Refactoring

---

## Manifestation

The phase of realization.

Questions:

* How should this become visible?
* How should it be built or expressed?

Activities:

* Building
* Rendering
* Executing
* Publishing

---

# [EPR-004] Elemental Correspondence

The phases may be represented through a symbolic layer.

These symbols do not replace technical descriptions.

They exist to aid navigation and memory.

## Discovery — Air

Symbol:

🜁

Characteristics:

* Visibility
* Perspective
* Exploration
* Orientation

Air represents the opening of the field of observation.

---

## Understanding — Water

Symbol:

▽

Characteristics:

* Reflection
* Reception
* Interpretation
* Internalization

Water represents the descent into meaning.

---

## Transformation — Fire

Symbol:

△

Characteristics:

* Change
* Refinement
* Reorganization
* Emergence

Fire represents transformation through activity.

---

## Manifestation — Earth

Symbol:

🜃

Characteristics:

* Stability
* Construction
* Materialization
* Preservation

Earth represents the realization of form.

---

# [EPR-005] Technical Roles

Roles are domain-specific.

Examples:

Discovery

* Explorer
* Locator
* Scanner
* Observer

Understanding

* Parser
* Analyzer
* Validator
* Classifier

Transformation

* Transformer
* Aggregator
* Compressor
* Refactorer

Manifestation

* Builder
* Renderer
* Executor
* Publisher

The same role may appear in multiple domains.

The phase remains stable while the role may change.

---

# [EPR-006] Semantic Cards

A Semantic Card may contain both a Role and a Phase.

Example:

Type:
Function

Role:
Builder

Phase:
Manifestation

Symbol:
🜃

Depth:
2

Level:
4

The card therefore expresses:

* what the object is,
* what it does,
* where it belongs in the knowledge process,
* and where it sits within the larger structure.

---

# [EPR-007] Principles

Roles are technical.

Phases are epistemic.

Symbols are mnemonic.

The symbolic layer must support the technical layer rather than replace it.

A Semantic Card should remain understandable even if the symbols are removed.

The purpose of symbols is navigation, memory, and recognition.

Meaning comes first.

Symbols follow meaning.

---

# [EPR-008] Fractal Phase Dynamics

The Four Epistemic Phases are not limited to a single scale.

A phase may appear:

* within a statement,
* within a function,
* within a class,
* within a module,
* or within an entire system.

The same phase pattern may therefore reappear across multiple levels of abstraction.

This principle is referred to as:

**Fractal Phase Dynamics**

Knowledge processes are recursive.

A cycle may exist inside another cycle.

A function may participate within a module-level cycle.

A module may participate within a system-level cycle.

A system may participate within a larger workflow.

The same epistemic movement may therefore appear repeatedly at different scales.

---

## Reference Cycle

The current model uses the following reference cycle:

Earth → Fire → Air → Water → Earth

This sequence must be preserved whenever possible.

Exceptional boundary cases may exist, but the cycle represents the primary movement of transformation.

Symbolically:

Earth
→ material
→ artifact
→ stabilized form

Fire
→ transformation
→ operation
→ activation

Air
→ temporary representation
→ temporary memory
→ intermediate state

Water
→ interpretation
→ analysis
→ flow

Earth
→ realized artifact
→ preserved result

The cycle may be understood as a recurring movement of information, structure, and realization.

---

## Scope-Relative Phase Principle

Phases are relative to the current scope of observation.

A structure that appears as Earth at one depth may appear as Air at another depth.

Example:

Within a function:

tree
→ Earth

because it represents the completed result of the local cycle.

Within a surrounding module:

tree
→ Air

because it serves as an intermediate representation used by subsequent operations.

Therefore:

A local artifact may become a temporary representation at a higher level of abstraction.

Likewise:

A temporary representation at one level may become a stabilized artifact at another.

Phases should therefore be interpreted relative to:

* depth,
* scope,
* and cycle boundaries.

Phase classification is not always absolute.

It is often scale-dependent.

---

## Reference Example

```python
def parse_file(path):
    text = read_file(path)
    tree = ast.parse(text)
    return tree
```

Local function cycle:

path
→ Earth

read_file(path)
→ Fire

text
→ Air

ast.parse(text)
→ Water

tree
→ Earth

Result:

Earth → Fire → Air → Water → Earth

However:

When observed from a higher-level workflow, the returned tree may become Air, serving as an intermediate representation within a larger cycle.

This illustrates the scope-relative nature of phase interpretation.

---

## Fractal Interpretation

Every cycle may contain smaller cycles.

Every completed artifact may become material for a larger process.

Statement Cycle
⊂ Function Cycle
⊂ Module Cycle
⊂ Package Cycle
⊂ System Cycle

The boundary between Earth and Air is therefore not fixed.

It depends on the current depth of observation.

This relationship forms one of the core principles of Fractal Phase Dynamics.

---

# [EPR-009] Semantic Rings and Semantic Seals

Not every component expresses a dominant phase.

Some components primarily exist to connect, coordinate, or activate multiple phases.

Examples:

* main()
* runner()
* workflow()
* pipeline()
* scheduler()
* event_loop()

These components are referred to as:

**Semantic Rings**

A Semantic Ring is not itself a phase.

Its purpose is to connect phases and complete a cycle.

A system becomes active when a Semantic Ring establishes a complete path through the necessary transformations.

---

## Semantic Seal

At the center of a Semantic Ring lies a unifying meaning.

This central meaning is referred to as a:

**Semantic Seal**

The Ring represents movement.

The Seal represents purpose/meaning.

Example:

Function:

parse_file()

Semantic Ring:

path → read → text → parse → tree

Semantic Seal:

"Transform text into structure."

Different implementations may share the same Semantic Seal while using different Semantic Rings.

---

## Principle

Ring and Seal should not be confused.

The Ring describes:

* process
* movement
* execution
* circulation

The Seal describes:

* intent
* meaning
* identity
* purpose

Movement follows the Seal.

Meaning precedes implementation.

A Semantic Seal represents the central meaning associated with a structure, transformation, or cycle.

The precise nature of Semantic Seals remains an area of ongoing exploration.

For now, a Seal should be understood as the meaning-centered counterpart to a Semantic Ring.

---

# [EPR-010] Elements, Modalities, and Archetypal Operations

## Purpose

This note extends the Role / Phase model through the traditional symbolic structure:

```
4 Elements × 3 Modalities = 12 Archetypal Operations
```

The goal is not to use popular astrology.

The goal is to study the symbolic logic of qualitative manifestation through a perennial framework.

---

## Guiding Principle

```
Element = qualitative field
Modality = mode of movement
Role = functional task
```

In the Semantic Observatory model:

```
Phase
    → What kind of semantic field is this?

Modality
    → How does this field move?

Role
    → What work does this card perform?
```

---

## Four Elemental Phases

The four phases correspond to the four elements.

```
Earth = fixed form / product / received material
Fire  = transformation / operation
Air   = temporary representation / conceptual structure
Water = flow / writing / transmission
```

---

## Three Modalities

The three modalities describe how a phase behaves.

```
Cardinal = initiating / opening / directing
Fixed    = stabilizing / preserving / sustaining
Mutable  = adapting / transitioning / transforming
```

Thus:

```
4 Elements
×
3 Modalities
=
12 Archetypal Operations
```

---

## Twelve Archetypal Operations

### Earth

```
Earth + Cardinal (Capricorn)
= form initiation
```

Starting a form, schema, model, file, or artifact.

```
Earth + Fixed (Taurus)
= form stabilization
```

Preserving stable data, constants, configuration, or persisted output.

```
Earth + Mutable (Virgo)
= form repositioning
```

Migrating, refactoring, or adapting an existing form.

---

### Fire

```
Fire + Cardinal (Aries)
= transformation initiation
```

Starting an operation, process, or transformation pipeline.

```
Fire + Fixed (Leo)
= transformation stabilization
```

Core transformation logic that consistently performs a defined operation.

```
Fire + Mutable (Sagittarius)
= transformation adaptation
```

Adapting transformation logic to context, strategy, or variant.

---

### Air

```
Air + Cardinal (Libra)
= representation initiation
```

Creating a type, interface, temporary model, or conceptual representation.

```
Air + Fixed (Aquarius)
= representation stabilization
```

Holding an AST, card, graph, or intermediate structure in a stable temporary form.

```
Air + Mutable (Gemini)
= representation remapping
```

Mapping, projecting, translating, or restructuring representations.

---

### Water

```
Water + Cardinal (Cancer)
= flow initiation
```

Beginning writing, exporting, streaming, or transmission.

```
Water + Fixed (Scorpio)
= flow channeling
```

Writing into a stable output format or controlled channel.

```
Water + Mutable (Pisces)
= flow adaptation
```

Streaming, syncing, updating, or distributing output dynamically.

---

## Programming Interpretation

This model may later be used to classify semantic cards.

Example:

```json
{
  "phase": "Fire",
  "modality": "Fixed",
  "zodiac": "Leo",
  "role": "Transformer"
}
```

This may indicate a core transformation function.

Example:

```json
{
  "phase": "Fire",
  "modality": "Mutable",
  "zodiac": "Sagittarius",
  "role": "Adapter"
}
```

These zodiac labels are included only as symbolic correspondences to the element–modality combination and do not imply astrological prediction or personality classification.

This may indicate a transformation adapter or strategy.

---

## Relation to Semantic Cards

A semantic card may be understood through three axes:

```
Phase
    elemental field

Modality
    inner movement

Role
    functional responsibility
```

Together, these axes help describe both:

```
what the card is
```

and

```
how the card acts
```

---

## Research Status

This model is experimental.

It should be treated as a symbolic research layer before becoming part of implementation.

Initial implementation should remain deterministic and simple.

Archetypal classification may be introduced after the base card, module, and UI systems are stable.

---

# [EPR-011] Archetypal Operations in Code

## Purpose

The purpose of this note is to illustrate how the twelve Archetypal Operations may appear within actual software systems.

The goal is not astrological classification.

The goal is practical semantic observation.

An Archetypal Operation should always be derived from:

```txt
Phase
    +
Modality
```

and only secondarily expressed through a zodiacal correspondence.

Because software behavior is context-dependent, classification should be based on the semantic role being performed within a specific scope rather than on the syntax of a statement alone.

---

## Reading Order

Classification should proceed in the following order:

```txt
Code
    ↓
Role
    ↓
Phase
    ↓
Modality
    ↓
Archetypal Operation
```

The zodiacal label is a symbolic shorthand.

It must never replace technical observation.

The same code fragment may express different Archetypal Operations depending on its role within the surrounding system.

---

# Earth Operations

Earth corresponds to:

```txt
Form
Artifact
Material
Persistence
```

---

## Earth + Cardinal

Capricorn

```python
class SemanticCard:
    ...
```

```python
cards = []
```

```python
output_path = "cards.json"
```

Interpretation:

```txt
Form Initiation

A stable form,
schema,
artifact path,
or material structure
is being established.
```

---

## Earth + Fixed

Taurus

```python
CONFIG = {
    "max_depth": 5,
    "view": "cards"
}
```

```python
CARD_TYPES = [...]
```

Interpretation:

```txt
Form Stabilization

Stable reference data,
constants,
configuration,
or preserved structures.
```

---

## Earth + Mutable

Virgo

```python
migrate_schema()
```

```python
refactor_cards()
```

Interpretation:

```txt
Form Repositioning

An existing structure
is being reorganized
without changing its fundamental purpose.
```

---

# Fire Operations

Fire corresponds to:

```txt
Transformation
Operation
Activation
```

---

## Fire + Cardinal

Aries

```python
start_pipeline()
```

```python
run_transform()
```

Interpretation:

```txt
Transformation Initiation

A transformation process
is being started or activated.
```

---

## Fire + Fixed

Leo

```python
build_cards(ast_tree)
```

```python
compress_ast(tree)
```

Interpretation:

```txt
Transformation Stabilization

A core transformation engine
consistently applies
a defined operation.
```

Note:

```python
build_cards(ast_tree)
```

is Fire + Fixed when it represents the stable core logic that repeatedly transforms AST material into Semantic Cards.

---

## Fire + Mutable

Sagittarius

```python
strategy.build_cards(ast_tree, mode="summary")
```

```python
adapter.convert(source)
```

Interpretation:

```txt
Transformation Adaptation

Transformation logic
changes according to context,
strategy,
mode,
or variant.
```

Note:

```python
build_cards(ast_tree)
```

may shift toward Fire + Mutable when its behavior adapts strongly according to configuration, mode, strategy, or target representation.

---

# Air Operations

Air corresponds to:

```txt
Temporary Representation
Conceptual Structure
Intermediate Memory
```

---

## Air + Cardinal

Libra

```python
cards = []
```

```python
graph = {}
```

```python
card = SemanticCard(...)
```

Interpretation:

```txt
Representation Initiation

A new temporary representation,
container,
or conceptual model
is being introduced.
```

---

## Air + Fixed

Aquarius

```python
call_graph = {...}
```

```python
semantic_cards = [...]
```

Interpretation:

```txt
Representation Stabilization

A temporary structure
is being held
for further use.
```

---

## Air + Mutable

Gemini

```python
map_cards_to_graph()
```

```python
translate_ast()
```

Interpretation:

```txt
Representation Remapping

One representation
is translated into another.
```

---

# Water Operations

Water corresponds to:

```txt
Flow
Writing
Transmission
Analysis
```

---

## Water + Cardinal

Cancer

```python
write_cards(cards)
```

```python
export_json(data)
```

Interpretation:

```txt
Flow Initiation

Information begins
to move outward.
```

---

## Water + Fixed

Scorpio

```python
json.dump(cards, file)
```

```python
save_graph(graph)
```

Interpretation:

```txt
Flow Channeling

Information is written
through a stable channel.
```

---

## Water + Mutable

Pisces

```python
async for event in stream:
    ...
```

```python
sync_updates()
```

Interpretation:

```txt
Flow Adaptation

Information moves
through a changing path.
```

---

# Principle

The twelve Archetypal Operations should be treated as:

```txt
Semantic Patterns
```

rather than:

```txt
Astrological Labels
```

The zodiacal correspondences are symbolic names for recurring operational forms.

Their purpose is:

```txt
Recognition
Navigation
Memory
```

not prediction.

Classification should remain role-dependent and context-sensitive.

A code fragment does not possess a permanent archetypal identity independent of its function within a system.

---

# Relation to Semantic Observatory

Within Semantic Observatory:

```txt
Phase
    =
Semantic Field

Modality
    =
Mode of Movement

Archetypal Operation
    =
Phase + Modality

Role
    =
Technical Responsibility
```

A Semantic Card may therefore be described through:

```txt
Role
Phase
Modality
Archetypal Operation
Depth
Level
```

This allows symbolic and technical descriptions to coexist within the same observational framework.

It also allows the same implementation pattern to receive different classifications when observed from different semantic scopes or responsibilities.

---

# [EPR-012] Ring Visibility, Completeness, and Partial Arcs

## Purpose

The purpose of this note is to describe how Semantic Rings appear within actual software systems.

A Semantic Ring may be:

* fully visible,
* partially visible,
* or syntactically compressed.

The underlying cycle may still exist even when some phases are hidden.

The goal is not to determine whether a ring exists.

The goal is to understand:

```txt
How much of the ring
is visible
within the current scope?
```

---

## Ring Visibility

A Semantic Ring may appear in different forms.

### Full Ring

The complete cycle is visible within the current scope.

### Compressed Ring

The complete cycle exists, but one or more phases are hidden by syntax or abstraction.

### Partial Arc

Only a segment of a larger ring is visible within the current scope.

A Partial Arc is not an incomplete structure.

It is a valid local observation of a larger cycle.

---

## Ring Completeness

Ring completeness describes how much of the reference cycle is observable.

The reference cycle is:

```txt
Earth → Fire → Air → Water → Earth
```

Completeness is expressed relative to the four primary phase transitions.

---

### 1/4

Single visible phase.

Example:

```txt
Earth
```

or

```txt
Water
```

Only one phase is visible within the current scope.

---

### 2/4

Visible transition.

Example:

```txt
Earth → Fire
```

or

```txt
Air → Water
```

A transformation path is visible.

---

### 3/4

Extended arc.

Example:

```txt
Earth → Fire → Air
```

or

```txt
Air → Water → Earth
```

Most of the cycle is visible.

One phase remains outside the current scope.

---

### 4/4

Complete cycle.

Example:

```txt
Earth → Fire → Air → Water → Earth
```

The complete semantic cycle is visible.

---

## Examples

### Compressed Ring

```python
def add(a, b):
    return a + b
```

Visible interpretation:

```txt
Earth → Fire → Earth
```

Expanded interpretation:

```txt
Earth
→ Fire
→ Air
→ Water
→ Earth
```

Ring Type:

```txt
Compressed Ring
```

Ring Completeness:

```txt
4/4
```

The cycle exists even though intermediate phases are hidden.

---

### Partial Arc

```python
save(data)
```

Interpretation:

```txt
Air
→ Water
→ Earth
```

Ring Type:

```txt
Partial Arc
```

Ring Completeness:

```txt
3/4
```

The operation represents a visible segment of a larger cycle.

---

### Rendering Example

```python
frame = render(world)
```

Interpretation:

```txt
Earth
→ Fire
→ Air
```

Ring Type:

```txt
Partial Arc
```

Ring Completeness:

```txt
3/4
```

The generated image is a temporary representation rather than a preserved artifact.

---

## Ring Scope

Ring interpretation depends on scope.

A structure that appears as:

```txt
2/4
```

at statement level

may appear as:

```txt
4/4
```

at function level.

Likewise:

A function-level Full Ring may become a Partial Arc within a larger workflow.

Completeness is therefore scope-relative.

---

## Principle

Semantic Ring analysis should not ask:

```txt
Is this a ring?
```

Instead, it should ask:

```txt
What portion of the ring
is visible here?
```

and:

```txt
At what scope
is the ring being observed?
```

---

## Relation to Fractal Phase Dynamics

Ring visibility is a consequence of Fractal Phase Dynamics.

Every cycle may contain smaller cycles.

Every visible ring may participate within a larger ring.

```txt
Statement Ring
⊂ Function Ring
⊂ Module Ring
⊂ Package Ring
⊂ System Ring
```

The same structure may therefore appear as:

```txt
Partial Arc
```

at one depth,

and:

```txt
Full Ring
```

at another.

Ring visibility, completeness, and scope should always be interpreted together.

# [EPR-013] Semantic CPG and the Projection Layer

The Semantic Observatory shall use a unified **Semantic Code Property Graph (Semantic CPG)** as its core analysis model. AST, CFG, DFG, and the Call Graph are generated as independent analyses and then merged into a single Semantic CPG through a shared node identity system.

The Semantic CPG is **not** intended to be rendered directly. Instead, all user interfaces are deterministic **projections** of the underlying graph.

```text
Semantic AST
      │
 ┌────┼────┐
 │    │    │
CFG  DFG  Call Graph
 │    │    │
 └────┼────┘
      ▼
 Semantic CPG
      ▼
 Projection Layer
      ├── Flowchart View
      ├── Ring View
      ├── Card View
      ├── Graph View
      └── Semantic View
```

Within this architecture, the Semantic CPG serves as the **Single Source of Truth**. Every visualization represents a deterministic projection of the same underlying analysis model, ensuring that visualization concerns remain completely separated from program analysis.

This separation allows multiple visual paradigms—such as flowcharts, ring layouts, semantic cards, or graph-based exploration—to coexist while remaining fully consistent with one another.

# [EPR-014] Geometric Cohesion and Edge Integrity

In the Semantic Observatory, the primary carrier of meaning is not the individual node, but the relationships between nodes. A graph derives its semantic integrity from the correctness and consistency of its connections.

Every semantic connection should satisfy the following principles:

- **Explicit** — Every relationship should be represented directly rather than inferred from hidden state or implicit behavior.
- **Deterministic** — Given the same source program, the same semantic relationship should always be produced.
- **Locally Consistent** — Every connection should obey the structural rules of its immediate neighborhood. Global correctness emerges from locally valid relationships.
- **Verifiable** — Every connection should be independently checkable against the graph's structural rules.

This principle is referred to as **Geometric Cohesion**: the integrity of the whole system emerges from the integrity of its connections.

Accordingly, the Semantic Observatory should validate not only individual nodes but also the semantic correctness of edges. Invalid transitions, inconsistent relationships, or broken structural rules should be treated as first-class graph validation errors.

Examples include:

- Invalid control-flow transitions.
- Invalid data dependencies.
- Illegal phase transitions.
- Broken element ordering.
- Missing structural links.
- Inconsistent semantic relationships.

Geometric Cohesion extends traditional program analysis from *node correctness* toward *relationship correctness*. The graph is considered structurally sound only when both its entities and their connections satisfy deterministic and verifiable rules.