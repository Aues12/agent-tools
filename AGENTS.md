# AGENTS.md

## Purpose

This repository develops independent tools with contracts that make them usable
by AI agents. It is an experimental collection of capabilities, specifications,
and examples, not a single agent application.

The goal is a modular capability layer where:

* LLMs focus on reasoning, planning, and parameter generation.
* Tools provide reusable, bounded capabilities.
* Shared contracts make tools discoverable and predictable to callers.
* Skills describe reusable workflows; the current meta-skills are drafts.

Agents and external orchestration environments can call these tools. This
repository does not currently implement an execution runtime.

The system is designed to support both:

* large reasoning models
* smaller local models

---

# Quick Navigation

Read only the context needed for the current task:

1. To **find a capability**, scan the tool table in `README.md` or search
   `registry/tool_registry.json` for a task keyword. Do not read the whole
   registry unless auditing it.
2. To **use one tool**, read its local `SKILL.yaml` or README and an example
   request. Follow its local `AGENTS.md` if present. Do not load unrelated
   tool descriptions.
3. To **change a tool**, read its local `AGENTS.md`, implementation, and
   tests. Consult `USE_TOOL.md` for the shared invocation envelope.
4. Read `standards/` when changing contracts or adding capabilities, and
   `FUTURE_IMPROVEMENTS.md` only for roadmap work.

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
* an agent should select and parameterize them as needed

Tools are treated as capabilities/faculties (Turkish: "Meleke, Kuvvet") rather than generic helper code.

---

# Architectural Direction

Current tool-use model:

```text
Human or agent
  ↓ discovers a capability through documentation or registry
Tool interface (documented request and response)
  ↓
Independent tool implementation
  ↓
Structured result
```

Skills may guide multi-step use. A host runtime may invoke tools, but it is
not a required layer or an implemented component of this repository.

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
├── book-editing-tools/ # manuscript audits, plan validation, safe DOCX assembly
├── visual-tools/       # current artifact visualization apps
├── experiments/        # legacy apps with separate input contracts
├── runtime/            # notes on possible runtime integration; no implementation
├── registry/           # discoverability and metadata registries
├── memory/             # long-lived memory categories
├── agent-playground/   # small examples and historical analysis notes
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

---

# Agent-Agnostic Principle

This ecosystem should not depend on a single agent framework or model vendor.

It is a portable capability layer intended to integrate with multiple
orchestration environments.

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

The goal is reusable, inspectable capabilities that agents can invoke without
depending on one orchestration system.
