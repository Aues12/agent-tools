import "./SemanticCard.css";
import { phaseSymbols } from "../../data/semanticCard.js";

function titleCase(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function lineRange(source) {
  return `${source.line}-${source.endLine}`;
}

export function SemanticCard({ card }) {
  const phaseSymbol = phaseSymbols[card.phase] ?? "?";

  return (
    <article className="semantic-card" aria-labelledby={`${card.id}-title`}>
      <header className="semantic-card__meta">
        <span>{titleCase(card.kind)}</span>
        <span>Lines {lineRange(card.source)}</span>
      </header>

      <div className="semantic-card__body">
        <div>
          <h1 id={`${card.id}-title`} className="semantic-card__title">
            {card.title}
          </h1>
          <p className="semantic-card__subtle">
            Depth {card.depth} / Level {card.level}
          </p>
        </div>

        <button
          className="semantic-card__action"
          type="button"
          aria-label={`${card.phase} phase symbol`}
          title={`${card.phase} · ${phaseSymbol}`}
        >
          <span className="semantic-card__action-symbol" aria-hidden="true">
            {phaseSymbol}
          </span>
        </button>
      </div>

      <p className="semantic-card__summary">{card.summary}</p>

      <div className="semantic-card__chips" aria-label="Semantic tags">
        <span className="semantic-card__chip">Role / {card.role}</span>
        <span className="semantic-card__chip">Phase / {card.phase}</span>
      </div>

      <footer className="semantic-card__trace">{card.source.displayPath}</footer>
    </article>
  );
}
