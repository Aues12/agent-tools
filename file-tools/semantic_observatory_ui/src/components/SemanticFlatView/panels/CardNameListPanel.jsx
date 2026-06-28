import { useEffect, useRef } from "react";

export function CardNameListPanel({ cards, selectedCard, totalCount, onSelectCard }) {
  const rowRefs = useRef(new Map());

  useEffect(() => {
    if (!selectedCard) {
      return;
    }
    rowRefs.current.get(selectedCard.id)?.scrollIntoView({
      block: "nearest",
    });
  }, [selectedCard]);

  function moveSelection(direction) {
    if (cards.length === 0) {
      return;
    }
    const currentIndex = Math.max(
      0,
      cards.findIndex((card) => card.id === selectedCard?.id),
    );
    const nextIndex = Math.min(
      cards.length - 1,
      Math.max(0, currentIndex + direction),
    );
    const nextId = cards[nextIndex].id;
    onSelectCard(nextId);
    window.requestAnimationFrame(() => {
      rowRefs.current.get(nextId)?.focus();
    });
  }

  function handleKeyDown(event) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      moveSelection(1);
    }
    if (event.key === "ArrowUp") {
      event.preventDefault();
      moveSelection(-1);
    }
  }

  return (
    <section
      className="card-name-panel flat-panel"
      aria-label="Atlas index"
      onKeyDown={handleKeyDown}
    >
      <div className="panel-header panel-header--compact">
        <p className="eyebrow">Atlas Index</p>
        <h2>{cards.length} / {totalCount}</h2>
      </div>

      <div className="card-name-list" aria-label="Card name list">
        {cards.length === 0 && (
          <p className="empty-state">No cards match the current index.</p>
        )}
        {cards.map((card) => (
          <button
            key={card.id}
            ref={(element) => {
              if (element) {
                rowRefs.current.set(card.id, element);
              } else {
                rowRefs.current.delete(card.id);
              }
            }}
            type="button"
            className={
              card.id === selectedCard?.id
                ? "card-name-row card-name-row--active"
                : "card-name-row"
            }
            onClick={() => onSelectCard(card.id)}
          >
            <span className="card-name-row__seal" aria-hidden="true">
              {card.phase.charAt(0)}
            </span>
            <span className="card-name-row__body">
              <span className="card-name-row__title">{card.title}</span>
              <span className="card-name-row__meta">
                {card.role} · {card.phase}
              </span>
            </span>
          </button>
        ))}
      </div>
    </section>
  );
}
