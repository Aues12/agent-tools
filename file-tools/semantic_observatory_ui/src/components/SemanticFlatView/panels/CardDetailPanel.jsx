function lineRange(source) {
  return `${source.line}-${source.endLine}`;
}

function relationTitle(relation) {
  if (relation.label) {
    return relation.label;
  }
  return relation.target.split(/[.:]/).filter(Boolean).at(-1) ?? relation.target;
}

export function CardDetailPanel({
  activeTab,
  card,
  cardIds,
  tabs,
  onSelectCard,
  onTabChange,
}) {
  if (!card) {
    return (
      <section className="detail-panel flat-panel" aria-label="Research notes">
        <div className="panel-header panel-header--compact">
          <p className="eyebrow">Research Notes</p>
          <h2>Empty</h2>
        </div>
        <p className="empty-state">No card selected.</p>
      </section>
    );
  }

  return (
    <section className="detail-panel flat-panel" aria-label="Research notes">
      <div className="panel-header panel-header--compact">
        <p className="eyebrow">Research Notes</p>
        <h2>{activeTab}</h2>
      </div>

      <div className="tabs" role="tablist" aria-label="Detail views">
        {tabs.map((tab) => (
          <button
            key={tab}
            type="button"
            role="tab"
            aria-selected={activeTab === tab}
            className={activeTab === tab ? "tab tab--active" : "tab"}
            onClick={() => onTabChange(tab)}
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
              <dd>{card.kind}</dd>
            </div>
            <div>
              <dt>Role</dt>
              <dd>{card.role}</dd>
            </div>
            <div>
              <dt>Phase</dt>
              <dd>{card.phase}</dd>
            </div>
            <div>
              <dt>Module</dt>
              <dd>{card.module}</dd>
            </div>
            <div>
              <dt>Depth</dt>
              <dd>{card.depth}</dd>
            </div>
            <div>
              <dt>Level</dt>
              <dd>{card.level}</dd>
            </div>
          </dl>
        </div>
      )}

      {activeTab === "Relations" && (
        <div className="detail-view relation-list">
          {(card.relations ?? []).map((relation) => {
            const isLinked = cardIds.has(relation.target);
            const Element = isLinked ? "button" : "div";
            return (
              <Element
                key={`${relation.kind}-${relation.target}`}
                type={isLinked ? "button" : undefined}
                className={isLinked ? "relation-row relation-row--link" : "relation-row"}
                onClick={isLinked ? () => onSelectCard(relation.target) : undefined}
              >
                <span className="relation-row__kind">{relation.kind}</span>
                <strong className="relation-row__title">{relationTitle(relation)}</strong>
                <span className="relation-row__target">{relation.target}</span>
              </Element>
            );
          })}
        </div>
      )}

      {activeTab === "DFG" && (
        <div className="detail-view dfg-view">
          {card.dfg ? (
            <>
              <div className="dfg-levels">
                {card.dfg.nodes.map((node) => (
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
                {card.dfg.edges.map((edge) => (
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
            <strong>{card.source.path}</strong>
          </div>
          <div>
            <span>Lines</span>
            <strong>{lineRange(card.source)}</strong>
          </div>
          <div>
            <span>ID</span>
            <strong>{card.id}</strong>
          </div>
        </div>
      )}
    </section>
  );
}
