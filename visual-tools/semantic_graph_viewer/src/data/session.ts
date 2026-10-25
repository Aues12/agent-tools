import { parseSemanticGraph, type SemanticGraph } from "./graph.ts";

const GRAPH_KEY = "semantic-graph-viewer.graph.v1";
const VIEW_KEY = "semantic-graph-viewer.view.v1";

export type ViewProfile = "classic" | "study";
export type SessionStorage = Pick<Storage, "getItem" | "setItem">;

export interface SavedViewport {
  x: number;
  y: number;
  width: number;
  height: number;
  canvasWidth: number;
  canvasHeight: number;
}

export interface SavedView {
  profile: ViewProfile;
  indexOpen: boolean;
  inspectorOpen: boolean;
  query: string;
  kind: string | null;
  selectedId: number | null;
  studyCardId: number | null;
  viewport: SavedViewport | null;
}

export interface RestoredSession extends SavedView {
  graph: SemanticGraph;
  fileName: string;
}

function record(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function finite(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function readViewport(value: unknown): SavedViewport | null {
  if (!record(value)) return null;
  const { x, y, width, height, canvasWidth, canvasHeight } = value;
  if (!finite(x) || !finite(y) || !finite(width) || !finite(height) || !finite(canvasWidth) || !finite(canvasHeight)) return null;
  if (width <= 0 || height <= 0 || canvasWidth <= 0 || canvasHeight <= 0) return null;
  return { x, y, width, height, canvasWidth, canvasHeight };
}

export function browserStorage(): SessionStorage | null {
  try { return typeof window === "undefined" ? null : window.localStorage; }
  catch { return null; }
}

/** Tie view state to the exact graph contents, even when two files share an ID. */
export function graphFingerprint(graph: SemanticGraph): string {
  const json = JSON.stringify(graph);
  let hash = 2166136261;
  for (let index = 0; index < json.length; index++) hash = Math.imul(hash ^ json.charCodeAt(index), 16777619);
  return `${graph.graph_id}:${json.length}:${(hash >>> 0).toString(16)}`;
}

export function restoreSession(storage: SessionStorage | null, fallback: SemanticGraph, fallbackName: string): RestoredSession {
  let graph = fallback;
  let fileName = fallbackName;
  try {
    const saved = storage?.getItem(GRAPH_KEY);
    if (saved) {
      const value: unknown = JSON.parse(saved);
      if (record(value) && value.version === 1 && typeof value.fileName === "string" && value.fileName.trim()) {
        graph = parseSemanticGraph(value.graph);
        fileName = value.fileName;
      }
    }
  } catch { /* A stale or inaccessible cache must not prevent the viewer from opening. */ }

  const defaults: RestoredSession = {
    graph, fileName, profile: "classic", indexOpen: true, inspectorOpen: true,
    query: "", kind: null, selectedId: null, studyCardId: null, viewport: null,
  };
  try {
    const saved = storage?.getItem(VIEW_KEY);
    if (!saved) return defaults;
    const value: unknown = JSON.parse(saved);
    if (!record(value) || value.version !== 1 || value.graphFingerprint !== graphFingerprint(graph)) return defaults;
    const ids = new Set(graph.nodes.map((node) => node.unique_id));
    const kinds = new Set(graph.nodes.map((node) => node.kind));
    const profile = value.profile === "study" ? "study" : "classic";
    return {
      graph, fileName, profile,
      indexOpen: typeof value.indexOpen === "boolean" ? value.indexOpen : true,
      inspectorOpen: typeof value.inspectorOpen === "boolean" ? value.inspectorOpen : true,
      query: typeof value.query === "string" ? value.query : "",
      kind: typeof value.kind === "string" && kinds.has(value.kind) ? value.kind : null,
      selectedId: typeof value.selectedId === "number" && ids.has(value.selectedId) ? value.selectedId : null,
      studyCardId: profile === "study" && typeof value.studyCardId === "number" && ids.has(value.studyCardId) ? value.studyCardId : null,
      viewport: readViewport(value.viewport),
    };
  } catch { return defaults; }
}

function write(storage: SessionStorage | null, key: string, value: unknown): boolean {
  try {
    if (!storage) return false;
    storage.setItem(key, JSON.stringify(value));
    return true;
  } catch { return false; }
}

export function saveGraph(storage: SessionStorage | null, graph: SemanticGraph, fileName: string): boolean {
  return write(storage, GRAPH_KEY, { version: 1, graph, fileName });
}

export function saveView(storage: SessionStorage | null, fingerprint: string, view: SavedView): boolean {
  return write(storage, VIEW_KEY, { version: 1, graphFingerprint: fingerprint, ...view });
}
