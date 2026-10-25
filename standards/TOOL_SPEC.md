# Tool Specification

## Purpose

A tool is a narrow, reusable capability. It should perform one bounded job with
predictable inputs, outputs, errors, and side effects.

## Tool Layout

Each tool directory should contain:

```text
tool_name/
├── AGENTS.md
├── SKILL.yaml
├── tool.py             # default entrypoint name
├── tests/
└── examples/
```

`tool.py` is the default for new tools, not a required filename. An existing
tool may use another entrypoint (including a parent dispatcher) when each
interface declares that path in `SKILL.yaml` and the file exists. Do not add a
second wrapper solely to satisfy the default layout.

## Required Metadata

`SKILL.yaml` acts as the local discovery metadata until the registry becomes the
primary source of truth. It should include:

* `name`: snake_case tool name.
* `type`: `tool`.
* `capability`: short capability label.
* `purpose`: one sentence describing the tool.
* `interfaces`: access surfaces such as `stdin_json` or `python_api`.
* `operations`: bounded actions available through one or more interfaces.
* `side_effects`: explicit description of reads and writes.
* `status`: `draft`, `experimental`, or `stable`.

An optional `search_terms` list may contain short, factual aliases or common
task vocabulary to improve lexical discovery. It does not declare that a tool
is suitable for every task containing those words.

## Interface and Operation Model

Tools should distinguish access surfaces from executable actions.

An `interface` answers:

```text
How can a runtime or agent access this tool?
```

Examples:

```yaml
interfaces:
  - name: stdin_json
    entrypoint: semantic_cards.py
    transport: stdin_json
  - name: python_api
    entrypoint: tool.py
    callables:
      - cards_from_file
      - cards_from_source
      - build_cards
      - run
```

An `operation` answers:

```text
What bounded action can the tool perform?
```

Examples:

```yaml
operations:
  - name: cards_from_file
    available_via:
      - stdin_json
      - python_api
    params:
      path:
        type: string
        required: true
      encoding:
        type: string
        required: false
        default: utf-8
      include_statements:
        type: boolean
        required: false
        default: true
    returns:
      type: object
      description: Semantic cards result.
```

This separation keeps invocation unambiguous:

```text
interface = how to call
operation = what to do
params = operation inputs
returns = operation output
```

Do not use `interfaces` as a plain list of function or operation names.
Function names belong under `python_api.callables`; action names belong under
`operations`.

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
