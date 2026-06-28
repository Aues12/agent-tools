# SO-UI-004 — Flat View Design Language (v2)

## Purpose

Flat View is the first production-ready interface of Semantic Observatory.

Its purpose is not to visualize the complete Observatory model.

Its purpose is:

* browsing semantic cards,
* filtering information,
* inspecting card content,
* validating generated semantic structures.

Flat View is primarily an inspection and research environment.

It serves as the foundation upon which future Observatory and Orbit views will be built.

---

# Core Design Principle

Flat View should not feel like:

* a corporate dashboard,
* an admin panel,
* an IDE inspector,
* an MMORPG quest tracker.

Instead, it should feel like:

> A modern research desk containing an ancient knowledge atlas.

The user should feel as if they are exploring a living manuscript rather than navigating software panels.

---

# Visual References

## Primary References

### Ancient Knowledge Atlases

* parchment manuscripts
* astronomy notebooks
* celestial maps
* navigational charts
* observatory journals

### Modern Research Tools

* Obsidian
* Notion
* Apple Human Interface Design

### FFXIV UI (Selective Inspiration)

FFXIV is not a direct visual reference.

However, several qualities are valuable:

* material depth
* elegant framing
* restrained gold accents
* layered information hierarchy
* calm mystical atmosphere

Avoid:

* quest tracker aesthetics
* fantasy inventory layouts
* oversized RPG icons
* glowing magical effects
* game-like HUD elements

The goal is not a game UI.

The goal is a scholarly interface with subtle mystical qualities.

---

# Material Language

## Parchment

The interface should not use completely flat surfaces.

Surfaces may contain:

* extremely subtle paper fibers
* extremely subtle noise
* extremely subtle aging

Texture should remain nearly invisible.

Users should not consciously notice it.

The result should feel warmer and more natural than a flat digital interface.

---

## Ink

Primary text should resemble ink on paper.

Readable, calm, and high-contrast.

Readability always takes priority over aesthetics.

---

## Gold

Gold is an accent color.

It should be used only for:

* active selections
* semantic highlights
* important navigation markers
* seals and symbolic elements

Gold should never dominate the interface.

---

# Geometric Identity

Semantic Observatory should not rely heavily on icons.

Preferred visual language:

* geometric seals
* symbolic markers
* directional forms
* subtle sacred geometry

Future versions may represent:

* phases
* directions
* operations

through geometric symbols.

Flat View only establishes the foundation of this language.

---

# Information Architecture

Flat View must scale to hundreds or thousands of semantic cards.

Cards should not be rendered directly as large items inside navigation lists.

The interface should follow a progressive left-to-right reading flow.

```text
[Index Panel]
      →
[Card Name List]
      →
[Card View]
      →
[Card Details]
```

This structure supports:

1. filtering
2. browsing
3. inspection
4. analysis

in a natural sequence.

---

# Four-Column Layout

## Column 1 — Index Panel

Purpose:

* search
* filters
* kind selection
* role selection
* phase selection
* module selection

This column should remain narrow.

Its purpose is navigation.

Not content.

---

## Column 2 — Card Name List

The atlas index.

This is the primary browsing area.

Contains:

* card names
* short metadata
* optional seal indicators

This list must be:

* scrollable
* compact
* information-dense

The user should be able to navigate hundreds of cards efficiently.

Full card rendering should not happen here.

---

## Column 3 — Card View

The selected card.

This is where the visual identity of Semantic Observatory appears.

The card may display:

* title
* summary
* phase
* role
* semantic seal
* essential metadata

This view should prioritize clarity and beauty over information density.

Purpose:

> Reveal the identity of the card.

---

## Column 4 — Card Details

Deep inspection area.

May contain:

* overview
* relations
* DFG
* traces
* semantic links
* future observatory data

Purpose:

> Reveal everything known about the card.

---

# Component Architecture

Flat View should be composed of small independent components.

```text
SemanticFlatView
│
├── IndexPanel
│
├── CardNameListPanel
│
├── CardViewPanel
│
└── CardDetailPanel
```

Each component should:

* have a clear responsibility,
* be independently testable,
* be independently maintainable,
* be reusable in future views.

This architecture is intended to support:

* Flat View
* Orbit View
* Observatory View

without major rewrites.

---

# Card Philosophy

Cards should remain compact.

A card represents:

* one concept
* one observation
* one semantic unit

Cards exist to communicate meaning.

Not to occupy space.

Avoid excessive padding and oversized layouts.

---

# Workspace Metaphor

The interface should feel like:

```text
Tools
   →
Atlas Index
   →
Open Page
   →
Research Notes
```

or

```text
Filters
   →
Catalog
   →
Current Manuscript
   →
Annotations
```

The experience should resemble studying a document.

Not managing software panels.

---

# Future Views

Flat View is not the final destination.

Future interfaces may include:

* Orbit View
* Observatory View
* Star Map View

These views may introduce:

* circular navigation
* semantic directions
* orbital relationships
* geometric positioning
* observatory-style exploration

Flat View remains the structured inspection layer beneath them.

---

# Final Design Goal

Semantic Observatory should feel like:

> Obsidian's information density,
>
> FFXIV's material richness,
>
> an ancient astronomical atlas,
>
> and a modern research workstation,
>
> combined into a single coherent interface.
