import type { SemanticGraph, SemanticGraphNode } from "../types/semanticGraph";
import { nodeDate } from "../types/semanticGraph";

export interface TimelineNode {
  node: SemanticGraphNode;
  date: Date;
  x: number;
  y: number;
  radius: number;
  degree: number;
  lane: number;
}

export interface TimelineLayout {
  nodes: TimelineNode[];
  byId: Map<string, TimelineNode>;
  width: number;
  height: number;
  axisY: number;
  minDate: Date;
  maxDate: Date;
  years: Array<{ year: number; x: number }>;
}

const DAY_MS = 86_400_000;
const PADDING_X = 110;
const AXIS_Y = 108;
const LANE_GAP = 34;
const LANE_COUNT = 15;
const MIN_NODE_GAP = 24;

function timestamp(node: SemanticGraphNode): number {
  return nodeDate(node)?.getTime() ?? 0;
}

export function buildTimelineLayout(graph: SemanticGraph): TimelineLayout {
  const sorted = [...graph.nodes].sort(
    (left, right) => timestamp(left) - timestamp(right) || left.id.localeCompare(right.id),
  );
  const minDate = nodeDate(sorted[0])!;
  const maxDate = nodeDate(sorted.at(-1)!)!;
  const daySpan = Math.max(1, (maxDate.getTime() - minDate.getTime()) / DAY_MS);
  const width = Math.max(3200, Math.ceil(daySpan * 3.4) + PADDING_X * 2);
  const height = AXIS_Y + LANE_COUNT * LANE_GAP + 96;
  const degree = new Map(graph.nodes.map((node) => [node.id, 0]));
  for (const edge of graph.edges) {
    degree.set(edge.source, (degree.get(edge.source) ?? 0) + 1);
    degree.set(edge.target, (degree.get(edge.target) ?? 0) + 1);
  }

  const laneLastX = Array.from({ length: LANE_COUNT }, () => -Infinity);
  const nodes = sorted.map((node) => {
    const date = nodeDate(node)!;
    const progress = (date.getTime() - minDate.getTime()) / (daySpan * DAY_MS);
    const x = PADDING_X + progress * (width - PADDING_X * 2);
    let lane = laneLastX.findIndex((lastX) => x - lastX >= MIN_NODE_GAP);
    if (lane === -1) {
      lane = laneLastX.indexOf(Math.min(...laneLastX));
    }
    laneLastX[lane] = x;
    const nodeDegree = degree.get(node.id) ?? 0;
    return {
      node,
      date,
      x,
      y: AXIS_Y + 48 + lane * LANE_GAP,
      radius: Math.min(10, 4 + Math.sqrt(nodeDegree) * 1.2),
      degree: nodeDegree,
      lane,
    };
  });
  const byId = new Map(nodes.map((item) => [item.node.id, item]));

  const years: Array<{ year: number; x: number }> = [];
  for (let year = minDate.getFullYear(); year <= maxDate.getFullYear(); year += 1) {
    const date = new Date(year, 0, 1);
    const progress = (date.getTime() - minDate.getTime()) / (daySpan * DAY_MS);
    years.push({ year, x: PADDING_X + progress * (width - PADDING_X * 2) });
  }

  return { nodes, byId, width, height, axisY: AXIS_Y, minDate, maxDate, years };
}
