export interface SemanticGraphNode {
  id: string;
  label: string;
  kind: string;
  attributes?: Record<string, unknown>;
}

export interface SemanticGraphEdge {
  source: string;
  target: string;
  kind: string;
  label?: string;
  attributes?: Record<string, unknown>;
}

export interface SemanticGraph {
  type: "semantic_graph";
  directed: true;
  acyclic?: boolean;
  nodes: SemanticGraphNode[];
  edges: SemanticGraphEdge[];
  kinds?: { nodes: string[]; edges: string[] };
  name?: string;
  description?: string;
  attributes?: Record<string, unknown>;
}

export function nodeDate(node: SemanticGraphNode): Date | undefined {
  const rawDate = node.attributes?.date;
  if (typeof rawDate !== "string") return undefined;
  const date = new Date(rawDate);
  return Number.isNaN(date.getTime()) ? undefined : date;
}

export function parseSemanticGraph(value: unknown): SemanticGraph {
  if (!value || typeof value !== "object") {
    throw new Error("Graph JSON bir nesne olmalı.");
  }
  const graph = value as Partial<SemanticGraph>;
  if (graph.type !== "semantic_graph" || graph.directed !== true) {
    throw new Error("Yönlü bir semantic_graph belgesi bekleniyor.");
  }
  if (!Array.isArray(graph.nodes) || graph.nodes.length === 0) {
    throw new Error("Graph en az bir node içermeli.");
  }
  if (!Array.isArray(graph.edges)) {
    throw new Error("Graph edges alanı bir dizi olmalı.");
  }

  const nodeIds = new Set<string>();
  for (const node of graph.nodes) {
    if (!node || typeof node.id !== "string" || !node.id.trim()) {
      throw new Error("Her node boş olmayan bir id taşımalı.");
    }
    if (!nodeDate(node)) {
      throw new Error(`Node geçerli bir attributes.date taşımıyor: ${node.id}`);
    }
    if (nodeIds.has(node.id)) throw new Error(`Tekrarlanan node id: ${node.id}`);
    nodeIds.add(node.id);
  }
  for (const edge of graph.edges) {
    if (!edge || !nodeIds.has(edge.source) || !nodeIds.has(edge.target)) {
      throw new Error("Her edge var olan source ve target node'larına bağlanmalı.");
    }
  }
  return graph as SemanticGraph;
}
