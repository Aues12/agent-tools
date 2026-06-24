export const phaseSymbols = {
  Discovery: "🜁",
  Understanding: "▽",
  Transformation: "△",
  Manifestation: "🜃",
};

export const semanticCards = [
  {
    id: "function:semantic_ast.ast_parsing.parse_file",
    kind: "function",
    title: "parse_file",
    depth: 1,
    level: 2,
    summary: "Reads Python source from a path and returns a normalized semantic AST module tree.",
    role: "Parser",
    phase: "Understanding",
    module: "semantic_ast.ast_parsing",
    source: {
      path: "file-tools/semantic_ast/ast_parsing/ast_parser.py",
      displayPath: "semantic_ast/ast_parsing/ast_parser.py",
      line: 70,
      endLine: 76,
    },
    relations: [
      {
        kind: "uses",
        target: "Path.read_text",
        label: "reads source text",
      },
      {
        kind: "calls",
        target: "parse_source",
        label: "normalizes parsed source",
      },
    ],
    dfg: {
      nodes: [
        { id: "parse_file:path", name: "path", kind: "parameter", flowLevel: 0, depth: 0 },
        { id: "parse_file:source", name: "source", kind: "binding", flowLevel: 1, depth: 1 },
        { id: "parse_file:tree", name: "tree", kind: "return_value", flowLevel: 2, depth: 1 },
      ],
      edges: [
        { source: "path", target: "source", operation: "read_text" },
        { source: "source", target: "tree", operation: "parse_source" },
      ],
    },
  },
  {
    id: "function:semantic_ast.call_graph.build_call_graph",
    kind: "function",
    title: "build_call_graph",
    depth: 2,
    level: 4,
    summary: "Builds a deterministic direct call graph from semantic AST function nodes.",
    role: "Builder",
    phase: "Manifestation",
    module: "semantic_ast.call_graph",
    source: {
      path: "file-tools/semantic_ast/call_graph/call_graph.py",
      displayPath: "semantic_ast/call_graph.py",
      line: 18,
      endLine: 82,
    },
    relations: [
      {
        kind: "calls",
        target: "_collect_functions",
        label: "collects local function nodes",
      },
      {
        kind: "calls",
        target: "_compute_levels",
        label: "assigns call graph height",
      },
    ],
  },
  {
    id: "function:semantic_dfg.build_dfg",
    kind: "function",
    title: "build_dfg",
    depth: 1,
    level: 3,
    summary: "Builds a local data-flow graph that records function-internal value movement.",
    role: "Builder",
    phase: "Manifestation",
    module: "semantic_dfg",
    source: {
      path: "file-tools/semantic_dfg/builder.py",
      displayPath: "semantic_dfg/builder.py",
      line: 23,
      endLine: 47,
    },
    relations: [
      {
        kind: "uses",
        target: "semantic_ast",
        label: "consumes normalized structure",
      },
      {
        kind: "produces",
        target: "data_flow_graph",
        label: "emits value-flow localization",
      },
    ],
    dfg: {
      nodes: [
        { id: "build_dfg:tree", name: "tree", kind: "parameter", flowLevel: 0, depth: 0 },
        { id: "build_dfg:functions", name: "functions", kind: "binding", flowLevel: 1, depth: 1 },
        { id: "build_dfg:function_graphs", name: "function_graphs", kind: "binding", flowLevel: 2, depth: 1 },
        { id: "build_dfg:result", name: "data_flow_graph", kind: "return_value", flowLevel: 3, depth: 1 },
      ],
      edges: [
        { source: "tree", target: "functions", operation: "_collect_functions" },
        { source: "functions", target: "function_graphs", operation: "build_function" },
        { source: "function_graphs", target: "data_flow_graph", operation: "return" },
      ],
    },
  },
  {
    id: "function:semantic_cards.build_cards",
    kind: "function",
    title: "build_cards",
    depth: 1,
    level: 3,
    summary: "Turns a normalized semantic AST tree into navigable cards and relation records.",
    role: "Builder",
    phase: "Manifestation",
    module: "semantic_cards",
    source: {
      path: "file-tools/semantic_cards/tool.py",
      displayPath: "semantic_cards/tool.py",
      line: 51,
      endLine: 61,
    },
    relations: [
      {
        kind: "uses",
        target: "semantic_ast",
        label: "reads structural localization",
      },
      {
        kind: "produces",
        target: "semantic_cards",
        label: "emits card/interface localization",
      },
    ],
  },
];

export const filterOptions = {
  kind: ["all", ...new Set(semanticCards.map((card) => card.kind))],
  role: ["all", ...new Set(semanticCards.map((card) => card.role))],
  phase: ["all", ...new Set(semanticCards.map((card) => card.phase))],
  module: ["all", ...new Set(semanticCards.map((card) => card.module))],
};
