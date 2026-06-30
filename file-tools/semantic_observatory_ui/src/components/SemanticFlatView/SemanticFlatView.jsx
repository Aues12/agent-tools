import { useMemo, useState } from "react";
import { analyzePythonFile } from "../../api/analyzePythonFile.js";
import {
  filterOptions as sampleFilterOptions,
  semanticCards as sampleSemanticCards,
} from "../../data/semanticCard.js";
import { CardDetailPanel } from "./panels/CardDetailPanel.jsx";
import { CardNameListPanel } from "./panels/CardNameListPanel.jsx";
import { CardViewPanel } from "./panels/CardViewPanel.jsx";
import { IndexPanel } from "./panels/IndexPanel.jsx";

const tabs = ["Overview", "Relations", "DFG", "Trace"];
const designModes = [
  { id: "modern", label: "Modern" },
  { id: "ancient", label: "Ancient" },
];
const sortOptions = [
  { id: "source", label: "Source order" },
  { id: "level-desc", label: "Level high to low" },
  { id: "level-asc", label: "Level low to high" },
  { id: "title", label: "Title A-Z" },
];
const defaultFilters = {
  kind: "all",
  role: "all",
  phase: "all",
  module: "all",
};

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

function sortCards(cards, sortMode) {
  const indexedCards = cards.map((card, index) => ({ card, index }));
  indexedCards.sort((left, right) => {
    if (sortMode === "level-desc") {
      return right.card.level - left.card.level || left.index - right.index;
    }
    if (sortMode === "level-asc") {
      return left.card.level - right.card.level || left.index - right.index;
    }
    if (sortMode === "title") {
      return left.card.title.localeCompare(right.card.title) || left.index - right.index;
    }
    return left.index - right.index;
  });
  return indexedCards.map(({ card }) => card);
}

export function SemanticFlatView() {
  const [uiData, setUiData] = useState({
    semanticCards: sampleSemanticCards,
    filterOptions: sampleFilterOptions,
    sourceName: "Sample data",
  });
  const [analysisStatus, setAnalysisStatus] = useState({
    state: "sample",
    message: "Sample data",
  });
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState(defaultFilters);
  const [sortMode, setSortMode] = useState("source");
  const [selectedId, setSelectedId] = useState(sampleSemanticCards[0]?.id);
  const [activeTab, setActiveTab] = useState("Overview");
  const [designMode, setDesignMode] = useState("ancient");
  const semanticCards = uiData.semanticCards;
  const filterOptions = uiData.filterOptions;

  const visibleCards = useMemo(() => {
    const filteredCards = semanticCards.filter((card) => {
      return matchesQuery(card, query) && matchesFilter(card, filters);
    });
    return sortCards(filteredCards, sortMode);
  }, [filters, query, semanticCards, sortMode]);

  const selectedCard = useMemo(() => {
    return (
      semanticCards.find((card) => card.id === selectedId) ??
      visibleCards[0] ??
      semanticCards[0]
    );
  }, [selectedId, semanticCards, visibleCards]);

  async function analyzeFile(file) {
    setAnalysisStatus({
      state: "loading",
      message: `Analyzing ${file.name}`,
    });

    try {
      const analysis = await analyzePythonFile(file);
      const nextCards = analysis.ui.semanticCards;
      setUiData({
        semanticCards: nextCards,
        filterOptions: analysis.ui.filterOptions,
        sourceName: analysis.source.displayName,
      });
      setFilters(defaultFilters);
      setQuery("");
      setSelectedId(nextCards[0]?.id);
      setActiveTab("Overview");
      setAnalysisStatus({
        state: "ready",
        message: `${analysis.source.displayName} · ${analysis.ui.stats.cards} cards`,
      });
    } catch (error) {
      setAnalysisStatus({
        state: "error",
        message: error instanceof Error ? error.message : "Semantic analysis failed.",
      });
    }
  }

  function updateFilter(key, value) {
    setFilters((current) => ({
      ...current,
      [key]: value,
    }));
  }

  function selectCard(cardId) {
    setSelectedId(cardId);
    setActiveTab("Overview");
  }

  return (
    <main className={`observatory-shell theme-${designMode}`}>
      <IndexPanel
        designMode={designMode}
        designModes={designModes}
        filterOptions={filterOptions}
        filters={filters}
        query={query}
        sortMode={sortMode}
        sortOptions={sortOptions}
        onDesignModeChange={setDesignMode}
        onFileAnalyze={analyzeFile}
        onFilterChange={updateFilter}
        onQueryChange={setQuery}
        onSortModeChange={setSortMode}
        sourceName={uiData.sourceName}
        status={analysisStatus}
      />
      <CardNameListPanel
        cards={visibleCards}
        selectedCard={selectedCard}
        totalCount={semanticCards.length}
        onSelectCard={selectCard}
      />
      <CardViewPanel card={selectedCard} />
      <CardDetailPanel
        activeTab={activeTab}
        card={selectedCard}
        cardIds={new Set(semanticCards.map((card) => card.id))}
        tabs={tabs}
        onSelectCard={selectCard}
        onTabChange={setActiveTab}
      />
    </main>
  );
}
