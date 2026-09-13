# Semantic Observatory

*A working notebook on meaning, observation, structure, localization, geometry, and software architecture.*

Semantic Observatory is a collection of interconnected theories, observations, and design experiments.

Its purpose is not to preserve conclusions, but to preserve conceptual continuity while ideas evolve.

The observatory treats knowledge as a network of observations connected through relationships.

Software serves as the initial domain of exploration, but the principles described here are intended to apply more broadly to knowledge systems, scientific models, philosophy, history, and other structured domains.

---

## Directory Tree

```text
semantic_observatory/
├── README.md
├── epistemic-grounding.md
├── phase-interpretation-contract.md
├── epistemic-phases-and-roles.md
├── faz-döngüleri.md
├── flat-view-ui.md
├── foundations.md
├── function-mandala.md
├── geometric-field-engine.md
├── implementation-map.md
├── localization.md
├── observation-theory.md
├── ontological-layer.md
├── question-centered-knowledge.md
├── quest-tree.md
├── semantic-architecture.md
├── semantic-cards.md
├── semantic-ui.md
├── semantic-ui-design.md
├── semantic-workbench.md
├── symbolic-geometry.md
├── the-zodiac.md
└── vertical-ontology.md
```

---

## Document Status

```text
Status        Documents
---------------------------------------------------------------
Active Core   foundations, observation-theory, localization,
              vertical-ontology, semantic-cards,
              epistemic-phases-and-roles, epistemic-grounding

Active Bridge implementation-map, semantic-architecture,
              semantic-ui, flat-view-ui, semantic-ui-design,
              phase-interpretation-contract

Experimental  symbolic-geometry, geometric-field-engine,
              function-mandala, quest-tree, semantic-workbench,
              ontological-layer, faz-döngüleri, the-zodiac,
              question-centered-knowledge

Future        star maps, repository-scale observatory maps,
              build mode contracts, projection-layer schemas
```

Active Core documents define the conceptual language.

Active Bridge documents connect that language to implementation, UI, and
product direction.

Experimental documents are important research notes, but should not be treated
as executable contracts until they are mapped through `implementation-map.md`,
tool schemas, or UI specifications.

---

## Conceptual Architecture

The observatory is organized into complementary layers.

### [OBS] Observation Theory

Knowledge Ontology

Question:

What exists?

Observation Units are the fundamental objects of knowledge.

---

### [LOC] Localization Theory

Representation Ontology

Question:

How does it appear?

Localizations describe how meaning manifests through different representations.

---

### [VRT] Vertical Ontology

Structural Ontology

Question:

How is it layered?

Vertical Ontology studies abstraction, implementation, hierarchy, and navigation between levels.

---

### [SC] Semantic Cards

Knowledge Interface

Question:

How is it presented?

A Semantic Card is a localization of an Observation Unit within a navigable knowledge system.

Cards act as interfaces between observations and users.

---

### [QST] Quest Tree

Navigation Ontology

Question:

How is it navigated?

Quest Trees organize pathways through knowledge.

---

### [GEO] Geometry

Visual Ontology

Question:

How is it visualized?

Geometry studies spatial and symbolic representations of meaning, structure, and relationships.

Current geometry documents are exploratory. They define visual-localization
principles and future projection ideas, but they do not yet define a stable
tool contract.

---

## Current Implementation Alignment

The current executable Semantic Observatory stack is:

```text
Python source
  ↓
semantic_ast          structural localization
  ↓
semantic_cfg          local control-flow localization
semantic_dfg          local value-flow localization
call_graph            local function-call localization
  ↓
semantic_cpg          unified analysis localization
  ↓
semantic_cards        card/interface localization
  ↓
semantic_view         compact presentation localization
  ↓
semantic_observatory_pipeline
  ↓
semantic_observatory_ui
```

The UI currently emphasizes Flat View card inspection. CPG-aware artifacts are
available for future projection layers, while geometric and mandala views remain
conceptual until their construction rules stabilize.


## Epistemic clarification

Read [Epistemic Grounding](epistemic-grounding.md) for target/claim/basis
distinctions and [Phase Interpretation Contract](phase-interpretation-contract.md)
for the boundary between symbolic readings and executable phase assignments.
These notes clarify the engineering use of the evolving research vocabulary.

## Question-centered knowledge direction

[Question-Centered Knowledge and Bounded Memory](question-centered-knowledge.md)
explores source access, meaning construction, retrieval, and knowledge
maintenance through progressive disclosure and explicit context/storage
budgets. It is a research direction, not an implemented memory subsystem.

## Core Documents

### [FND] Foundations

The foundational principles of the observatory.

Questions:

* What is meaning?
* What is structure?
* What is correspondence?
* What is localization?

---

### [OBS] Observation Theory

The study of observations as the fundamental units of knowledge.

Questions:

* What is an observation?
* How do observations relate?
* How does knowledge emerge?

---

### [LOC] Localization Theory

The study of how meaning appears through different representations.

Questions:

* How does meaning manifest?
* What is a localization?
* How do different representations correspond to each other?

---

### [VRT] Vertical Ontology

The study of knowledge as a vertically navigable structure.

Questions:

* How do levels of abstraction relate?
* What are the Tower and the Dungeon?
* What is vertical navigation?
* What is the hierarchy of knowledge?

---

### [SC] Semantic Cards

The study of cards as containers, portals, and navigation units.

Questions:

* What is a Semantic Card?
* How should observations be organized?
* How can knowledge be compressed without losing meaning?

---

## Future / Deferred Documents

### [MAP] Star Maps

Knowledge constellations, regions, pathways, and navigable conceptual spaces.

### Projection Layer Schemas

Stable JSON contracts for flowchart, geometric field, telescope, and map views.

### Build Mode Contracts

Rules for moving from observation interfaces into architecture-editing and
source-synthesis workflows.

---

## Guiding Principle

Observe.

Relate.

Compress.

Navigate.

Understand.
