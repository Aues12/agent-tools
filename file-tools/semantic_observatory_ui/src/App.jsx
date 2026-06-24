import { useMemo, useState } from "react";
import { SemanticCard } from "./components/SemanticCard/SemanticCard.jsx";
import { filterOptions, semanticCards } from "./data/semanticCard.js";

const tabs = ["Overview", "Relations", "DFG", "Trace"];

function matchesFilter(card, filters) {
  return Object.entries(filters).every(([key, value]) => {
    return value === "all" || card[key] === value;
  });
}

function matchesQuery(card, query) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    return true;
  }

  return [
    card.title,
    card.kind,
    card.role,
    card.phase,
    card.module,
    card.summary,
    card.source.displayPath,
  ]
    .join(" ")
    .toLowerCase()
    .includes(normalized);
}

function lineRange(source) {
  return `${source.line}-${source.endLine}`;
}

function relationLabel(relation) {
  return relation.label ? `${relation.kind} · ${relation.label}` : relation.kind;
}

export function App() {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState({
    kind: "all",
    role: "all",
    phase: "all",
    module: "all",
  });
  const [selectedId, setSelectedId] = useState(semanticCards[0]?.id);
  const [activeTab, setActiveTab] = useState("Overview");

  const visibleCards = useMemo(() => {
    return semanticCards.filter((card) => {
      return matchesQuery(card, query) && matchesFilter(card, filters);
    });
  }, [filters, query]);

  const selectedCard = useMemo(() => {
    return (
      semanticCards.find((card) => card.id === selectedId) ??
      visibleCards[0] ??
      semanticCards[0]
    );
  }, [selectedId, visibleCards]);

  function updateFilter(key, value) {
    setFilters((current) => ({
      ...current,
      [key]: value,
    }));
  }

  return (
    <main className="observatory-shell">
      <aside className="inspector-sidebar" aria-label="Semantic cards">
        <div className="sidebar-header">
          <p className="eyebrow">Semantic Observatory</p>
          <h1>Card Inspector</h1>
        </div>

        <label className="search-field">
          <span>Search</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="parse, builder, dfg"
          />
        </label>

        <div className="filter-grid" aria-label="Filters">
          {Object.entries(filterOptions).map(([key, values]) => (
            <label key={key} className="select-field">
              <span>{key}</span>
              <select
                value={filters[key]}
                onChange={(event) => updateFilter(key, event.target.value)}
              >
                {values.map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </label>
          ))}
        </div>

        <div className="card-list" aria-label="Card list">
          {visibleCards.map((card) => (
            <button
              key={card.id}
              type="button"
              className={
                card.id === selectedCard.id
                  ? "card-list__item card-list__item--active"
                  : "card-list__item"
              }
              onClick={() => {
                setSelectedId(card.id);
                setActiveTab("Overview");
              }}
            >
              <span className="card-list__title">{card.title}</span>
              <span className="card-list__meta">
                {card.role} · {card.phase}
              </span>
            </button>
          ))}
        </div>
      </aside>

      <section className="inspector-main" aria-label="Selected semantic card">
        <div className="selected-layout">
          <SemanticCard card={selectedCard} />

          <section className="detail-panel" aria-label="Card details">
            <div className="tabs" role="tablist" aria-label="Detail views">
              {tabs.map((tab) => (
                <button
                  key={tab}
                  type="button"
                  role="tab"
                  aria-selected={activeTab === tab}
                  className={activeTab === tab ? "tab tab--active" : "tab"}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab}
                </button>
              ))}
            </div>

            {activeTab === "Overview" && (
              <div className="detail-view">
                <dl className="metadata-grid">
                  <div>
                    <dt>Kind</dt>
                    <dd>{selectedCard.kind}</dd>
                  </div>
                  <div>
                    <dt>Role</dt>
                    <dd>{selectedCard.role}</dd>
                  </div>
                  <div>
                    <dt>Phase</dt>
                    <dd>{selectedCard.phase}</dd>
                  </div>
                  <div>
                    <dt>Module</dt>
                    <dd>{selectedCard.module}</dd>
                  </div>
                  <div>
                    <dt>Depth</dt>
                    <dd>{selectedCard.depth}</dd>
                  </div>
                  <div>
                    <dt>Level</dt>
                    <dd>{selectedCard.level}</dd>
                  </div>
                </dl>
              </div>
            )}

            {activeTab === "Relations" && (
              <div className="detail-view relation-list">
                {(selectedCard.relations ?? []).map((relation) => (
                  <div key={`${relation.kind}-${relation.target}`} className="relation-row">
                    <span>{relationLabel(relation)}</span>
                    <strong>{relation.target}</strong>
                  </div>
                ))}
              </div>
            )}

            {activeTab === "DFG" && (
              <div className="detail-view dfg-view">
                {selectedCard.dfg ? (
                  <>
                    <div className="dfg-levels">
                      {selectedCard.dfg.nodes.map((node) => (
                        <div
                          key={node.id}
                          className="dfg-node"
                          style={{ "--depth": node.depth }}
                        >
                          <span className="dfg-node__name">{node.name}</span>
                          <span className="dfg-node__meta">
                            {node.kind} · flow {node.flowLevel} · depth {node.depth}
                          </span>
                        </div>
                      ))}
                    </div>
                    <div className="edge-list">
                      {selectedCard.dfg.edges.map((edge) => (
                        <div
                          key={`${edge.source}-${edge.target}-${edge.operation}`}
                          className="edge-row"
                        >
                          <span>{edge.source}</span>
                          <span>→</span>
                          <span>{edge.target}</span>
                          <strong>{edge.operation}</strong>
                        </div>
                      ))}
                    </div>
                  </>
                ) : (
                  <p className="empty-state">No local data-flow artifact.</p>
                )}
              </div>
            )}

            {activeTab === "Trace" && (
              <div className="detail-view trace-view">
                <div>
                  <span>Path</span>
                  <strong>{selectedCard.source.path}</strong>
                </div>
                <div>
                  <span>Lines</span>
                  <strong>{lineRange(selectedCard.source)}</strong>
                </div>
                <div>
                  <span>ID</span>
                  <strong>{selectedCard.id}</strong>
                </div>
              </div>
            )}
          </section>
        </div>
      </section>
    </main>
  );
}
