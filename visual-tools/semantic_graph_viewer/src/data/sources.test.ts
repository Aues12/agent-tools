import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { parseSemanticGraph } from "./graph.ts";
import { sourcesForNode } from "./sources.ts";

test("study card URL sources become distinct linked cards", () => {
  const graph = parseSemanticGraph(JSON.parse(readFileSync(new URL("../../public/graphs/working_memory_study_demo.json", import.meta.url), "utf8")));
  const sources = sourcesForNode(graph, graph.nodes[0]);
  assert.ok(sources.length > 0);
  assert.equal(sources[0].kind, "online");
  assert.match(sources[0].href ?? "", /^https:\/\//);
});

test("catalog references keep file paths, interpretations and unresolved IDs distinct", () => {
  const graph = parseSemanticGraph(JSON.parse(readFileSync(new URL("../../../../skills/notes_to_semantic_graph/examples/example_graph.json", import.meta.url), "utf8")));
  graph.nodes[0].attributes.source_refs = [{ source_id: "note_1" }, { source_id: "interpretation_1" }, { source_id: "missing" }];
  const sources = sourcesForNode(graph, graph.nodes[0]);
  assert.deepEqual(sources.map((source) => source.sourceId), ["note_1", "interpretation_1", "missing"]);
  assert.equal(sources[0].detail, "lecture_notes.md");
  assert.equal(sources[0].href, undefined);
  assert.equal(sources[1].interpretation, true);
  assert.equal(sources[2].kind, "unknown");
});

test("catalog URL sources only link to HTTP(S), with duplicate card URLs removed", () => {
  const graph = parseSemanticGraph(JSON.parse(readFileSync(new URL("../../public/graphs/working_memory_study_demo.json", import.meta.url), "utf8")));
  const url = (graph.nodes[0].attributes.card as { sources: { url: string }[] }).sources[0].url;
  graph.attributes.sources = [
    { id: "online_1", type: "online", label: "Catalog source", url },
    { id: "unsafe_1", type: "online", label: "Unsafe URL", url: "javascript:alert(1)" },
  ];
  graph.nodes[0].attributes.source_refs = [{ source_id: "online_1" }, { source_id: "unsafe_1" }];
  const sources = sourcesForNode(graph, graph.nodes[0]);
  assert.equal(sources.filter((source) => source.href === url).length, 1);
  assert.equal(sources.find((source) => source.sourceId === "unsafe_1")?.href, undefined);
});
