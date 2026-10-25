import type { DisplaySource } from "../data/sources.ts";

function kindLabel(source: DisplaySource): string {
  if (source.kind === "agent_interpretation") return "Agent interpretation";
  if (source.kind === "file") return "Local file";
  if (source.kind === "online" || source.kind === "url" || source.href) return "Online source";
  if (source.kind === "unknown") return "Unresolved reference";
  return source.kind.replaceAll("_", " ");
}

export function StudySources({ sources }: { sources: DisplaySource[] }) {
  if (!sources.length) return null;
  return <section className="study-dialog-section">
    <h3 className="study-sources-heading">Sources <span>{sources.length}</span></h3>
    <div className="study-source-list">
      {sources.map((source) => {
        const content = <>
          <span className={`study-source-kind${source.interpretation ? " study-source-kind-interpretation" : ""}`}>{kindLabel(source)}</span>
          <span className="study-source-title">{source.label}{source.href && <span className="study-source-arrow" aria-hidden="true">↗</span>}</span>
          {(source.detail || source.sourceId) && <span className="study-source-meta">
            {source.detail && <span>{source.detail}</span>}
            {source.sourceId && <span className="study-source-id">{source.sourceId}</span>}
          </span>}
        </>;
        return source.href
          ? <a className="study-source-card study-source-link" key={source.key} href={source.href} target="_blank" rel="noopener noreferrer" aria-label={`${source.label} (opens in new tab)`}>{content}</a>
          : <div className="study-source-card" key={source.key}>{content}</div>;
      })}
    </div>
  </section>;
}
