import { parseCardContent } from "./card.ts";

export interface GraphNode {
  unique_id: number;
  label: string;
  kind: string;
  attributes: Record<string, unknown>;
}

export interface GraphEdge {
  unique_id: number;
  source: number;
  target: number;
  kind: string;
  label?: string | null;
  attributes: Record<string, unknown>;
}

export interface SemanticGraph {
  type: "semantic_graph";
  version: "0.1.0";
  graph_id: string;
  title?: string | null;
  attributes: Record<string, unknown>;
  revision?: number;
  next_node_id?: number;
  next_edge_id?: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
}

function record(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function positiveId(value: unknown): value is number {
  return typeof value === "number" && Number.isSafeInteger(value) && value > 0;
}

function nonempty(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function attributes(value: unknown, path: string): asserts value is Record<string, unknown> {
  if (!record(value)) throw new Error(`${path} must be a JSON object.`);
}

/** Validate the persisted v0.1.0 contract without repairing or changing claims. */
export function parseSemanticGraph(value: unknown): SemanticGraph {
  if (!record(value)) throw new Error("Graph must be a JSON object.");
  if (value.type !== "semantic_graph") throw new Error("type must be semantic_graph.");
  if (value.version !== "0.1.0") throw new Error("Only semantic_graph version 0.1.0 is supported.");
  if (!nonempty(value.graph_id)) throw new Error("graph_id must be a non-empty string.");
  if (value.title !== undefined && value.title !== null && typeof value.title !== "string") throw new Error("title must be a string or null.");
  attributes(value.attributes, "attributes");
  if (!Array.isArray(value.nodes)) throw new Error("nodes must be an array.");
  if (!Array.isArray(value.edges)) throw new Error("edges must be an array.");
  const nodeIds = new Set<number>();
  const edgeIds = new Set<number>();
  value.nodes.forEach((node: unknown, index: number) => {
    const path = `nodes[${index}]`;
    if (!record(node)) throw new Error(`${path} must be an object.`);
    if (!positiveId(node.unique_id)) throw new Error(`${path}.unique_id must be a positive integer.`);
    if (nodeIds.has(node.unique_id)) throw new Error(`Duplicate node unique_id ${node.unique_id}.`);
    if (!nonempty(node.label)) throw new Error(`${path}.label must be a non-empty string.`);
    if (!nonempty(node.kind)) throw new Error(`${path}.kind must be a non-empty string.`);
    attributes(node.attributes, `${path}.attributes`);
    parseCardContent(node.attributes.card, `${path}.attributes.card`);
    nodeIds.add(node.unique_id);
  });
  value.edges.forEach((edge: unknown, index: number) => {
    const path = `edges[${index}]`;
    if (!record(edge)) throw new Error(`${path} must be an object.`);
    if (!positiveId(edge.unique_id)) throw new Error(`${path}.unique_id must be a positive integer.`);
    if (edgeIds.has(edge.unique_id)) throw new Error(`Duplicate edge unique_id ${edge.unique_id}.`);
    if (!positiveId(edge.source) || !positiveId(edge.target)) throw new Error(`${path} must have positive integer source and target IDs.`);
    if (!nodeIds.has(edge.source) || !nodeIds.has(edge.target)) throw new Error(`${path} (#${edge.unique_id}) references a missing node.`);
    if (!nonempty(edge.kind)) throw new Error(`${path}.kind must be a non-empty string.`);
    if (edge.label !== undefined && edge.label !== null && typeof edge.label !== "string") throw new Error(`${path}.label must be a string or null.`);
    attributes(edge.attributes, `${path}.attributes`);
    edgeIds.add(edge.unique_id);
  });
  if (value.revision !== undefined && (!Number.isSafeInteger(value.revision) || (value.revision as number) < 0)) throw new Error("revision must be a non-negative integer.");
  if (value.next_node_id !== undefined && (!positiveId(value.next_node_id) || value.next_node_id <= Math.max(0, ...nodeIds))) throw new Error("next_node_id must exceed every node ID.");
  if (value.next_edge_id !== undefined && (!positiveId(value.next_edge_id) || value.next_edge_id <= Math.max(0, ...edgeIds))) throw new Error("next_edge_id must exceed every edge ID.");
  return value as unknown as SemanticGraph;
}

export interface GraphView {
  byId: Map<number, GraphNode>;
  incoming: Map<number, GraphEdge[]>;
  outgoing: Map<number, GraphEdge[]>;
  kinds: { kind: string; count: number }[];
}

/** Presentation indexes reference the original graph records. */
export function adaptGraph(graph: SemanticGraph): GraphView {
  const byId = new Map(graph.nodes.map((node) => [node.unique_id, node]));
  const incoming = new Map(graph.nodes.map((node) => [node.unique_id, [] as GraphEdge[]]));
  const outgoing = new Map(graph.nodes.map((node) => [node.unique_id, [] as GraphEdge[]]));
  const counts = new Map<string, number>();
  graph.nodes.forEach((node) => counts.set(node.kind, (counts.get(node.kind) ?? 0) + 1));
  graph.edges.forEach((edge) => {
    incoming.get(edge.target)!.push(edge);
    outgoing.get(edge.source)!.push(edge);
  });
  return { byId, incoming, outgoing, kinds: [...counts].map(([kind, count]) => ({ kind, count })).sort((a, b) => a.kind.localeCompare(b.kind)) };
}

export function matchingNodeIds(graph: SemanticGraph, query: string, kind: string | null): Set<number> {
  const needle = query.trim().toLocaleLowerCase();
  return new Set(graph.nodes.filter((node) =>
    (kind === null || node.kind === kind) &&
    (!needle || `${node.label} ${node.kind} ${node.unique_id}`.toLocaleLowerCase().includes(needle))
  ).map((node) => node.unique_id));
}

export function colorForKind(kind: string): string {
  let hash = 2166136261;
  for (const char of kind) hash = Math.imul(hash ^ char.codePointAt(0)!, 16777619);
  return `hsl(${(hash >>> 0) % 360} 64% 72%)`;
}
