# Semantic Graph Viewer

A standalone React, TypeScript, and Vite viewer for `semantic_graph` v0.1.0 JSON artifacts. The bundled BookBarcode graph is an example, and any valid graph in the same format can be loaded locally. The viewer does not edit or reinterpret graph records.

Requires Node.js 24 or newer for the TypeScript test runner.

## Run

```bash
cd visual-tools/semantic_graph_viewer
npm ci
npm run dev
```

Open the `http://127.0.0.1:...` URL printed by Vite. Do not open `index.html` as a `file://` URL; browsers cannot run the uncompiled TypeScript entry point that way. Use **Load JSON graph** to inspect another artifact. File contents stay in the browser.

## Validate and build

```bash
npm test
npm run typecheck
npm run build
npm run preview
```

## Input contract

The root object requires `type: "semantic_graph"`, `version: "0.1.0"`, a nonempty `graph_id`, `attributes`, and `nodes` and `edges` arrays. Nodes require positive integer `unique_id`, nonempty `label` and `kind`, and an `attributes` object. Edges require positive integer `unique_id`, valid `source` and `target` node IDs, nonempty `kind`, and an `attributes` object. `title`, `revision`, counters, and edge `label` follow the repository format. Node and edge kinds are open strings.

Validation reports malformed records, duplicate IDs, and missing endpoints. The viewer keeps the original records in memory; search, filters, colors, and layout are derived presentation data. The layered layout condenses cycles before ordering nodes, so cyclic graphs remain navigable. Very large graphs can become visually dense; this first version is aimed at human-scale artifacts.

The default example is the English translation in `public/graphs/bookbarcode_workflow_dag_en.json`. The supplied Turkish source remains in `public/graphs/bookbarcode_workflow_dag.json`. Translation changes the example's title and display labels only; IDs, kinds, attributes, and edge endpoints are preserved. Graphs loaded through **Load JSON graph** display their text exactly as supplied.
