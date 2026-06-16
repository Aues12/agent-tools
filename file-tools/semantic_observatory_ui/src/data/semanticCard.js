export const phaseSymbols = {
  Discovery: "🜁",
  Understanding: "▽",
  Transformation: "△",
  Manifestation: "🜃",
};

// This is a temporary view-model for the first prototype card.
export const semanticCard = {
  id: "function:semantic_ast.call_graph.build_call_graph",
  kind: "function",
  title: "build_call_graph",
  depth: 2,
  level: 4,
  summary: "Builds a deterministic direct call graph from compressed semantic AST nodes.",
  role: "Builder",
  phase: "Manifestation",
  source: {
    path: "file-tools/semantic_ast/call_graph/call_graph.py",
    displayPath: "semantic_ast/call_graph.py",
    line: 18,
    endLine: 82,
  },
};
