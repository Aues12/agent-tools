import { useEffect, useRef } from "react";
import { cardForNode } from "../data/card.ts";
import { colorForKind, type GraphEdge, type GraphNode, type GraphView } from "../data/graph.ts";

interface Props {
  node: GraphNode;
  view: GraphView;
  onClose: () => void;
  onNavigate: (id: number) => void;
}

export function StudyCardDialog({ node, view, onClose, onNavigate }: Props) {
  const dialog = useRef<HTMLDialogElement>(null);
  const body = useRef<HTMLDivElement>(null);
  const closeButton = useRef<HTMLButtonElement>(null);
  const card = cardForNode(node);
  const otherAttributes = Object.entries(node.attributes).filter(([key]) => key !== "card");

  useEffect(() => {
    const element = dialog.current;
    if (!element) return;
    element.showModal();
    return () => { if (element.open) element.close(); };
  }, []);
  useEffect(() => {
    if (body.current) body.current.scrollTop = 0;
    closeButton.current?.focus();
  }, [node.unique_id]);

  function relation(edge: GraphEdge, otherId: number) {
    const other = view.byId.get(otherId)!;
    return <button className="study-relation" key={edge.unique_id} onClick={() => onNavigate(otherId)}>
      <span className="study-relation-kind">{edge.kind.replaceAll("_", " ")}{edge.label ? ` · ${edge.label}` : ""}</span>
      <span>{other.label} <span className="study-relation-id">#{other.unique_id} ↗</span></span>
    </button>;
  }

  return <dialog ref={dialog} className="study-dialog" aria-labelledby="study-card-title" onCancel={(event) => { event.preventDefault(); onClose(); }} onClick={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <div className="study-dialog-header">
      <span className="study-dialog-eyebrow">STUDY CARD · NODE #{node.unique_id}</span>
      <button ref={closeButton} className="study-dialog-close" onClick={onClose} aria-label="Close study card">×</button>
    </div>
    <div className="study-dialog-body" ref={body}>
      <span className="study-dialog-kind" style={{ color: colorForKind(node.kind), borderColor: colorForKind(node.kind) }}>{node.kind}</span>
      <h2 id="study-card-title">{node.label}</h2>
      {card?.summary && <p className="study-dialog-summary">{card.summary}</p>}
      {card?.sections.map((section, index) => <section className="study-dialog-section" key={`${index}-${section.heading}`}><h3>{section.heading}</h3><p>{section.body}</p></section>)}
      {!card?.summary && !card?.sections.length && <p className="study-dialog-empty">No extended notes are included for this node.</p>}
      {otherAttributes.length > 0 && <section className="study-dialog-section"><h3>Other attributes</h3><dl className="study-attributes">{otherAttributes.map(([key, value]) => <div key={key}><dt>{key}</dt><dd>{typeof value === "string" ? value : JSON.stringify(value)}</dd></div>)}</dl></section>}
      {card && card.sources.length > 0 && <section className="study-dialog-section"><h3>Sources</h3><ul className="study-sources">{card.sources.map((source) => <li key={source.url}><a href={source.url} target="_blank" rel="noopener noreferrer">{source.label} ↗</a></li>)}</ul></section>}
      <section className="study-dialog-section"><h3>Connections</h3>
        <div className="study-connections"><div><h4>Incoming <span>{view.incoming.get(node.unique_id)?.length ?? 0}</span></h4>{view.incoming.get(node.unique_id)?.map((edge) => relation(edge, edge.source))}</div><div><h4>Outgoing <span>{view.outgoing.get(node.unique_id)?.length ?? 0}</span></h4>{view.outgoing.get(node.unique_id)?.map((edge) => relation(edge, edge.target))}</div></div>
      </section>
    </div>
  </dialog>;
}
