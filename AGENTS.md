# AGENTS.md

## Purpose

This repository is an experimental agent-tools development environment.

The long-term goal is to build a modular AI-oriented orchestration system where:

* LLMs focus on reasoning, planning, and parameter generation.
* Tools provide reusable capabilities.
* Skills provide reusable workflows.
* The runtime coordinates execution.
* Behavior becomes modular, inspectable, and composable.

The system should support both:

* large reasoning models
* smaller local models

by externalizing procedural behavior into tools and skills.

---

# Core Philosophy

The model should not rewrite every workflow from scratch.

Instead:

* reusable capabilities should exist as tools
* reusable procedures should exist as skills
* the model should orchestrate and parameterize them

This repository treats tools as "capabilities" or "faculties" (Turkish: "kuvvet" veya "meleke") rather than simple helper functions.

Examples:

| Tool         | Capability   |
| ------------ | ------------ |
| rename_files | organization |
| copy_paste   | transfer     |
| find_block   | localization |
| compare      | comparison   |

---

# Architectural Direction

The intended architecture is:

```text
LLM
  ↓
Planner / Agent
  ↓
Skills or Tools
  ↓
Execution Runtime
```

The runtime may later include:

* state tracking
* procedural memory
* permission systems
* logging
* tool registries
* skill registries
* multi-agent orchestration

---

# Repository Structure

```text
agent-tools-dev/
│
├── standards/
│   ├── TOOL_SPEC.md
│   ├── SKILL_SPEC.md
│   ├── AGENT_SPEC.md
│   └── naming.yaml
│
├── templates/
│   ├── tool_template/
│   └── skill_template/
│
├── meta-skills/
│   ├── create_tool/
│   └── create_skill/
│
├── file-tools/
│   ├── copy_paste/
│   │   ├── AGENTS.md
│   │   ├── SKILL.yaml
│   │   ├── tool.py
│   │   ├── tests/
│   │   └── examples/
│   │
│   └── rename_files/
│       ├── AGENTS.md
│       ├── SKILL.yaml
│       ├── tool.py
│       ├── tests/
│       └── examples/
│
├── runtime/
│
├── registry/
│
├── memory/
│
└── state/
```

---

# Tool Philosophy

Tools should:

* do one thing well
* remain deterministic where possible
* expose narrow interfaces
* avoid hidden side effects
* be composable
* remain testable

Preferred approach:

* Python-first implementation
* shell usage only when necessary

Tool execution should ideally remain:

* cross-platform
* inspectable
* versionable
* safe to orchestrate

Tool functions should also include short explanatory comments/docstrings.

Reasoning:

* improves readability
* helps small models understand intent
* improves maintainability
* supports automated tooling and parsing
* reduces ambiguity during orchestration

---

# Skill Philosophy

Skills are reusable workflows.

A skill is not a tool.

A skill orchestrates tools and Agent tasks.

Example:

```yaml
name: move_function

steps:
  - tool: find_block
  - tool: extract_block
  - tool: insert_text
```

Skills may later support:

* branching
* retries
* validation
* memory access
* permissions
* state awareness

---

# Meta-Skills

Meta-skills are skills that create or organize the skill ecosystem itself.

Examples:

* create_tool
* create_skill
* update_registry
* generate_tests

These meta-skills are intended to help the ecosystem grow consistently.

---

# Initial Tool: copy_paste

The first major tool will be:

```text
copy_paste
```

Purpose:

Safely move or duplicate text blocks between files.

Initial capabilities:

```python
read_file(path)
find_text(file, text)
extract_range(file, start, end)
insert_text(file, line, content)
```

Future planned capabilities:

* semantic block finding
* indentation preservation
* duplicate prevention
* structural insertion
* AST-aware operations
* multi-file workflows

---

# Selection Problem

One important architectural goal is solving the:

```text
selection problem
```

Meaning:

The model should not need to manually reason about exact line numbers whenever possible.

Instead:

* helper tools
* locators
* semantic selectors

should narrow the execution target.

Example:

```python
find_block(
    file="app.py",
    query="def main"
)
```

This design helps:

* small models
* orchestration reliability
* deterministic execution
* token efficiency

---

# Runtime, Registry, Memory, and State

## Runtime

The runtime acts as the orchestration kernel of the ecosystem.

Responsibilities may include:

* skill execution
* tool dispatching
* executor management
* workflow orchestration
* task lifecycle management
* event processing

Possible future runtime structure:

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

The runtime should eventually support event-driven orchestration.

Example flow:

```text
↓
Event
↓
Runtime
↓
State Update
↓
Memory Update
Tool
```

---

## Registry

The registry acts as the capability map of the ecosystem.

It tracks:

* available tools
* available skills
* available executors
* metadata and versions

Possible future structure:

```text
registry/
├── tool_registry.json
├── skill_registry.json
├── executor_registry.json
└── loader.py
```

---

## Memory

Memory is intended for longer-lived information.

Potential memory categories:

```text
memory/
├── procedural/
├── semantic/
├── task_history/
├── project_memory/
└── preferences/
```

Important distinction:

* memory stores long-term information
* state stores current runtime conditions

The system is especially interested in:

```text
procedural memory
```

Meaning:

Reusable knowledge about how tasks are commonly performed.

Examples:

* preferred project structures
* preferred package managers
* recurring workflows
* coding conventions

---

## State

State represents the current condition of the running system.

Examples:

* active project
* active branch
* active skill
* last modified files
* recent tool usage
* running tasks

Possible future structure:

```text
state/
├── session_state.json
├── runtime_state.json
├── active_tasks.json
└── context_cache/
```

State should eventually update automatically.

Preferred long-term approach:

```text
event-driven state updates
```

Meaning:

Tools emit events.

The runtime processes those events and updates:

* state
* memory
* execution history

Example:

```json
{
  "event": "file_modified",
  "file": "app.py"
}
```

This separation allows:

* deterministic tools
* centralized state handling
* cleaner orchestration
* improved scalability

---

# Runtime Direction

Long-term runtime goals:

* stateful orchestration
* tool registries
* skill registries
* memory systems
* execution history
* permission systems
* multi-model coordination

Possible future executor structure:

```text
Executors/
├── Python
├── Bash
├── Git
├── Codex
└── Local Models
```

---

# Agent-Agnostic Philosophy

This ecosystem is intended to remain:

```text
agent-agnostic
```

Meaning:

The tool and skill system should not depend on a single agent framework, model provider, or orchestration runtime.

The architecture should remain portable and reusable across different systems.

Possible integrations may include:

* Pi Agent
* Codex
* local LLM runtimes
* future orchestration frameworks
* custom runtimes

The repository therefore focuses on:

* reusable capabilities
* modular workflows
* standardized interfaces
* inspectable execution
* portable orchestration patterns

The long-term goal is to build a flexible capability layer that can operate independently from any single agent implementation.

---

# Current Priorities

Current implementation priorities:

1. standards/
2. template system
3. meta-skill system
4. create_tool meta-skill
5. copy_paste tool
6. registry system
7. tool chaining

Permission systems are intentionally postponed until the runtime architecture stabilizes.

---

# Implementation Contracts

The initial repository implementation should convert the philosophy above into
small, inspectable contracts.

New tools should include:

* local `AGENTS.md`
* `SKILL.yaml` metadata
* `tool.py`
* tests
* examples
* registry entry

New skills should include:

* `SKILL.yaml` metadata
* concrete workflow steps
* required inputs and outputs
* validation checks
* registry entry

When adding or modifying capabilities:

* keep public interfaces narrow
* document side effects explicitly
* prefer 1-based line numbers for user-facing text selection APIs
* validate before mutating files
* update registry files when adding discoverable tools or skills
* add tests before considering a tool usable

---

# Design Principles

The ecosystem should aim for:

* modularity
* inspectability
* composability
* low-context execution
* deterministic tooling
* reusable procedural memory
* compatibility with both large and small models

The long-term goal is not merely code generation.

The long-term goal is orchestrated, reusable, inspectable intelligent behavior.
