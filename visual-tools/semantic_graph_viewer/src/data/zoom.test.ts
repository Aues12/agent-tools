import assert from "node:assert/strict";
import test from "node:test";
import { wheelZoomFactor } from "./zoom.ts";

test("small touchpad movements zoom proportionally and reverse symmetrically", () => {
  const outward = wheelZoomFactor(5, 0, 600);
  assert.ok(outward > 1 && outward < 1.01);
  assert.ok(Math.abs(outward * wheelZoomFactor(-5, 0, 600) - 1) < 1e-12);
});

test("wheel line and page units are normalized and large events are bounded", () => {
  assert.equal(wheelZoomFactor(1, 1, 600), wheelZoomFactor(16, 0, 600));
  assert.equal(wheelZoomFactor(1, 2, 600), wheelZoomFactor(120, 0, 600));
  assert.equal(wheelZoomFactor(5000, 0, 600), wheelZoomFactor(120, 0, 600));
  assert.equal(wheelZoomFactor(0, 0, 600), 1);
});
