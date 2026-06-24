# Semantic UI

Semantic UI defines how Semantic Observatory concepts become interactive visual interfaces.

It translates semantic cards, roles, phases, relations, flowcharts, trees, and future observatory maps into usable screen structures.

---

## Purpose

The UI should make semantic structure observable.

It should help users move from:

```txt
source code
    ↓
semantic cards
    ↓
relations
    ↓
architecture
```

The first implementation should remain simple and deterministic.

---

## UI Strategy

Semantic Observatory may eventually support multiple interface models.

### Flat Interface

A simple screen-based interface.

Useful for:

* card lists
* search
* filters
* detail panels
* fast inspection

This should be the first implementation target.

### Flowchart Interface

The first visual architecture view.

Useful for:

* card order
* dependency flow
* phase flow
* module pipelines
* architecture inspection

### Telescope Interface

A zoom-based observatory interface.

Useful for:

* repository-scale navigation
* module clusters
* constellation views
* general-to-specific exploration

### Build Mode

An architecture-editing mode.

Useful for:

* drag-and-drop card ordering
* blueprint editing
* source synthesis preparation
* architecture construction

Build Mode should come after the observation interfaces are stable.

---

## v0.1 Goal — Flat Card Inspector

```txt
cards.json
    ↓
card list
    ↓
selected card
    ↓
card details
```

The user should be able to:

* view a list of cards
* search cards
* filter cards
* select one card
* inspect the selected card
* see basic relations and trace information

---

## v0.1 Screen Layout

```txt
┌────────────────────┬────────────────────────────┐
│ Search / Filters   │ Selected Card              │
│                    │                            │
│ Card List          │ SemanticCard Component     │
│                    │                            │
│ build_call_graph   │ Details                    │
│ parse_source       │ Relations                  │
│ compress_ast       │ Trace                      │
│                    │                            │
└────────────────────┴────────────────────────────┘
```

---

## Core Views

### Card List

The left panel lists available semantic cards.

The list should support:

* text search
* role filter
* phase filter
* kind filter
* module filter

### Selected Card View

The right panel displays the selected card.

It should reuse the existing Semantic Card component.

### Card Details

Below or beside the visual card, show structured details:

* title
* kind
* role
* phase
* summary
* source trace
* relations

### DFG Enrichment

For function cards, a local Data Flow Graph may enrich the card without
replacing it.

The DFG shows function-internal value movement.

The Semantic Card remains the navigable semantic unit.

```txt
Semantic Card
    ↓
DFG detail
    ↓
function-internal flow
```

This keeps the card stable while allowing users to inspect how values enter,
transform, and leave the local function scope.

---

## Data Model

The UI should consume generated semantic data.

It should not become the source of truth.

Expected inputs:

```txt
cards.json
relations.json
sourcemap.json
```

The UI renders and later may edit views.

Semantic truth remains in upstream artifacts.

---

## v0.2 Goal — Flowchart View

```txt
cards.json
    ↓
flowchart nodes
    ↓
flowchart edges
    ↓
interactive flowchart
```

The Flowchart View should help users:

* see card order
* inspect dependency flow
* follow relations between cards
* understand simple pipelines
* navigate architecture visually

---

## Flowchart Layout

```txt
┌─────────────────────────────────────┐
│ Search / Filters                    │
├─────────────────────────────────────┤
│                                     │
│        Flowchart Canvas             │
│                                     │
│        ○ ──→ ○ ──→ ○                │
│              │                      │
│              ↓                      │
│              ○                      │
│                                     │
├─────────────────────────────────────┤
│ Selected Card Details               │
└─────────────────────────────────────┘
```

---

## Flowchart Rules

Flowchart layout should prefer semantic clarity over visual decoration.

Initial ordering may follow:

```txt
dependencies
    ↓
card order
    ↓
phase order
    ↓
module grouping
```

The first Flowchart View should be inspection-only.

No source code should be modified from the flowchart.

---

## v0.3 Goal — Phase Lanes and Module Grouping

Phase lanes organize cards by phase.

Module grouping organizes cards by module.

This helps answer questions such as:

```txt
Is this module a full local pipeline?
```

or:

```txt
Is this module only one stage of a larger pipeline?
```

---

## v0.4 Goal — Telescope Interface

The Telescope Interface introduces zoom-based navigation.

Navigation becomes magnification.

Users move through levels such as:

```txt
Repository
    ↓
Subsystem
    ↓
Module
    ↓
Card
```

or:

```txt
Observatory
    ↓
Constellation
    ↓
Cluster
    ↓
Card
```

---

## v0.5 Goal — Build Mode

Build Mode introduces architecture editing.

It may support:

* drag-and-drop card ordering
* blueprint editing
* module synthesis preparation
* source synthesis workflows

Build Mode must remain separate from Inspection Mode.

```txt
Inspection Mode
    → observe architecture

Build Mode
    → modify architecture
```

User edits should update blueprint/order data.

They should not directly rewrite source code.

---

## Relationship to Card-Driven Architecture

The UI should gradually reveal that:

```txt
card ordering = architecture
```

In early versions, this is observed.

In later versions, this may be edited.

---

## Design Principle

Start flat.

Then add depth.

Then add construction.

```txt
Flat UI
    ↓
Flowchart UI
    ↓
Phase / Module Views
    ↓
Telescope UI
    ↓
Build Mode
```

The first version should be easy to build, easy to test, and easy to understand.
