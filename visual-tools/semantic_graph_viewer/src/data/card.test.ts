import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { cardForNode, parseCardContent } from "./card.ts";
import { adaptGraph, parseSemanticGraph } from "./graph.ts";

test("study example is a semantic_graph with cards and directed connections", () => {
  const graph = parseSemanticGraph(JSON.parse(readFileSync(new URL("../../public/graphs/working_memory_study_demo.json", import.meta.url), "utf8")));
  const view = adaptGraph(graph);
  assert.equal(graph.nodes.length, 4);
  assert.equal(view.kinds.length, 3);
  assert.equal(cardForNode(view.byId.get(4)!)?.sections.length, 2);
  assert.deepEqual(view.incoming.get(4)?.map((edge) => edge.source), [1, 3]);
});

test("optional card content is validated without requiring a card on every node", () => {
  assert.equal(parseCardContent(undefined, "card"), null);
  assert.throws(() => parseCardContent({ summary: "" }, "card"), /card.summary/);
  assert.throws(() => parseCardContent({ sections: [{ heading: "Only a heading" }] }, "card"), /card.sections\[0\]/);
  assert.throws(() => parseCardContent({ sources: [{ label: "Unsafe", url: "javascript:alert(1)" }] }, "card"), /HTTP\(S\)/);
  const graph = JSON.parse(readFileSync(new URL("../../public/graphs/working_memory_study_demo.json", import.meta.url), "utf8"));
  graph.nodes[0].attributes.card.summary = "";
  assert.throws(() => parseSemanticGraph(graph), /nodes\[0\]\.attributes\.card\.summary/);
});
