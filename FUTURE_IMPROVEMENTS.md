# Future Improvements

This file is the canonical place for future work, roadmap items, deferred
architecture, and long-term improvement ideas.

---

# Repository Priorities

Current priorities are to make independently usable tools easier to understand,
integrate, and validate:

1. Clarify and apply the contracts in `standards/` across existing tools.
2. Improve tool documentation, examples, and verification.
3. Mature registry metadata and discovery for tools and skills.
4. Improve templates and the draft `create_tool` / `create_skill` workflows.
5. Explore chaining or host integrations only where a concrete use case needs
   them.

Permission policies for agent hosts remain deferred. They should not be a
prerequisite for running a standalone tool.

---

# Architecture Direction

## Optional host integration

There is no executable runtime in this repository. An agent or host can call
tools through their documented interfaces without adopting a project-specific
runtime. A future adapter could use registry metadata for discovery and tool
invocation, or coordinate a documented skill workflow. Such an adapter should
remain optional and keep tool behavior in the tools themselves.

Ideas such as planning, task queues, event processing, execution history,
permission policy, memory-aware workflows, and multi-model coordination belong
to possible host integrations. They are not commitments or requirements of the
current tool layer. Start with a concrete integration need before defining an
engine or executor architecture.

## Registry

The registry should mature as a discoverable map for independent tools, skills,
their interfaces, metadata, and versions. Executor metadata is optional future
work.

Possible structure:

```text
registry/
├── tool_registry.json
├── skill_registry.json
├── executor_registry.json
└── loader.py
```

The existing `loader.py` can be extended for validation, discovery, and version
handling where a caller needs those functions.

## Memory

Repository memory stores longer-lived project information. Host-specific memory
and execution state, if added later, should be kept separate from tool logic.

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

An integrating host may need transient execution state.

Examples:

* active project, branch, or task
* active skill
* recent tool usage
* last modified files

One possible host design is event-driven state updates from tool calls.

Example event:

```json
{
  "event": "file_modified",
  "file": "app.py"
}
```

## Executors and Model Coordination

Potential host adapters or executor families, if a concrete integration needs
them:

* Python
* Bash
* Git
* Codex
* local model runtimes

---

# Meta-Skills

The current meta-skills are drafts. A future workflow runner could make some of
them executable without making a central runtime mandatory for tools.

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
