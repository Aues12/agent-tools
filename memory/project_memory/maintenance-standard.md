# Project Memory Maintenance Standard

This document defines how `project_memory` should be updated and reviewed.

The goal is to make maintenance routine rather than optional.

## Purpose

Project memory should preserve development continuity.

It should remain:

* chronological
* concept-aware
* implementation-aware
* lightweight enough to maintain

## Update Triggers

Update `project_memory` when one or more of the following happens:

* a new tool, subtool, or runtime layer is introduced
* a major refactor changes boundaries or architecture
* a new conceptual distinction becomes operationally important
* a UI experiment establishes a reusable design rule
* repository vocabulary changes or becomes more precise
* a meaningful scope reduction removes an earlier direction
* a memory document in `semantic_observatory/` begins affecting implementation choices

Do not update it for trivial formatting-only changes unless they materially
change how the repository is understood.

## Required Update Pattern

For a meaningful milestone:

1. Add or extend the detailed month file under `chronology/`
2. Update `timeline.md` if the milestone changes the high-level story
3. Link the note to commits, files, or memory documents when possible

## Entry Shape

Each chronology entry should include:

* date
* note type: `commit-backed` or `working-note`
* observed milestones
* important artifacts or commits
* interpretation

Prefer short sections over long prose.

## Observatory Alignment Rules

When possible, each entry should identify one or more affected layers:

* structural localization
* relation localization
* interface localization
* presentation localization
* conceptual or ontological vocabulary

Good entries explain not only what changed, but where the change belongs.

## Review Standard

Review `project_memory` when:

* a new conceptual subsystem appears
* a release-sized milestone is reached
* a UI direction becomes stable enough to name
* the timeline starts drifting from actual repository history

During review, check:

* Is the high-level timeline still truthful?
* Are month files still chronological and readable?
* Are important repository shifts missing?
* Do entries reflect observatory vocabulary where useful?
* Are theory documents and implementation notes still connected?

## Practical Maintenance Rhythm

Recommended rhythm:

* after a major implementation session: add a short `working-note`
* after a meaningful commit cluster lands: convert or complement with `commit-backed` notes
* after conceptual documents start changing implementation decisions: mention that bridge explicitly

## Non-Goals

`project_memory` is not:

* a substitute for git history
* a complete changelog
* a task scratchpad
* a philosophical notebook by itself

It is the repository's development memory.
