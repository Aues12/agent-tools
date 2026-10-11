import type { SemanticGraph } from "./graph.ts";

export const NODE_WIDTH = 232;
export const NODE_HEIGHT = 84;
export interface Point { x: number; y: number }
export interface Layout { positions: Map<number, Point>; width: number; height: number; cyclic: boolean }

/** Place strongly connected components in left-to-right layers. Cycles remain visible. */
export function layoutGraph(graph: SemanticGraph): Layout {
  const ids = graph.nodes.map((node) => node.unique_id);
  const adjacency = new Map(ids.map((id) => [id, [] as number[]]));
  graph.edges.forEach((edge) => adjacency.get(edge.source)!.push(edge.target));
  const discovery = new Map<number, number>();
  const low = new Map<number, number>();
  const stack: number[] = [];
  const onStack = new Set<number>();
  const components: number[][] = [];
  let next = 0;
  function visit(id: number): void {
    discovery.set(id, next);
    low.set(id, next++);
    stack.push(id);
    onStack.add(id);
    for (const target of adjacency.get(id)!) {
      if (!discovery.has(target)) {
        visit(target);
        low.set(id, Math.min(low.get(id)!, low.get(target)!));
      } else if (onStack.has(target)) {
        low.set(id, Math.min(low.get(id)!, discovery.get(target)!));
      }
    }
    if (low.get(id) === discovery.get(id)) {
      const component: number[] = [];
      let member: number;
      do {
        member = stack.pop()!;
        onStack.delete(member);
        component.push(member);
      } while (member !== id);
      components.push(component.sort((a, b) => a - b));
    }
  }
  ids.forEach((id) => { if (!discovery.has(id)) visit(id); });
  const membership = new Map<number, number>();
  components.forEach((component, index) => component.forEach((id) => membership.set(id, index)));
  const outgoing = components.map(() => new Set<number>());
  const incoming = components.map(() => new Set<number>());
  let cyclic = components.some((component) => component.length > 1);
  graph.edges.forEach((edge) => {
    const source = membership.get(edge.source)!;
    const target = membership.get(edge.target)!;
    if (source === target) { if (edge.source === edge.target) cyclic = true; return; }
    outgoing[source].add(target);
    incoming[target].add(source);
  });
  const indegree = incoming.map((parents) => parents.size);
  const layers = components.map(() => 0);
  const queue = indegree.map((count, index) => count === 0 ? index : -1).filter((index) => index >= 0);
  for (let index = 0; index < queue.length; index++) {
    const source = queue[index];
    for (const target of outgoing[source]) {
      layers[target] = Math.max(layers[target], layers[source] + 1);
      indegree[target]--;
      if (indegree[target] === 0) queue.push(target);
    }
  }
  const columns = new Map<number, number[]>();
  components.forEach((_, index) => {
    const layer = layers[index];
    if (!columns.has(layer)) columns.set(layer, []);
    columns.get(layer)!.push(index);
  });
  // Barycenter ordering makes branches easier to follow while keeping deterministic ties.
  const ranks = new Map<number, number>();
  [...columns.keys()].sort((a, b) => a - b).forEach((layer) => {
    const column = columns.get(layer)!;
    column.sort((a, b) => {
      const score = (index: number) => {
        const parents = [...incoming[index]].filter((parent) => ranks.has(parent));
        return parents.length ? parents.reduce((sum, parent) => sum + ranks.get(parent)!, 0) / parents.length : index;
      };
      return score(a) - score(b) || a - b;
    });
    column.forEach((index, rank) => ranks.set(index, rank));
  });
  const positions = new Map<number, Point>();
  const columnHeights = [...columns.values()].map((column) => column.reduce((sum, index) => sum + components[index].length, 0));
  const maxHeight = Math.max(1, ...columnHeights);
  for (const [layer, column] of columns) {
    const count = column.reduce((sum, index) => sum + components[index].length, 0);
    let row = (maxHeight - count) / 2;
    for (const index of column) {
      for (const id of components[index]) {
        positions.set(id, { x: 72 + layer * 326, y: 72 + row * 126 });
        row++;
      }
    }
  }
  const maxLayer = Math.max(0, ...layers);
  return { positions, width: 72 + maxLayer * 326 + NODE_WIDTH + 72, height: 72 + (maxHeight - 1) * 126 + NODE_HEIGHT + 72, cyclic };
}
