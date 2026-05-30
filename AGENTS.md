# AGENTS.md

## Purpose

This repository is an experimental agent-tools development environment.

The goal is to build a modular capability layer where:

* LLMs focus on reasoning, planning, and parameter generation.
* Tools provide reusable, bounded capabilities.
* Skills provide reusable workflows.
* A runtime coordinates execution.

The system is designed to support both:

* large reasoning models
* smaller local models

---

# Quick Navigation

Read in this order when onboarding:

1. `AGENTS.md` (this file): architecture and contracts
2. `USE_TOOL.md`: standard tool usage contract
3. `registry/tool_registry.json`: discoverable tool map
4. `standards/`: formal specs (`TOOL_SPEC.md`, `SKILL_SPEC.md`, `AGENT_SPEC.md`)

---

# USE_TOOL

For standard tool invocation, request/response envelope, and CLI examples, see:

* `USE_TOOL.md`

This file stays architecture-focused and tool-agnostic.

---

# Core Philosophy

Models should not rewrite every procedure from scratch.

Instead:

* reusable capabilities should exist as tools
* reusable procedures should exist as skills
* the model should orchestrate and parameterize them

Tools are treated as capabilities/faculties (Turkish: "Meleke, Kuvvet") rather than generic helper code.

---

# Architectural Direction

Intended flow:

```text
LLM
  ↓
Planner / Agent
  ↓
Skills or Tools
  ↓
Execution Runtime
```

The architecture is intentionally:

* modular
* inspectable
* composable
* agent-agnostic

---

# Repository Structure

```text
agent-tools/
│
├── standards/          # specs and naming rules
├── templates/          # starter templates for tools/skills
├── meta-skills/        # skills that create/maintain ecosystem assets
├── file-tools/         # deterministic tool implementations
├── runtime/            # orchestration runtime (current + future)
├── registry/           # discoverability and metadata registries
├── memory/             # long-lived memory categories
├── agent-playground/   # analysis outputs and experiment artifacts
└── test-data/          # test fixtures/sample inputs
```

---

# Tool Philosophy

Tools should:

* do one thing well
* remain deterministic where possible
* expose narrow interfaces
* avoid hidden side effects
* remain composable and testable

Preferred implementation approach:

* Python-first
* shell only when necessary

Tool functions should include concise docstrings/comments where they improve clarity.

---

# Skill Philosophy

Skills are reusable workflows, not low-level capabilities.

A skill orchestrates tools and agent actions, and should declare:

* inputs
* outputs
* steps
* validation checks

Skills should be concrete enough for smaller models to execute reliably.

---

# Meta-Skills

Meta-skills maintain and grow the ecosystem itself.

Examples:

* create_tool
* create_skill
* update_registry
* generate_tests

Long-term expectation:

* meta-skills become executable pipelines, not only documentation.

---

# Selection Problem

A key design target is reducing manual line-number reasoning.

Instead of selecting text by fragile offsets, prefer semantic locators/selectors
that narrow targets before mutation.

This improves:

* reliability
* determinism
* token efficiency
* small-model usability

---

# Future Architecture

This section consolidates long-term runtime direction.

## Runtime

The runtime is the orchestration kernel. Expected responsibilities:

* skill execution
* tool dispatching
* executor management
* task lifecycle handling
* event processing

Possible structure:

```text
runtime/
├── engine.py
├── planner.py
├── dispatcher.py
├── executor_manager.py
├── task_queue.py
├── event_bus.py
├── state_manager.py
└── memory_manager.py
```

## Registry

The registry is the capability map. It should track:

* tools
* skills
* executors
* metadata and versions

Possible structure:

```text
registry/
├── tool_registry.json
├── skill_registry.json
├── executor_registry.json
└── loader.py
```

## Memory

Memory stores longer-lived information (distinct from runtime state).

Potential categories:

```text
memory/
├── procedural/
├── semantic/
├── task_history/
├── project_memory/
└── preferences/
```

Focus area:

* procedural memory (reusable know-how about how work is performed)

## State

State represents current runtime conditions.

Examples:

* active project/branch/task
* active skill
* recent tool usage
* last modified files

Preferred direction:

* event-driven state updates from tool/runtime events

Example event:

```json
{
  "event": "file_modified",
  "file": "app.py"
}
```

## Executors and Model Coordination

Potential executor families:

* Python
* Bash
* Git
* Codex
* Local model runtimes

Long-term runtime goals:

* stateful orchestration
* registry-backed discoverability
* memory integration
* execution history
* permission systems
* multi-model coordination

---

# Agent-Agnostic Principle

This ecosystem should not depend on a single agent framework or model vendor.

It is a portable capability layer intended to integrate with multiple
orchestration environments.

---

# Current Priorities

Current implementation priorities:

1. standards/
2. template system
3. meta-skill system
4. create_tool/create_skill execution workflows
5. registry maturity
6. tool chaining/orchestration

Permission systems remain intentionally postponed until runtime contracts
stabilize.

---

# Implementation Contracts

New tools should include:

* local `AGENTS.md`
* `SKILL.yaml`
* `tool.py`
* tests
* examples
* registry entry

New skills should include:

* `SKILL.yaml`
* concrete workflow steps
* required inputs/outputs
* validation checks
* registry entry

When adding/modifying capabilities:

* keep interfaces narrow
* document side effects explicitly
* validate before mutation
* update registries for discoverability
* add tests before considering a capability usable
* prefer 1-based line numbers for user-facing text selection APIs

---

# Design Principles

The ecosystem should optimize for:

* modularity
* inspectability
* composability
* low-context execution
* deterministic tooling
* reusable procedural memory
* compatibility across model sizes

The goal is not only code generation.

The goal is orchestrated, reusable, inspectable intelligent behavior.
