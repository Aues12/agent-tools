# Agent Specification

## Purpose

Agents orchestrate reasoning, planning, skills, and tools. They should use the
repository's reusable capabilities instead of rewriting procedural behavior from
scratch.

## Operating Rules

Agents working in this repository should:

* read the nearest `AGENTS.md` before editing.
* prefer existing tools and skills over ad hoc scripts.
* preserve user changes and avoid destructive actions.
* keep tool behavior deterministic where practical.
* update registry metadata when adding tools or skills.
* add tests and examples for new capabilities.
* document any side effect that changes files or state.

## Decision Pattern

When handling a task, an agent should:

1. identify whether the task is a tool, skill, runtime, registry, memory, or
   state concern.
2. inspect existing reusable capabilities.
3. select the narrowest applicable tool or skill.
4. implement missing capability only when reuse is not enough.
5. validate the result with tests or examples.

## Portability

Agents should avoid coupling repository concepts to one provider, model, or
agent runtime. Provider-specific integrations should be adapters rather than
core concepts.
