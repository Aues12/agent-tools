import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { parseSemanticGraph } from "./graph.ts";
import { graphFingerprint, restoreSession, saveGraph, saveView, type SavedView, type SessionStorage } from "./session.ts";

const example = parseSemanticGraph(JSON.parse(readFileSync(new URL("../../public/graphs/bookbarcode_workflow_dag_en.json", import.meta.url), "utf8")));
const study = parseSemanticGraph(JSON.parse(readFileSync(new URL("../../public/graphs/working_memory_study_demo.json", import.meta.url), "utf8")));

function memoryStorage(): SessionStorage {
  const data = new Map<string, string>();
  return { getItem: (key) => data.get(key) ?? null, setItem: (key, value) => { data.set(key, value); } };
}

test("loaded graph and study position survive a session restore", () => {
  const storage = memoryStorage();
  const view: SavedView = {
    profile: "study", indexOpen: false, inspectorOpen: true, query: "memory", kind: study.nodes[0].kind,
    selectedId: study.nodes[0].unique_id, studyCardId: study.nodes[0].unique_id,
    viewport: { x: 150, y: -20, width: 900, height: 600, canvasWidth: 1200, canvasHeight: 800 },
  };
  assert.equal(saveGraph(storage, study, "lecture.json"), true);
  assert.equal(saveView(storage, graphFingerprint(study), view), true);
  assert.deepEqual(restoreSession(storage, example, "default"), { graph: study, fileName: "lecture.json", ...view });
});

test("view state is ignored after a different graph is loaded", () => {
  const storage = memoryStorage();
  saveView(storage, graphFingerprint(study), {
    profile: "study", indexOpen: false, inspectorOpen: false, query: "old", kind: null,
    selectedId: study.nodes[0].unique_id, studyCardId: study.nodes[0].unique_id, viewport: null,
  });
  const restored = restoreSession(storage, example, "default");
  assert.equal(restored.graph, example);
  assert.equal(restored.selectedId, null);
  assert.equal(restored.query, "");
  assert.equal(restored.profile, "classic");
});

test("invalid or unavailable browser storage falls back to the bundled graph", () => {
  const storage: SessionStorage = {
    getItem: () => "{invalid json",
    setItem: () => { throw new Error("QuotaExceededError"); },
  };
  assert.equal(restoreSession(storage, example, "default").graph, example);
  assert.equal(saveGraph(storage, study, "lecture.json"), false);
  assert.equal(saveView(null, graphFingerprint(study), {
    profile: "classic", indexOpen: true, inspectorOpen: true, query: "", kind: null,
    selectedId: null, studyCardId: null, viewport: null,
  }), false);
});
