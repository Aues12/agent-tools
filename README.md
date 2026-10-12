# agent-tools

`agent-tools` is an experimental capability layer for AI agents. Instead of
asking a model to recreate every procedure, it gives the agent bounded tools
for concrete operations and skills for repeatable workflows. The model decides
what to do and supplies parameters; the tools return results that can be
inspected and composed. The design is intended to work across agent frameworks
and model sizes.

## How the system fits together

- **Tools** perform narrow jobs through explicit interfaces. Most Python tools
  accept an `operation` and `params` as JSON and return a structured result.
  They are designed for an agent to select and call, but can also be run by a
  person from the terminal.
- **Skills** describe procedures: inputs, steps, tools to call, outputs, and
  validation. The current [meta-skills](meta-skills/) are drafts.
- **Standards** define the contracts for tools, skills, agents, and schemas;
  the [registries](registry/) make available capabilities discoverable.
- **Runtime** coordination is the architectural direction. This repository
  does not yet contain an implemented orchestration runtime.

This separation keeps reasoning with the agent and repeatable operations in
small, testable components. See [AGENTS.md](AGENTS.md) for the full design.

## A first tool call

From the repository root, this Python 3 command asks `copy_paste` to locate a
heading without changing any files:

```bash
printf '%s' '{"operation":"find_text","params":{"file":"AGENTS.md","text":"Agent-Agnostic Principle"}}' | python3 file-tools/copy_paste/copy_paste.py
```

The response contains `success: true` and a 1-based line and column in
`result`. An agent can use the same request shape after finding the operation
in the [tool registry](registry/tool_registry.json). See
[USE_TOOL.md](USE_TOOL.md) for the shared invocation convention.

## Where to go next

- **Use a capability:** Browse the [tool registry](registry/tool_registry.json),
  then open a tool's local README for parameters and tests. The
  [semantic graph tool](file-tools/semantic_graph/README.md) and its
  [viewer](visual-tools/semantic_graph_viewer/README.md) form one v0.1.0 path.
- **Understand Python code:** Start with [semantic AST](file-tools/semantic_ast/README.md)
  and [semantic cards](file-tools/semantic_cards/README.md); follow
  [CFG](file-tools/semantic_cfg/README.md), [DFG](file-tools/semantic_dfg/README.md),
  or [CPG](file-tools/semantic_cpg/README.md) for different analyses. These
  are separate, tested tools with documented limits.
- **Build a tool or skill:** Read the [standards](standards/) and
  [templates](templates/) before the draft [meta-skills](meta-skills/).
  [Future improvements](FUTURE_IMPROVEMENTS.md) records planned work.
- **Explore research and prototypes:** See the [Observatory pipeline](file-tools/semantic_observatory_pipeline/README.md),
  [experiments](experiments/README.md), [playground](agent-playground/README.md),
  and [memory](memory/README.md). Research notes provide context, not contracts.

The registry currently labels tools `experimental`, including tested ones; it
does not promise cross-version API stability. Before public visibility, Git
history still needs a privacy review, plus licensing, CI, packaging, and test
coverage decisions.
