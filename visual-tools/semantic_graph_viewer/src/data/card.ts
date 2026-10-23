import type { GraphNode } from "./graph.ts";

export interface CardSection { heading: string; body: string }
export interface CardSource { label: string; url: string }
export interface CardContent {
  summary?: string;
  sections: CardSection[];
  sources: CardSource[];
}

function object(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function text(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

/** Validate the viewer's optional card convention inside semantic_graph node attributes. */
export function parseCardContent(value: unknown, path: string): CardContent | null {
  if (value === undefined) return null;
  if (!object(value)) throw new Error(`${path} must be an object.`);
  if (value.summary !== undefined && !text(value.summary)) throw new Error(`${path}.summary must be a non-empty string.`);
  if (value.sections !== undefined && !Array.isArray(value.sections)) throw new Error(`${path}.sections must be an array.`);
  if (value.sources !== undefined && !Array.isArray(value.sources)) throw new Error(`${path}.sources must be an array.`);

  const sections = (value.sections ?? []) as unknown[];
  sections.forEach((section, index) => {
    if (!object(section) || !text(section.heading) || !text(section.body)) {
      throw new Error(`${path}.sections[${index}] must have a non-empty heading and body.`);
    }
  });
  const sources = (value.sources ?? []) as unknown[];
  sources.forEach((source, index) => {
    if (!object(source) || !text(source.label) || !text(source.url)) {
      throw new Error(`${path}.sources[${index}] must have a non-empty label and URL.`);
    }
    try {
      const url = new URL(source.url);
      if (url.protocol !== "https:" && url.protocol !== "http:") throw new Error("Unsupported protocol");
    } catch {
      throw new Error(`${path}.sources[${index}].url must be an HTTP(S) URL.`);
    }
  });
  return { summary: value.summary as string | undefined, sections: sections as CardSection[], sources: sources as CardSource[] };
}

export function cardForNode(node: GraphNode): CardContent | null {
  return parseCardContent(node.attributes.card, `node #${node.unique_id}.attributes.card`);
}
