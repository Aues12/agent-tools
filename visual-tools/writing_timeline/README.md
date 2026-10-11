# Writing Timeline

A standalone TypeScript/React Canvas application for exploring dated writing
and the references between posts.

The application consumes a directed `semantic_graph` document. Node dates are
read from `attributes.date`; edges retain their source-to-target direction.

## Run

```bash
npm install
npm run dev
```

The default graph is `public/graphs/book_reference_graph.json`. Another graph
can be opened from the sidebar without changing source files.

## Validate

```bash
npm run typecheck
npm run build
```
