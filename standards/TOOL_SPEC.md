# Tool Specification

## Purpose

A tool is a narrow, reusable capability. It should perform one bounded job with
predictable inputs, outputs, errors, and side effects.

## Required Layout

Each tool directory should contain:

```text
tool_name/
├── AGENTS.md
├── SKILL.yaml
├── tool.py
├── tests/
└── examples/
```

## Required Metadata

`SKILL.yaml` acts as the local discovery metadata until the registry becomes the
primary source of truth. It should include:

* `name`: snake_case tool name.
* `type`: `tool`.
* `capability`: short capability label.
* `purpose`: one sentence describing the tool.
* `interfaces`: exported callable functions.
* `side_effects`: explicit description of reads and writes.
* `status`: `draft`, `experimental`, or `stable`.

## Interface Rules

Tool functions should:

* accept explicit parameters.
* return plain Python values where possible.
* avoid process-global state.
* validate inputs before mutating files.
* raise clear exceptions on invalid use.
* document line-number conventions when applicable.

## Side Effects

Reads and writes must be obvious from the function name and metadata. A function
that modifies files should not also perform unrelated registry, memory, or state
updates unless that behavior is part of its documented contract.

## Testing Expectations

Every tool should have tests for:

* normal behavior.
* invalid input.
* boundary cases.
* file mutation behavior, if any.

Prefer standard-library tests unless a dependency materially improves clarity.
