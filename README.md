# agent-tools

`agent-tools` is an experimental development environment for building reusable
capabilities for agents.

The repository separates three concerns:

* `tools`: deterministic, bounded capabilities
* `skills`: reusable workflows that orchestrate tools
* `runtime`: execution and coordination layers above those capabilities

The goal is to help LLMs focus on reasoning, planning, and parameter generation
instead of rewriting the same procedures from scratch.

## Mental Model

The intended flow is:

```text
LLM
  -> Planner / Agent
  -> Skills or Tools
  -> Execution Runtime
```

This repository is designed to stay:

* modular
* inspectable
* composable
* agent-agnostic

## Repository Map

```text
agent-tools/
├── file-tools/        # deterministic tool implementations
├── meta-skills/       # skills that create or maintain ecosystem assets
├── runtime/           # orchestration runtime
├── registry/          # discoverable tool and skill metadata
├── memory/            # long-lived conceptual and project memory
├── standards/         # formal specs and contracts
├── templates/         # starter templates for tools and skills
├── agent-playground/  # analysis outputs and experiment artifacts
└── test-data/         # test fixtures
```

## Where To Start

If you are onboarding into the repo, read in this order:

1. [AGENTS.md](./AGENTS.md)
2. [USE_TOOL.md](./USE_TOOL.md)
3. [registry/tool_registry.json](./registry/tool_registry.json)
4. [FUTURE_IMPROVEMENTS.md](./FUTURE_IMPROVEMENTS.md)
5. [standards/](./standards/)

## Key Areas

### Tools

Tools are small, deterministic capabilities.

They usually expose a shared CLI contract:

* input: JSON from `stdin`
* output: JSON to `stdout`

See [USE_TOOL.md](./USE_TOOL.md).

### Registry

The registry is the capability map for tools and skills.

Start here when you want to discover what already exists:

* [registry/tool_registry.json](./registry/tool_registry.json)
* [registry/skill_registry.json](./registry/skill_registry.json)

### Memory

The `memory/` directory stores long-lived context that should survive across
sessions.

Important current areas:

* [memory/semantic_observatory/](./memory/semantic_observatory/): the
  repository's conceptual notebook and the philosophical and ontological-epistemic framing.
* [memory/project_memory/](./memory/project_memory/): the repository's
  development memory, preserving architectural decisions, milestone history,
  and the chronology of how the system evolves.

### Standards

Formal repository contracts live in [standards/](./standards/).

These define expectations for tools, skills, agents, interfaces, and schemas.

## Guiding Principle

Build reusable, inspectable intelligent behavior.
