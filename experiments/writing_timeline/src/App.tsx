import { useEffect, useMemo, useState } from "react";
import { TimelineCanvas } from "./timeline/TimelineCanvas";
import {
  nodeDate,
  parseSemanticGraph,
  type SemanticGraph,
  type SemanticGraphNode,
} from "./types/semanticGraph";

interface LoadState {
  graph?: SemanticGraph;
  loading: boolean;
  error?: string;
}

function normalized(value: string): string {
  return value.trim().toLocaleLowerCase("tr");
}

function mostConnectedNodeId(graph: SemanticGraph): string | undefined {
  const degrees = new Map(graph.nodes.map((node) => [node.id, 0]));
  for (const edge of graph.edges) {
    degrees.set(edge.source, (degrees.get(edge.source) ?? 0) + 1);
    degrees.set(edge.target, (degrees.get(edge.target) ?? 0) + 1);
  }
  return graph.nodes.reduce<string | undefined>((best, node) => {
    if (!best || (degrees.get(node.id) ?? 0) > (degrees.get(best) ?? 0)) return node.id;
    return best;
  }, undefined);
}

function displayDate(node: SemanticGraphNode): string {
  const date = nodeDate(node);
  if (!date) return "Tarih yok";
  return new Intl.DateTimeFormat("tr-TR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  }).format(date);
}

export function App() {
  const [state, setState] = useState<LoadState>({ loading: true });
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState<string>();

  useEffect(() => {
    let active = true;
    fetch("/graphs/book_reference_graph.json")
      .then(async (response) => {
        if (!response.ok) throw new Error(`Graph yüklenemedi (${response.status}).`);
        return parseSemanticGraph(await response.json());
      })
      .then((graph) => {
        if (!active) return;
        setState({ graph, loading: false });
        setSelectedId(mostConnectedNodeId(graph));
      })
      .catch((error: unknown) => {
        if (active) setState({ loading: false, error: error instanceof Error ? error.message : "Graph yüklenemedi." });
      });
    return () => {
      active = false;
    };
  }, []);

  const selectedNode = state.graph?.nodes.find((node) => node.id === selectedId);
  const dateRange = useMemo(() => {
    if (!state.graph) return "—";
    const years = state.graph.nodes
      .map((node) => nodeDate(node)?.getFullYear())
      .filter((year): year is number => typeof year === "number");
    return years.length > 0 ? `${Math.min(...years)}—${Math.max(...years)}` : "—";
  }, [state.graph]);
  const searchResults = useMemo(() => {
    if (!state.graph || !normalized(query)) return [];
    const needle = normalized(query);
    return state.graph.nodes
      .filter((node) => normalized(`${node.label} ${node.id}`).includes(needle))
      .slice(0, 10);
  }, [query, state.graph]);
  const connections = useMemo(() => {
    if (!state.graph || !selectedId) return { incoming: [], outgoing: [] };
    const byId = new Map(state.graph.nodes.map((node) => [node.id, node]));
    return {
      outgoing: state.graph.edges
        .filter((edge) => edge.source === selectedId)
        .map((edge) => byId.get(edge.target))
        .filter((node): node is SemanticGraphNode => Boolean(node)),
      incoming: state.graph.edges
        .filter((edge) => edge.target === selectedId)
        .map((edge) => byId.get(edge.source))
        .filter((node): node is SemanticGraphNode => Boolean(node)),
    };
  }, [selectedId, state.graph]);

  async function openGraph(file: File) {
    try {
      const graph = parseSemanticGraph(JSON.parse(await file.text()));
      setState({ graph, loading: false });
      setSelectedId(mostConnectedNodeId(graph));
      setQuery("");
    } catch (error: unknown) {
      setState({ loading: false, error: error instanceof Error ? error.message : "Graph okunamadı." });
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <header>
          <p className="eyebrow">Yazı Atlası</p>
          <h1>Bağlantılı Zaman</h1>
          <p className="lede">Yazıların kronolojik akışı ve birbirlerine verdikleri açık referanslar.</p>
        </header>

        <label className="field upload-field">
          <span>Graph aç</span>
          <input
            type="file"
            accept="application/json,.json"
            onChange={(event) => {
              const file = event.target.files?.[0];
              if (file) void openGraph(file);
              event.target.value = "";
            }}
          />
        </label>

        <label className="field">
          <span>Yazı ara</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="başlık veya slug"
          />
        </label>

        {searchResults.length > 0 && (
          <div className="search-results" aria-label="Arama sonuçları">
            {searchResults.map((node) => (
              <button key={node.id} type="button" onClick={() => setSelectedId(node.id)}>
                <strong>{node.label}</strong>
                <time>{displayDate(node)}</time>
              </button>
            ))}
          </div>
        )}

        {state.loading && <p className="status">Graph yükleniyor…</p>}
        {state.error && <p className="status status--error">{state.error}</p>}
        {state.graph && (
          <dl className="stats">
            <div><dt>Yazı</dt><dd>{state.graph.nodes.length}</dd></div>
            <div><dt>Referans</dt><dd>{state.graph.edges.length}</dd></div>
            <div><dt>Aralık</dt><dd>{dateRange}</dd></div>
          </dl>
        )}

        {selectedNode && (
          <section className="inspector">
            <p className="eyebrow">Seçili yazı</p>
            <h2>{selectedNode.label}</h2>
            <time>{displayDate(selectedNode)}</time>
            <p className="slug">{selectedNode.id}</p>

            <div className="connection-groups">
              <ConnectionGroup title="Referans verdiği" nodes={connections.outgoing} onSelect={setSelectedId} />
              <ConnectionGroup title="Ona referans veren" nodes={connections.incoming} onSelect={setSelectedId} />
            </div>
          </section>
        )}
      </aside>

      <section className="workspace" aria-label="Yazı zaman çizgisi">
        {state.graph ? (
          <TimelineCanvas graph={state.graph} query={query} selectedId={selectedId} onSelect={setSelectedId} />
        ) : (
          <div className="empty-state">Başlamak için bir semantic_graph JSON dosyası aç.</div>
        )}
      </section>
    </main>
  );
}

function ConnectionGroup({
  title,
  nodes,
  onSelect,
}: {
  title: string;
  nodes: SemanticGraphNode[];
  onSelect: (nodeId: string) => void;
}) {
  return (
    <div className="connection-group">
      <h3>{title} <span>{nodes.length}</span></h3>
      {nodes.length === 0 ? (
        <p>Bağlantı yok.</p>
      ) : (
        nodes.map((node) => (
          <button key={node.id} type="button" onClick={() => onSelect(node.id)}>{node.label}</button>
        ))
      )}
    </div>
  );
}
