import { SemanticCard } from "../../SemanticCard/SemanticCard.jsx";

export function CardViewPanel({ card }) {
  if (!card) {
    return (
      <section className="card-view-panel" aria-label="Open semantic card">
        <div className="panel-header panel-header--inline">
          <p className="eyebrow">Open Page</p>
        </div>
        <p className="empty-state">No card selected.</p>
      </section>
    );
  }

  return (
    <section className="card-view-panel" aria-label="Open semantic card">
      <div className="panel-header panel-header--inline">
        <p className="eyebrow">Open Page</p>
        <span>{card.module}</span>
      </div>
      <SemanticCard card={card} />
    </section>
  );
}
