# agent-tools

`agent-tools` is an experimental repository of independent tools with shared,
agent-compatible contracts. Instead of recreating each procedure from scratch,
an agent can select a bounded tool, supply its parameters, and inspect the
result. Skills describe workflows worth repeating. The tools also remain usable
on their own, across agent frameworks and model sizes.

Current tools cover text and file operations, Python code analysis, graph
authoring, manuscript audits, plan validation, and guarded DOCX assembly. The
repository also includes a graph viewer, specifications, examples, and research
notes. These are separate capabilities, not one finished application.

The repository root is a development workspace, not an installable aggregate
Python package. Use each tool through its documented interface.

## How the system fits together

- **Tools** perform narrow jobs through explicit interfaces. Most accept an
  `operation` and `params` as JSON and return a structured result. They are
  designed for agents to call and remain usable from a terminal.
- **Skills** describe procedures: inputs, steps, tools, outputs, and validation.
  The current [meta-skills](meta-skills/) are drafts.
- **Standards** define contracts; [registries](registry/) make capabilities
  discoverable. An agent or external runtime can use these interfaces; this
  repository does not provide an execution runtime.

See [AGENTS.md](AGENTS.md) for the architecture and [USE_TOOL.md](USE_TOOL.md)
for the invocation contract.

## A first tool call

From the repository root, this Python 3.11+ command finds a heading without
changing any files:

```bash
printf '%s' '{"operation":"find_text","params":{"file":"AGENTS.md","text":"Agent-Agnostic Principle"}}' | python3 file-tools/copy_paste/copy_paste.py
```

The JSON response contains `success: true` and a 1-based line and column in
`result`. The [tool registry](registry/tool_registry.json) lists other
operations and entrypoints; each tool's documentation supplies its parameters
and limits.

## Tools at a glance

These are the registered capabilities. The indented AST tools can also be
called through `semantic_ast`; the manuscript tools share the
[`book-editing-tools` guide](book-editing-tools/README.md).

| Tool | What it does |
| --- | --- |
| [copy_paste](file-tools/copy_paste/README.md) | Reads, finds, extracts, and inserts text. |
| [rename_files](file-tools/rename_files/README.md) | Plans or applies filename changes. |
| [ast_dump](file-tools/ast_dump/README.md) | Produces Python's native AST dump. |
| [isbn_barcode](file-tools/isbn_barcode/README.md) | Generates and verifies ISBN-13 barcodes. |
| [semantic_graph](file-tools/semantic_graph/README.md) | Builds and saves general graphs. |
| [semantic_ast](file-tools/semantic_ast/README.md) | Dispatches Python parsing, compression, and call graphs. |
| ↳ [ast_parsing](file-tools/semantic_ast/ast_parsing/README.md) | Parses Python into a semantic AST. |
| ↳ [compression](file-tools/semantic_ast/compression/README.md) | Reduces semantic AST detail. |
| ↳ [call_graph](file-tools/semantic_ast/call_graph/README.md) | Extracts local function-call relations. |
| [semantic_cards](file-tools/semantic_cards/README.md) | Builds navigable code cards and relations. |
| [semantic_cfg](file-tools/semantic_cfg/README.md) | Builds local control-flow graphs. |
| [semantic_dfg](file-tools/semantic_dfg/README.md) | Builds local data-flow graphs. |
| [semantic_cpg](file-tools/semantic_cpg/README.md) | Merges AST, control, data, and call graphs. |
| [semantic_observatory_pipeline](file-tools/semantic_observatory_pipeline/README.md) | Prepares analysis artifacts and UI data. |
| [book-editing-tools](book-editing-tools/README.md) | Groups manuscript audits, plan validation, and guarded DOCX assembly. |
| ↳ [manuscript_inventory](book-editing-tools/manuscript_inventory/SKILL.yaml) | Inventories articles, dates, and order. |
| ↳ [index_audit](book-editing-tools/index_audit/SKILL.yaml) | Checks article coverage in an index. |
| ↳ [chronology_audit](book-editing-tools/chronology_audit/SKILL.yaml) | Finds out-of-order and undated articles. |
| ↳ [overlap_audit](book-editing-tools/overlap_audit/SKILL.yaml) | Finds matching titles across manuscripts. |
| ↳ [edition_diff](book-editing-tools/edition_diff/SKILL.yaml) | Flags added, removed, moved, and changed articles. |
| ↳ [ebook_preflight](book-editing-tools/ebook_preflight/SKILL.yaml) | Flags DOCX layout and image candidates for review. |
| ↳ [chapter_plan](book-editing-tools/chapter_plan/SKILL.yaml) | Validates complete chronological plans, with or without parts. |
| ↳ [docx_assemble](book-editing-tools/docx_assemble/SKILL.yaml) | Previews and creates a new DOCX from a validated plan. |

## Where to go next

- **Use or extend a tool:** Follow its README, then the relevant
  [tool](standards/TOOL_SPEC.md) or [skill](standards/SKILL_SPEC.md) contract and
  [templates](templates/). [Future improvements](FUTURE_IMPROVEMENTS.md)
  records planned work.
- **Work with code or graphs:** See [semantic AST](file-tools/semantic_ast/README.md),
  [semantic cards](file-tools/semantic_cards/README.md), and the distinct
  [CFG](file-tools/semantic_cfg/README.md), [DFG](file-tools/semantic_dfg/README.md),
  and [CPG](file-tools/semantic_cpg/README.md) analyses. The
  [semantic graph viewer](visual-tools/semantic_graph_viewer/README.md) opens
  v0.1.0 graphs from [semantic_graph](file-tools/semantic_graph/README.md).
- **Audit a manuscript:** Start with the [book-editing guide](book-editing-tools/README.md).
  Its tools report evidence and uncertainty; editorial decisions remain with
  the user or agent.
- **Explore context:** [Experiments](experiments/README.md),
  [playground](agent-playground/README.md), and [memory](memory/README.md)
  record prototypes, examples, and research. For documentation work, see the
  [documentation principles](memory/procedural/DOCUMENTATION_PRINCIPLES.md).

The registry labels tools `experimental`, including tested ones; it does not
promise cross-version API stability.

The repository is licensed under the [MIT License](LICENSE).
