# Writing Timeline (legacy experiment)

A standalone TypeScript/React Canvas application for exploring dated writing
and the references between posts.

The application consumes an older directed graph format with string node IDs.
It is **not compatible** with the v0.1.0 `semantic_graph` tool or its viewer.
Node dates are read from `attributes.date`; edges retain their source-to-target
direction. No schema conversion is provided.

## Run

```bash
cd experiments/writing_timeline
npm ci
npm run dev
```

The default `public/graphs/book_reference_graph.json` is a small synthetic
example. Another legacy-format graph can be opened from the sidebar. The
original large book graph and its obsolete generator were removed from the
working tree; the generator called a `build_graph` API that no longer exists.
Their exact history remains in the private `agent-tools-dev` copy.

## Validate

```bash
npm run typecheck
npm run build
```
