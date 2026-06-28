# Semantic UI Design Notes

This document records visual design direction for Semantic Observatory UI
experiments.

The current Flat Card Inspector v0.1 behavior is the stable reference. Design
experiments should preserve the same information architecture and data model.

The canonical Flat View design brief is:

* `memory/semantic_observatory/flat-view-ui.md`

---

## Stable Interaction Contract

Design variants should keep these functions intact:

* card list
* search
* filters
* selected semantic card
* overview details
* relations
* DFG enrichment
* trace information

Design variants should not redefine semantic truth. They only change how the
same semantic artifacts are perceived.

---

## Flat View v0.2 Structure

Flat View v0.2 uses a four-column research desk model:

```txt
Tools / Filters
    →
Atlas Index
    →
Open Page
    →
Research Notes
```

This maps to the component structure:

```txt
SemanticFlatView
├── IndexPanel
├── CardNameListPanel
├── CardViewPanel
└── CardDetailPanel
```

The structure separates navigation from browsing, browsing from card identity,
and card identity from deep inspection.

---

## Visual Language Directions

### Modern Reference

The current default style is a restrained inspector interface.

It favors:

* neutral surfaces
* teal accents
* dense readability
* operational clarity

This remains the baseline for comparison.

### Ancient / Parchment Variant

The Design Lab parchment variant explores a more magical but still simple visual
language on top of the same Flat View data model.

It favors:

* parchment-colored backgrounds
* gold structural lines
* warm ink text
* restrained ritual atmosphere
* a light Ancient Egypt resonance

The goal is not theatrical decoration or a separate product mode. The interface
should feel quietly symbolic, readable, and artifact-like.

---

## Constraints

Design Lab changes should:

* keep the Flat Card Inspector workflow unchanged
* keep cards readable at desktop and mobile sizes
* avoid decorative clutter
* avoid making DFG details feel secondary or ornamental
* keep phase, depth, level, and flow level visually distinguishable
* remain reversible by switching visual language

---

## Open Design Questions

* Can phase symbols become subtle ritual markers without reducing clarity?
* Should DFG edges receive stronger gold-line treatment than card borders?
* Can depth and flow level be expressed through spacing and tone together?
* Should future phase-lane views use temple/pylon-like column rhythm, or stay
  closer to dense inspector ergonomics?
