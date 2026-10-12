# agent-tools

`agent-tools` is a collection of reusable capabilities for AI agents. Models
handle reasoning; small tools perform bounded operations; skills describe
workflows worth repeating. The aim is an inspectable, agent-agnostic layer that
can work with different models and runtimes.

This repository currently contains standalone Python tools and a graph viewer.
The orchestration runtime is planned, and the meta-skills are drafts.

## Try it

From the repository root, use Python 3 to create a graph:

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

The final line is `graph hello revision 3 nodes 2 edges 1`. See the
[graph tool](file-tools/semantic_graph/README.md) for saving JSON and the
[viewer](visual-tools/semantic_graph_viewer/README.md) for opening it.

## Find your way

- **Use a tool:** [Usage contract](USE_TOOL.md) → [tool registry](registry/tool_registry.json) → the tool's README.
- **Analyze Python:** [AST](file-tools/semantic_ast/README.md), [cards](file-tools/semantic_cards/README.md), [CFG](file-tools/semantic_cfg/README.md), [DFG](file-tools/semantic_dfg/README.md), and [CPG](file-tools/semantic_cpg/README.md) are separate, tested tools. The [Observatory pipeline](file-tools/semantic_observatory_pipeline/README.md) and [UI prototype](file-tools/semantic_observatory_ui/AGENTS.md) explore their presentation.
- **Understand or extend the project:** Start with [AGENTS.md](AGENTS.md), then consult the [standards](standards/) and [templates](templates/). [Future improvements](FUTURE_IMPROVEMENTS.md) records planned work.
- **Explore earlier ideas:** [Experiments](experiments/README.md), [playground](agent-playground/README.md), and [research notes](file-tools/semantic_graph/research/README.md) provide context, not implementation contracts.

Registry status is currently `experimental`, including for tested tools; no
cross-version API stability is promised. Before public release, the source
repository's Git history still needs a privacy review, plus licensing, CI,
packaging, and test-coverage decisions.
