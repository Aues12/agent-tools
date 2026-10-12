# agent-tools

`agent-tools` explores a reusable capability layer for AI agents. The idea is
simple: let a model reason about a task, call a bounded tool for a concrete
operation, and use a skill when the same workflow is worth repeating. Tools
should have inspectable inputs, outputs, and side effects so the approach can
work with different agent frameworks and model sizes.

Today, the repository contains independently runnable Python tools, a graph
viewer, contracts, and research notes. It is a development environment, not a
single finished application. The proposed orchestration runtime is documented
but not implemented here; the meta-skills are drafts.

## Try a tool

From the repository root, create a small graph with the `semantic_graph`
terminal interface. Python 3 is required; this example needs no install step.

```bash
python3 file-tools/semantic_graph/semantic_graph.py session <<'GRAPH'
new --graph-id hello
add-node --label Question
add-node --label Answer
add-edge --source 1 --target 2 --kind relates_to
show
exit
GRAPH
```

The last line should be `graph hello revision 3 nodes 2 edges 1`. The tool
assigns node and edge IDs and can save the result as JSON. Its
[README](file-tools/semantic_graph/README.md) explains the full command set;
the [semantic graph viewer](visual-tools/semantic_graph_viewer/README.md) can
open saved v0.1.0 graphs and includes a bundled example.

## Choose a reading path

- **I want to understand the design.** Start with [AGENTS.md](AGENTS.md) for
  the architecture and repository contracts, then [standards/](standards/) for
  formal specifications. [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md)
  records planned work.
- **I want to call a tool.** Use [USE_TOOL.md](USE_TOOL.md) for the request and
  response convention, then the [tool registry](registry/tool_registry.json)
  to find an operation and its entrypoint. Follow the tool's local README for
  parameters and validation.
- **I want to analyze Python code.** Begin with
  [semantic AST](file-tools/semantic_ast/README.md) for structure and
  [semantic cards](file-tools/semantic_cards/README.md) for navigable units.
  For local control and data flow, see [CFG](file-tools/semantic_cfg/README.md),
  [DFG](file-tools/semantic_dfg/README.md), and
  [CPG](file-tools/semantic_cpg/README.md). These are separate, tested tools
  with documented limits, not one required pipeline.
- **I want to explore a UI or an earlier idea.** See the
  [Semantic Observatory pipeline](file-tools/semantic_observatory_pipeline/README.md)
  and [UI prototype](file-tools/semantic_observatory_ui/AGENTS.md). The
  [experiments](experiments/README.md) area holds older applications with
  different input contracts; [agent-playground](agent-playground/README.md)
  holds small examples and archived analyses.
- **I want to add a capability.** Read the [tool](standards/TOOL_SPEC.md) or
  [skill](standards/SKILL_SPEC.md) contract, then the
  [templates](templates/) and [draft meta-skills](meta-skills/). The
  [skill registry](registry/skill_registry.json) records their current status.

The [memory](memory/README.md) and
[semantic graph research](file-tools/semantic_graph/research/README.md) areas
provide design context. They are not implementation contracts. The registry
currently marks tools as `experimental`, including `semantic_graph`; this is a
release-status label, not a claim that their tested operations are unreliable.
No cross-version API stability promise has been declared.

## Publication status

This repository is being prepared for public visibility. Earlier Git commits
still contain generated artifacts and machine-specific paths, so history needs
review before the source repository is made public. A license, CI, packaging
review, and a test-coverage gate are also future publication work.
