import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { adaptGraph, matchingNodeIds, parseSemanticGraph } from "./graph.ts";
import { layoutGraph } from "./layout.ts";

const example = parseSemanticGraph(JSON.parse(readFileSync(new URL("../../public/graphs/bookbarcode_workflow_dag.json", import.meta.url), "utf8")));
const englishExample = parseSemanticGraph(JSON.parse(readFileSync(new URL("../../public/graphs/bookbarcode_workflow_dag_en.json", import.meta.url), "utf8")));

test("English example translates display text while preserving graph structure", () => {
  assert.equal(englishExample.nodes.length, 29);
  assert.equal(englishExample.edges.length, 38);
  assert.deepEqual(englishExample.nodes.map(({ unique_id, kind, attributes }) => ({ unique_id, kind, attributes })), example.nodes.map(({ unique_id, kind, attributes }) => ({ unique_id, kind, attributes })));
  assert.deepEqual(englishExample.edges.map(({ unique_id, source, target, kind, attributes }) => ({ unique_id, source, target, kind, attributes })), example.edges.map(({ unique_id, source, target, kind, attributes }) => ({ unique_id, source, target, kind, attributes })));
  assert.equal(englishExample.graph_id, example.graph_id);
});

test("example preserves all records and directed endpoints", () => {
  assert.equal(example.nodes.length, 29);
  assert.equal(example.edges.length, 38);
  assert.deepEqual(example.nodes.map((node) => node.unique_id), Array.from({ length: 29 }, (_, index) => index + 1));
  assert.deepEqual(example.edges.map((edge) => [edge.source, edge.target]), JSON.parse(readFileSync(new URL("../../public/graphs/bookbarcode_workflow_dag.json", import.meta.url), "utf8")).edges.map((edge: { source: number; target: number }) => [edge.source, edge.target]));
  const view = adaptGraph(example);
  assert.equal(view.outgoing.get(1)?.[0].target, 2);
  assert.equal(view.incoming.get(2)?.[0].source, 1);
  assert.equal(layoutGraph(example).positions.size, 29);
});

test("open kinds and non-DAG graphs remain valid", () => {
  const graph = parseSemanticGraph({ type: "semantic_graph", version: "0.1.0", graph_id: "cycle", attributes: {}, nodes: [
    { unique_id: 1, label: "One", kind: "new kind", attributes: {} },
    { unique_id: 2, label: "Two", kind: "another kind", attributes: {} }
  ], edges: [
    { unique_id: 1, source: 1, target: 2, kind: "novel relation", attributes: {} },
    { unique_id: 2, source: 2, target: 1, kind: "reverse", attributes: {} }
  ] });
  assert.deepEqual(adaptGraph(graph).kinds.map((entry) => entry.kind), ["another kind", "new kind"]);
  assert.equal(layoutGraph(graph).cyclic, true);
  assert.notDeepEqual(layoutGraph(graph).positions.get(1), layoutGraph(graph).positions.get(2));
});

test("filtering does not mutate source graph", () => {
  const before = JSON.stringify(example);
  assert.equal(matchingNodeIds(example, "layout", "layout").size > 0, true);
  assert.equal(matchingNodeIds(example, "", null).size, 29);
  assert.equal(JSON.stringify(example), before);
});

test("invalid input produces actionable errors", () => {
  assert.throws(() => parseSemanticGraph({ ...example, version: "2.0.0" }), /version 0\.1\.0/);
  assert.throws(() => parseSemanticGraph({ ...example, nodes: [...example.nodes, example.nodes[0]] }), /Duplicate node unique_id 1/);
  assert.throws(() => parseSemanticGraph({ ...example, edges: [{ ...example.edges[0], target: 999 }] }), /references a missing node/);
  assert.throws(() => parseSemanticGraph({ ...example, nodes: [{ ...example.nodes[0], attributes: [] }] }), /attributes must be a JSON object/);
});
