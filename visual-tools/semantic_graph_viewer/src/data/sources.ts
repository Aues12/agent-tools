import { cardForNode } from "./card.ts";
import type { GraphNode, SemanticGraph } from "./graph.ts";

export interface DisplaySource {
  key: string;
  kind: string;
  label: string;
  detail?: string;
  href?: string;
  sourceId?: string;
  interpretation: boolean;
}

function record(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function nonempty(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function httpUrl(value: unknown): string | undefined {
  if (!nonempty(value)) return undefined;
  try {
    const url = new URL(value);
    return url.protocol === "https:" || url.protocol === "http:" ? value : undefined;
  } catch {
    return undefined;
  }
}

/** Adapt optional provenance attributes for display without changing graph records. */
export function sourcesForNode(graph: SemanticGraph, node: GraphNode): DisplaySource[] {
  const catalog = new Map<string, Record<string, unknown>>();
  if (Array.isArray(graph.attributes.sources)) {
    for (const entry of graph.attributes.sources) {
      if (record(entry) && nonempty(entry.id) && !catalog.has(entry.id)) catalog.set(entry.id, entry);
    }
  }

  const sources: DisplaySource[] = [];
  const seenIds = new Set<string>();
  const seenUrls = new Set<string>();
  const refs = node.attributes.source_refs;
  if (Array.isArray(refs)) {
    for (const ref of refs) {
      if (!record(ref) || !nonempty(ref.source_id) || seenIds.has(ref.source_id)) continue;
      seenIds.add(ref.source_id);
      const entry = catalog.get(ref.source_id);
      const kind = entry && nonempty(entry.type) ? entry.type : "unknown";
      const href = entry ? httpUrl(entry.url) : undefined;
      if (href) seenUrls.add(href);
      sources.push({
        key: `ref:${ref.source_id}`,
        kind,
        label: entry && nonempty(entry.label) ? entry.label : ref.source_id,
        detail: entry && nonempty(entry.path) ? entry.path : href ? new URL(href).hostname : undefined,
        href,
        sourceId: ref.source_id,
        interpretation: kind === "agent_interpretation",
      });
    }
  }

  for (const source of cardForNode(node)?.sources ?? []) {
    if (seenUrls.has(source.url)) continue;
    seenUrls.add(source.url);
    sources.push({
      key: `url:${source.url}`,
      kind: "online",
      label: source.label,
      detail: new URL(source.url).hostname,
      href: source.url,
      interpretation: false,
    });
  }
  return sources;
}
