import { useEffect, useMemo, useRef, useState, type ChangeEvent, type KeyboardEvent, type MouseEvent } from "react";
import exampleData from "../public/graphs/bookbarcode_workflow_dag_en.json";
import studyExampleData from "../public/graphs/working_memory_study_demo.json";
import { adaptGraph, colorForKind, matchingNodeIds, parseSemanticGraph, type GraphEdge, type SemanticGraph } from "./data/graph.ts";
import { GraphCanvas } from "./components/GraphCanvas";
import { StudyCardDialog } from "./components/StudyCardDialog";

const example = parseSemanticGraph(exampleData);
const studyExample = parseSemanticGraph(studyExampleData);
type ViewProfile = "classic" | "study";

function moveInList(event: KeyboardEvent<HTMLDivElement>) {
  const step = event.key === "ArrowDown" || event.key === "ArrowRight" ? 1
    : event.key === "ArrowUp" || event.key === "ArrowLeft" ? -1 : 0;
  if (!step) return;
  const buttons = [...event.currentTarget.querySelectorAll<HTMLButtonElement>("button")];
  if (!buttons.length) return;
  const focused = buttons.indexOf(event.target as HTMLButtonElement);
  const active = buttons.findIndex((button) => button.classList.contains("active"));
  const current = focused >= 0 ? focused : active;
  event.preventDefault();
  const next = current < 0 ? (step > 0 ? 0 : buttons.length - 1)
    : Math.max(0, Math.min(buttons.length - 1, current + step));
  buttons[next].focus();
  if (next !== current) buttons[next].click();
}

function focusListOnClick(event: MouseEvent<HTMLDivElement>) {
  const target = event.target as HTMLElement;
  const button = target.closest("button");
  if (button && event.currentTarget.contains(button)) button.focus();
  else event.currentTarget.focus();
}

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
  const [indexOpen, setIndexOpen] = useState(true);
  const [inspectorOpen, setInspectorOpen] = useState(true);
  const [optionsOpen, setOptionsOpen] = useState(false);
  const [profile, setProfile] = useState<ViewProfile>("classic");
  const [studyCardId, setStudyCardId] = useState<number | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const kindList = useRef<HTMLDivElement>(null);
  const nodeList = useRef<HTMLDivElement>(null);
  const optionsAnchor = useRef<HTMLDivElement>(null);
  const optionsButton = useRef<HTMLButtonElement>(null);
  const view = useMemo(() => adaptGraph(graph), [graph]);
  const matchedIds = useMemo(() => matchingNodeIds(graph, query, kind), [graph, query, kind]);
  const selected = selectedId === null ? null : view.byId.get(selectedId) ?? null;
  const studyCard = studyCardId === null ? null : view.byId.get(studyCardId) ?? null;

  useEffect(() => {
    if (!optionsOpen) return;
    function closeOnOutsideClick(event: PointerEvent) {
      if (!optionsAnchor.current?.contains(event.target as Node)) setOptionsOpen(false);
    }
    function closeOnEscape(event: globalThis.KeyboardEvent) {
      if (event.key !== "Escape") return;
      setOptionsOpen(false);
      optionsButton.current?.focus();
    }
    document.addEventListener("pointerdown", closeOnOutsideClick);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("pointerdown", closeOnOutsideClick);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, [optionsOpen]);

  function navigate(id: number) {
    setSelectedId(id);
    setFocus((previous) => ({ id, serial: (previous?.serial ?? 0) + 1 }));
    if (profile === "study") setStudyCardId(id);
  }

  function showGraph(loaded: SemanticGraph, name: string) {
    setGraph(loaded);
    setFileName(name);
    setError(null);
    setQuery("");
    setKind(null);
    setSelectedId(null);
    setStudyCardId(null);
    setFocus(null);
  }

  function closeStudyCard() {
    setStudyCardId(null);
    requestAnimationFrame(() => document.querySelector<HTMLElement>(".canvas")?.focus({ preventScroll: true }));
  }

  async function loadFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const value = JSON.parse(await file.text()) as unknown;
      const loaded = parseSemanticGraph(value);
      showGraph(loaded, file.name);
    } catch (cause) {
      setError(`${file.name}: ${cause instanceof Error ? cause.message : "Unable to read this file."}`);
    }
    event.target.value = "";
  }

  function relationship(edge: GraphEdge, otherId: number) {
    const other = view.byId.get(otherId)!;
    return <button className="relationship" key={edge.unique_id} onClick={() => navigate(otherId)}>
      <span className="relationship-kind">{edge.kind} <span>· edge #{edge.unique_id}</span></span>
      <span className="relationship-label">Node #{edge.source} → #{edge.target}{edge.label ? ` · ${edge.label}` : ""}</span>
      <span className="relationship-target">#{other.unique_id} · {other.label}</span>
      {Object.keys(edge.attributes).length > 0 && <span className="relationship-attrs">{JSON.stringify(edge.attributes)}</span>}
    </button>;
  }

  return <div className={`app-shell ${indexOpen ? "" : "index-collapsed"} ${inspectorOpen ? "" : "inspector-collapsed"}`}>
    <header className="topbar">
      <div className="brand-mark" aria-hidden="true">◈</div>
      <div className="brand"><strong>Semantic <span>Graph Viewer</span></strong><small>Explore the structure behind an artifact</small></div>
      <span className="version-pill">SEMANTIC GRAPH · v{graph.version}</span>
      <div className="topbar-spacer" />
      <div className="panel-toggles" aria-label="Panel visibility">
        <button className={`panel-toggle ${indexOpen ? "active" : ""}`} onClick={() => setIndexOpen((open) => !open)} aria-controls="semantic-index" aria-expanded={indexOpen} aria-label={indexOpen ? "Hide semantic index" : "Show semantic index"} title={indexOpen ? "Hide semantic index" : "Show semantic index"}><span aria-hidden="true">◧</span><span className="toggle-text">Index</span></button>
        <button className={`panel-toggle ${inspectorOpen ? "active" : ""}`} onClick={() => setInspectorOpen((open) => !open)} aria-controls="semantic-inspector" aria-expanded={inspectorOpen} aria-label={inspectorOpen ? "Hide semantic inspector" : "Show semantic inspector"} title={inspectorOpen ? "Hide semantic inspector" : "Show semantic inspector"}><span aria-hidden="true">◨</span><span className="toggle-text">Inspector</span></button>
      </div>
      <div className="options-anchor" ref={optionsAnchor}>
        <button ref={optionsButton} className={`options-button ${optionsOpen ? "active" : ""}`} aria-haspopup="dialog" aria-expanded={optionsOpen} aria-controls="viewer-options" onClick={() => setOptionsOpen((open) => !open)}><span aria-hidden="true">⚙</span><span>Options</span></button>
        {optionsOpen && <div id="viewer-options" className="options-popover" role="dialog" aria-label="Viewer options">
          <div className="options-header"><div><span className="panel-kicker">PREFERENCES</span><h2>Options</h2></div><button className="options-close" onClick={() => { setOptionsOpen(false); optionsButton.current?.focus(); }} aria-label="Close options">×</button></div>
          <div className="options-section"><h3>View profile</h3>
            <label className={`profile-card ${profile === "classic" ? "active" : ""}`}><input type="radio" name="view-profile" value="classic" checked={profile === "classic"} onChange={() => { setProfile("classic"); setStudyCardId(null); }} /><span><strong>Classic</strong><small>Original graph view</small></span></label>
            <label className={`profile-card ${profile === "study" ? "active" : ""}`}><input type="radio" name="view-profile" value="study" checked={profile === "study"} onChange={() => setProfile("study")} /><span><strong>Study</strong><small>Preview and open information cards</small></span></label>
            <button className="study-example-button" onClick={() => { showGraph(studyExample, "Working memory study example"); setProfile("study"); setOptionsOpen(false); }}>Open study example ↗</button>
          </div>
          <div className="options-section"><h3>Panels</h3><label className="options-row"><span>Show index</span><input type="checkbox" checked={indexOpen} onChange={(event) => setIndexOpen(event.target.checked)} /></label><label className="options-row"><span>Show inspector</span><input type="checkbox" checked={inspectorOpen} onChange={(event) => setInspectorOpen(event.target.checked)} /></label></div>
        </div>}
      </div>
      <span className="topbar-stats">{graph.nodes.length} nodes <i /> {graph.edges.length} relations</span>
    </header>

    <aside id="semantic-index" className="index-panel" aria-label="Semantic index" hidden={!indexOpen}>
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
      <button className="panel-kicker list-heading" onClick={() => kindList.current?.focus()}>NODE KINDS</button>
      <div ref={kindList} className="kind-list" role="group" aria-label="Node kinds" aria-keyshortcuts="ArrowUp ArrowDown ArrowLeft ArrowRight" tabIndex={-1} onClick={focusListOnClick} onKeyDown={moveInList}>
        <button className={`kind-filter ${kind === null ? "active" : ""}`} onClick={() => setKind(null)}><span>All kinds</span><span>{graph.nodes.length}</span></button>
        {view.kinds.map((entry) => <button key={entry.kind} className={`kind-filter ${kind === entry.kind ? "active" : ""}`} onClick={() => setKind(entry.kind)}><span><b className="kind-dot" style={{ background: colorForKind(entry.kind) }} />{entry.kind}</span><span>{entry.count}</span></button>)}
      </div>
      <div className="section-rule" />
      <button className="panel-kicker list-heading" onClick={() => nodeList.current?.focus()}>NODE INDEX</button>
      <div ref={nodeList} className="node-list" role="group" aria-label="Node index" aria-keyshortcuts="ArrowUp ArrowDown ArrowLeft ArrowRight" tabIndex={-1} onClick={focusListOnClick} onKeyDown={moveInList}>{graph.nodes.filter((node) => matchedIds.has(node.unique_id)).map((node) => <button key={node.unique_id} className={`node-list-item ${selectedId === node.unique_id ? "active" : ""}`} onClick={() => navigate(node.unique_id)}><span className="node-list-id">#{node.unique_id}</span><span>{node.label}</span></button>)}</div>
    </aside>

    <main className="main-panel"><GraphCanvas graph={graph} selectedId={selectedId} matchedIds={matchedIds} onSelect={setSelectedId} onOpenCard={setStudyCardId} profile={profile} focus={focus} key={graph.graph_id + fileName} /></main>

    <aside id="semantic-inspector" className="inspector-panel" aria-label="Semantic inspector" hidden={!inspectorOpen}>
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
    {profile === "study" && studyCard && <StudyCardDialog node={studyCard} view={view} onClose={closeStudyCard} onNavigate={navigate} />}
  </div>;
}
