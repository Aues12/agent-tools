# Future Improvements

This file is the canonical place for future work, roadmap items, deferred
architecture, and long-term improvement ideas.

---

# Repository Priorities

Current implementation priorities:

1. `standards/`
2. template system
3. meta-skill system
4. `create_tool` / `create_skill` execution workflows
5. registry maturity
6. tool chaining and orchestration

Permission systems remain intentionally postponed until runtime contracts
stabilize.

---

# Architecture Direction

## Runtime

The runtime is expected to become the orchestration kernel for skills, tools,
state, and memory.

Expected responsibilities:

* skill execution
* tool dispatching
* executor management
* task lifecycle handling
* event processing
* state updates through a central path

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

Planned components:

* `engine.py`: receive goals/tasks, request plans from the planner, coordinate
  execution, and return results.
* `planner.py`: generate ordered execution plans from user goals or task
  descriptions. It may start with simple rule-based logic and later evolve into
  an LLM-assisted planner.
* `executor.py`: load tools, execute tool interfaces, collect results, and
  handle execution errors without containing planning logic.

Long-term runtime goals:

* workflow orchestration
* autonomous execution
* memory-aware planning
* multi-step reasoning pipelines
* stateful orchestration
* registry-backed discoverability
* execution history
* permission systems
* multi-model coordination

## Registry

The registry should mature into the capability map for tools, skills,
executors, metadata, and versions.

Possible structure:

```text
registry/
├── tool_registry.json
├── skill_registry.json
├── executor_registry.json
└── loader.py
```

`loader.py` can become the single access layer for validation, discovery, and
version handling.

## Memory

Memory should store longer-lived information separately from runtime state.

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

* procedural memory: reusable know-how about how work is performed

## State

State should represent current runtime conditions.

Examples:

* active project, branch, or task
* active skill
* recent tool usage
* last modified files

Preferred direction:

* event-driven state updates from tool and runtime events

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
* local model runtimes

---

# Meta-Skills

Long-term expectation:

* meta-skills become executable pipelines, not only documentation.

---

# Selection and Locator Tools

A key design target is reducing manual line-number reasoning.

Instead of selecting text by fragile offsets, prefer semantic
locators/selectors that narrow targets before mutation.

Future semantic selection should live in a locator tool such as `find_block`.

This improves:

* reliability
* determinism
* token efficiency
* small-model usability

---

# Semantic AST Improvements

## Compression

Possible future extensions:

* repository memory generation
* semantic embeddings
* dependency summarization
* call graph compression
* semantic chunking
* retrieval-oriented indexing
* multi-resolution AST views

The long-term goal is compact semantic representations optimized for
intelligent systems.

## Call Graph

Possible future extensions:

* repository-wide dependency graphs
* circular dependency detection
* dead code discovery
* graph visualization
* semantic repository maps
* centrality analysis
* execution path tracing
* multi-file flow analysis

The long-term goal is making large codebases understandable through semantic
structure.
