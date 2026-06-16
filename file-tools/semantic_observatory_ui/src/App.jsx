import { SemanticCard } from "./components/SemanticCard/SemanticCard.jsx";
import { semanticCard } from "./data/semanticCard.js";

export function App() {
  return (
    <main className="observatory">
      <section className="stage" aria-label="Semantic card prototype">
        <SemanticCard card={semanticCard} />
      </section>
    </main>
  );
}
