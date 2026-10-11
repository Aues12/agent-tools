# AGENTS.md — writing_timeline

`writing_timeline` visualizes dated writing nodes and their directed reference
edges. It consumes `semantic_graph` JSON and does not create or repair graph
semantics.

The primary spatial rule is chronological: horizontal position comes from the
node's `attributes.date`. Vertical lanes exist only to prevent collisions.
Reference edges preserve source-to-target direction.

Keep the application independent from `semantic_observatory_ui`. Prefer a
calm, readable timeline with progressive disclosure over a dense generic graph
map. TypeScript is required for source files.
