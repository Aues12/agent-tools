import { useMemo, useRef, useState, type ChangeEvent } from "react";
import exampleData from "../public/graphs/bookbarcode_workflow_dag_en.json";
import { adaptGraph, colorForKind, matchingNodeIds, parseSemanticGraph, type GraphEdge, type SemanticGraph } from "./data/graph.ts";
import { GraphCanvas } from "./components/GraphCanvas";

const example = parseSemanticGraph(exampleData);

function Attributes({ value }: { value: Record<string, unknown> }) {
  const entries = Object.entries(value);
  return <details className="attributes"><summary>Attributes <span>{entries.length}</span></summary>
    {entries.length ? <dl>{entries.map(([key, item]) => <div key={key}><dt>{key}</dt><dd><code>{typeof item === "string" ? item : JSON.stringify(item)}</code></dd></div>)}</dl> : <p>No attributes</p>}
  </details>;
}

export function App() {
  const [graph, setGraph] = useState<SemanticGraph>(example);
  const [fileName, setFileName] = useState("BookBarcode English example");
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [kind, setKind] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [focus, setFocus] = useState<{ id: number; serial: number } | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const view = useMemo(() => adaptGraph(graph), [graph]);
  const matchedIds = useMemo(() => matchingNodeIds(graph, query, kind), [graph, query, kind]);
  const selected = selectedId === null ? null : view.byId.get(selectedId) ?? null;

  function navigate(id: number) {
    setSelectedId(id);
    setFocus((previous) => ({ id, serial: (previous?.serial ?? 0) + 1 }));
  }

  async function loadFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const value = JSON.parse(await file.text()) as unknown;
      const loaded = parseSemanticGraph(value);
      setGraph(loaded);
      setFileName(file.name);
      setError(null);
      setQuery("");
      setKind(null);
      setSelectedId(null);
      setFocus(null);
    } catch (cause) {
      setError(`${file.name}: ${cause instanceof Error ? cause.message : "Unable to read this file."}`);
    }
    event.target.value = "";
  }

  function relationship(edge: GraphEdge, otherId: number) {
    const other = view.byId.get(otherId)!;
    return <button className="relationship" key={edge.unique_id} onClick={() => navigate(otherId)}>
      <span className="relationship-kind">{edge.kind} <span>· edge #{edge.unique_id}</span></span>
      {edge.label && <span className="relationship-label">{edge.label}</span>}
      <span className="relationship-target">#{other.unique_id} · {other.label}</span>
      {Object.keys(edge.attributes).length > 0 && <span className="relationship-attrs">{JSON.stringify(edge.attributes)}</span>}
    </button>;
  }

  return <div className="app-shell">
    <header className="topbar">
      <div className="brand-mark" aria-hidden="true">◈</div>
      <div className="brand"><strong>Semantic <span>Graph Viewer</span></strong><small>Explore the structure behind an artifact</small></div>
      <span className="version-pill">SEMANTIC GRAPH · v{graph.version}</span>
      <div className="topbar-spacer" />
      <span className="topbar-stats">{graph.nodes.length} nodes <i /> {graph.edges.length} relations</span>
    </header>

    <aside className="index-panel" aria-label="Semantic index">
      <div className="panel-kicker">CURRENT GRAPH</div>
      <h1>{graph.title || graph.graph_id}</h1>
      <div className="graph-id">{graph.graph_id}</div>
      <div className="source-line">{fileName}{graph.revision !== undefined ? ` · revision ${graph.revision}` : ""}</div>
      <button className="load-button" onClick={() => fileInput.current?.click()}>Load JSON graph</button>
      <input ref={fileInput} type="file" accept=".json,application/json" onChange={loadFile} className="visually-hidden" aria-label="Choose semantic graph JSON file" />
      {error && <div className="load-error" role="alert"><strong>Could not load graph</strong><p>{error}</p></div>}
      <div className="section-rule" />
      <label className="panel-kicker" htmlFor="node-search">SEARCH NODES</label>
      <input id="node-search" className="search-input" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Label, kind, or ID…" />
      <div className="match-count">{matchedIds.size} of {graph.nodes.length} nodes</div>
      <div className="section-rule" />
      <div className="panel-kicker">NODE KINDS</div>
      <div className="kind-list">
        <button className={`kind-filter ${kind === null ? "active" : ""}`} onClick={() => setKind(null)}><span>All kinds</span><span>{graph.nodes.length}</span></button>
        {view.kinds.map((entry) => <button key={entry.kind} className={`kind-filter ${kind === entry.kind ? "active" : ""}`} onClick={() => setKind(entry.kind)}><span><b className="kind-dot" style={{ background: colorForKind(entry.kind) }} />{entry.kind}</span><span>{entry.count}</span></button>)}
      </div>
      <div className="section-rule" />
      <div className="panel-kicker">NODE INDEX</div>
      <div className="node-list">{graph.nodes.filter((node) => matchedIds.has(node.unique_id)).map((node) => <button key={node.unique_id} className={`node-list-item ${selectedId === node.unique_id ? "active" : ""}`} onClick={() => navigate(node.unique_id)}><span className="node-list-id">#{node.unique_id}</span><span>{node.label}</span></button>)}</div>
    </aside>

    <main className="main-panel"><GraphCanvas graph={graph} selectedId={selectedId} matchedIds={matchedIds} onSelect={setSelectedId} focus={focus} key={graph.graph_id + fileName} /></main>

    <aside className="inspector-panel" aria-label="Semantic inspector">
      {selected ? <>
        <div className="inspector-heading"><span className="panel-kicker">SELECTED NODE · #{selected.unique_id}</span><button aria-label="Clear selection" title="Clear selection" onClick={() => setSelectedId(null)}>×</button></div>
        <h2>{selected.label}</h2>
        <span className="kind-tag" style={{ color: colorForKind(selected.kind), borderColor: colorForKind(selected.kind) }}>{selected.kind}</span>
        <div className="detail-heading">SOURCE IDENTITY</div>
        <div className="identity-card"><div>Node ID <strong>#{selected.unique_id}</strong></div><div>Graph <strong>{graph.graph_id}</strong></div></div>
        <Attributes value={selected.attributes} />
        <div className="detail-heading">INCOMING <span>{view.incoming.get(selected.unique_id)?.length ?? 0}</span></div>
        {(view.incoming.get(selected.unique_id) ?? []).length ? view.incoming.get(selected.unique_id)!.map((edge) => relationship(edge, edge.source)) : <p className="empty-copy">No incoming relationships.</p>}
        <div className="detail-heading">OUTGOING <span>{view.outgoing.get(selected.unique_id)?.length ?? 0}</span></div>
        {(view.outgoing.get(selected.unique_id) ?? []).length ? view.outgoing.get(selected.unique_id)!.map((edge) => relationship(edge, edge.target)) : <p className="empty-copy">No outgoing relationships.</p>}
      </> : <div className="inspector-empty"><div className="empty-icon">◇</div><div className="panel-kicker">SEMANTIC INSPECTOR</div><h2>Select a node to explore its relationships</h2><p>Choose a node in the graph or index to see its original ID, attributes, incoming links, and outgoing links.</p></div>}
    </aside>
  </div>;
}
