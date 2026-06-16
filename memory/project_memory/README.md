# Project Memory

Use this directory for repository-specific conventions, architectural decisions,
and development history that should remain readable across sessions.

`project_memory` should be treated as the temporal localization of repository
development.

Source code shows the current concrete form.

`project_memory` preserves how that form emerged, shifted, narrowed, or gained
new layers over time.

In Semantic Observatory terms:

* code is one localization
* registry and specs are another localization
* project memory is the time-oriented localization of decisions and evolution

## Chronological Method

Project memory is maintained as a chronological notebook.

The goal is not to rewrite git history.

The goal is to preserve context:

* what changed
* why it mattered
* how the project direction evolved
* which conceptual layer was affected
* which localizations became aligned or diverged

## Structure

* `timeline.md`: high-level index of major milestones
* `chronology/`: month-based detailed notes in ascending date order
* `maintenance-standard.md`: update and review rules for keeping project memory useful

## Writing Rules

Prefer entries that are:

* date-first
* concrete
* short
* linked to real artifacts when possible

Use two note types:

* `commit-backed`: grounded in committed repository history
* `working-note`: useful local progress that may not be committed yet

Avoid generic diary text.

Record decisions, shifts in architecture, vocabulary changes, and meaningful UI
or tooling milestones.

When possible, describe a change in observatory-compatible terms:

* observation target
* localization change
* structural effect
* interface effect
* vocabulary or ontology effect

## Alignment With Semantic Observatory

`project_memory` is compatible with `memory/semantic_observatory/` when it
helps preserve conceptual continuity rather than only preserving event logs.

It should therefore help answer:

* What changed in the repository?
* Which layer changed: structural, relational, interface, presentation, or conceptual?
* How did the implementation move relative to observatory concepts?
* Which distinctions became clearer, for example `depth` vs `level` or `role` vs `phase`?

`project_memory` should not replace the observatory.

The observatory holds theory, vocabulary, and conceptual structure.

`project_memory` records when and how those concepts entered the repository or
changed its implementation.
