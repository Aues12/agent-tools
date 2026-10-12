# agent-tools

An experimental, agent-agnostic collection of bounded tools, reusable skill
workflows, and runtime prototypes. This repository is not a single integrated
semantic-analysis product.

## v0.1 path

The clearest current end-to-end path is [`semantic_graph`](file-tools/semantic_graph/README.md)
and its compatible [`semantic_graph_viewer`](visual-tools/semantic_graph_viewer/README.md).
The Python tool authors a persistent v0.1.0 graph; the standalone viewer loads
that format. Try the tool's terminal session and the viewer's bundled example
using the commands in their READMEs.

## Repository map

| Area | State | Purpose |
| --- | --- | --- |
| [`file-tools/semantic_graph/`](file-tools/semantic_graph/) | v0.1 | Persistent graph authoring and JSON contract |
| [`visual-tools/semantic_graph_viewer/`](visual-tools/semantic_graph_viewer/) | v0.1 companion | Viewer for that contract |
| [`semantic_ast/`](file-tools/semantic_ast/), [`semantic_cards/`](file-tools/semantic_cards/), [`semantic_cfg/`](file-tools/semantic_cfg/), [`semantic_dfg/`](file-tools/semantic_dfg/), [`semantic_cpg/`](file-tools/semantic_cpg/) | Experimental | Separate code-analysis tools with distinct outputs |
| [`semantic_observatory_pipeline/`](file-tools/semantic_observatory_pipeline/), [`semantic_observatory_ui/`](file-tools/semantic_observatory_ui/) | Experimental | Observatory pipeline and UI prototype |
| [`file-tools/`](file-tools/) | Mixed | Other bounded tools, including copy/paste, rename, AST dump, and ISBN barcode |
| [`experiments/`](experiments/) | Legacy experiments | Earlier schema-specific applications; not v0.1 examples |
| [`agent-playground/`](agent-playground/) | Examples and archive | Small fixtures and historical analysis notes |
| [`memory/`](memory/), [`semantic_graph/research/`](file-tools/semantic_graph/research/) | Research | Design and project notes; not implementation contracts |
| [`registry/`](registry/), [`standards/`](standards/), [`templates/`](templates/), [`meta-skills/`](meta-skills/), [`runtime/`](runtime/) | Infrastructure and drafts | Discovery, contracts, templates, skill drafts, runtime work |

Start with [AGENTS.md](AGENTS.md) for architecture, [USE_TOOL.md](USE_TOOL.md)
for invocation, and [registry/tool_registry.json](registry/tool_registry.json)
for the actual tool interfaces and status. Run each area independently as its
README describes. Research notes and older generated analyses are informative,
not evidence that the corresponding features are implemented.

## Before public visibility

The current working tree has been cleaned, but Git history still contains older
generated artifacts and machine-specific paths. Review and, where necessary,
rewrite the **source** repository's history before making it public. The
private `agent-tools-dev` copy preserves the pre-cleanup history.

Other publication work remains: choose a license, add CI, review packaging,
and define a test-coverage gate. These are outside this cleanup.
