import type { Point } from "./layout.ts";

export type ArrowDirection = "ArrowLeft" | "ArrowRight" | "ArrowUp" | "ArrowDown";

/** Choose the nearest node in the requested visual direction. */
export function nextNodeId(
  positions: Map<number, Point>,
  candidateIds: ReadonlySet<number>,
  selectedId: number | null,
  direction: ArrowDirection,
  viewportCenter: Point,
): number | null {
  const candidates = [...candidateIds].filter((id) => positions.has(id));
  if (candidates.length === 0) return null;

  const selectedPoint = selectedId === null || !candidateIds.has(selectedId) ? undefined : positions.get(selectedId);
  if (!selectedPoint) {
    return candidates.sort((a, b) => {
      const pa = positions.get(a)!;
      const pb = positions.get(b)!;
      const da = (pa.x - viewportCenter.x) ** 2 + (pa.y - viewportCenter.y) ** 2;
      const db = (pb.x - viewportCenter.x) ** 2 + (pb.y - viewportCenter.y) ** 2;
      return da - db || a - b;
    })[0];
  }

  const options = candidates.flatMap((id) => {
    if (id === selectedId) return [];
    const point = positions.get(id)!;
    const dx = point.x - selectedPoint.x;
    const dy = point.y - selectedPoint.y;
    const forward = direction === "ArrowRight" ? dx : direction === "ArrowLeft" ? -dx : direction === "ArrowDown" ? dy : -dy;
    if (forward <= 0) return [];
    const sideways = Math.abs(direction === "ArrowLeft" || direction === "ArrowRight" ? dy : dx);
    return [{ id, forward, sideways, score: forward + sideways * 1.25 }];
  });
  options.sort((a, b) => a.score - b.score || a.forward - b.forward || a.sideways - b.sideways || a.id - b.id);
  return options[0]?.id ?? null;
}
