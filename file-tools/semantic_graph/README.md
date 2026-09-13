# semantic_graph

`semantic_graph` v0.1.0 is a minimal graph-writing workspace for agents. Start
it once, send short commands to the same terminal process, and inspect or save
the graph whenever needed.

The tool deliberately has no DAG, directed-graph, dependency-graph, or domain
model. Its `Graph`, `Node`, and `Edge` classes only maintain identities and
endpoint integrity. Future graph models and profiles remain research topics.

## Terminal session

Start a persistent session from the repository root:

```bash
python3 file-tools/semantic_graph/semantic_graph.py session
```

Then build a graph incrementally:

```text
new --graph-id bookbarcode-flow --title "BookBarcode flow"
add-node --label "ISBN input" --kind input
add-node --label "Validate ISBN" --kind step
add-edge --source 1 --target 2 --kind next
show
show json
save /tmp/bookbarcode-flow.json
exit
```

Typical compact responses are:

```text
ok graph bookbarcode-flow
ok node 1 revision 1
ok node 2 revision 2
ok edge 1 revision 3
graph bookbarcode-flow revision 3 nodes 2 edges 1
```

Node and edge IDs have separate graph-local counters. Both start at `1` and are
assigned by the tool.

## JSON parameter packets

Longer or reusable arguments may be stored in a JSON object:

```json
{
  "label": "ISBN input",
  "kind": "input",
  "attributes": {"format": "ISBN-13"}
}
```

Pass the packet without embedding JSON in the shell command:

```text
add-node @file-tools/semantic_graph/examples/add_isbn_node.json
```

An edge packet uses `source`, `target`, and optional `kind`, `label`, and
`attributes` fields.

## General model behavior

The base graph accepts cycles, self-loops, and parallel edges. It does not infer
semantics or decide whether endpoint order means direction. Only these core
invariants are enforced:

* `graph_id` is non-empty;
* node and edge identities are positive and unique in their own namespaces;
* an edge references two existing nodes;
* counters never move backwards.

## Python and stdin JSON interfaces

The model classes are available from `model.py`. `tool.run()` additionally
supports the stateless operations `create_graph`, `add_node`, and `add_edge` for
runtime integrations. Each mutation returns the complete updated graph.

## Validation

```bash
python3 -m unittest discover -s file-tools/semantic_graph/tests -v
```

Research notes and the prospective graph-model taxonomy live in
[`research/`](research/README.md).
