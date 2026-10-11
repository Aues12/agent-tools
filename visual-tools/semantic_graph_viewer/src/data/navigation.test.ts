import test from "node:test";
import assert from "node:assert/strict";
import { nextNodeId } from "./navigation.ts";

const positions = new Map([
  [1, { x: 0, y: 0 }],
  [2, { x: 300, y: 0 }],
  [3, { x: 300, y: 120 }],
  [4, { x: 600, y: 0 }],
]);
const all = new Set(positions.keys());

test("arrow keys select the nearest node in each visual direction", () => {
  assert.equal(nextNodeId(positions, all, 1, "ArrowRight", { x: 0, y: 0 }), 2);
  assert.equal(nextNodeId(positions, all, 2, "ArrowLeft", { x: 0, y: 0 }), 1);
  assert.equal(nextNodeId(positions, all, 2, "ArrowDown", { x: 0, y: 0 }), 3);
  assert.equal(nextNodeId(positions, all, 3, "ArrowUp", { x: 0, y: 0 }), 2);
  assert.equal(nextNodeId(positions, all, 4, "ArrowRight", { x: 0, y: 0 }), null);
});

test("first arrow selects near the viewport center and filters limit candidates", () => {
  assert.equal(nextNodeId(positions, all, null, "ArrowRight", { x: 290, y: 5 }), 2);
  const filtered = new Set([1, 3]);
  assert.equal(nextNodeId(positions, filtered, 1, "ArrowRight", { x: 0, y: 0 }), 3);
  assert.equal(nextNodeId(positions, new Set(), 1, "ArrowRight", { x: 0, y: 0 }), null);
});
