"""Render Semantic CPG artifacts as small local HTML graph views."""

from __future__ import annotations

import html
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any


_OPERATIONS = {"render_cpg_html", "render_cpg_file"}
_DEFAULT_MAX_NODES = 200


def render_cpg_html(
    cpg: Mapping[str, Any],
    title: str | None = None,
    max_nodes: int = _DEFAULT_MAX_NODES,
) -> str:
    """Return a self-contained HTML debug graph for a Semantic CPG."""
    graph = _graph_model(cpg, max_nodes=max_nodes)
    display_title = title or _default_title(cpg)
    data_json = _script_json(graph)
    escaped_title = html.escape(display_title, quote=True)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <style>
    :root {{
      color-scheme: light;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #20252b;
      background: #f3f5f2;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-width: 320px; min-height: 100vh; }}
    button, input {{ font: inherit; }}
    .shell {{
      min-height: 100vh;
      display: grid;
      grid-template-columns: 260px minmax(460px, 1fr) 320px;
      background: #eef1f0;
    }}
    aside, main {{ min-width: 0; }}
    .panel {{
      height: 100vh;
      overflow: auto;
      padding: 18px;
      border-right: 1px solid #ccd5d1;
      background: #f8faf7;
    }}
    .details {{ border-right: 0; border-left: 1px solid #ccd5d1; }}
    h1, h2 {{ margin: 0; line-height: 1.15; letter-spacing: 0; }}
    h1 {{ font-size: 20px; color: #1c2a2b; }}
    h2 {{ margin-top: 18px; font-size: 13px; color: #334240; text-transform: uppercase; }}
    .meta {{ margin-top: 8px; color: #65716e; font-size: 12px; line-height: 1.45; }}
    .filter-list {{ display: grid; gap: 8px; margin-top: 10px; }}
    label {{
      display: grid;
      grid-template-columns: 18px minmax(0, 1fr) auto;
      gap: 8px;
      align-items: center;
      color: #263133;
      font-size: 12px;
    }}
    label span {{ min-width: 0; overflow-wrap: anywhere; }}
    .swatch {{ width: 10px; height: 10px; border-radius: 999px; border: 1px solid rgba(0,0,0,.18); }}
    .canvas {{
      height: 100vh;
      min-width: 0;
      position: relative;
      background:
        linear-gradient(#e7ece9 1px, transparent 1px),
        linear-gradient(90deg, #e7ece9 1px, transparent 1px),
        #f3f5f2;
      background-size: 28px 28px;
      overflow: auto;
    }}
    .toolbar {{
      position: static;
      min-height: 40px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin: 14px;
      padding: 10px 12px;
      color: #2b3837;
      background: rgba(248,250,247,.92);
      border: 1px solid #cbd4d0;
      border-radius: 8px;
      font-size: 12px;
      backdrop-filter: blur(8px);
      pointer-events: none;
    }}
    .toolbar strong {{ font-size: 13px; }}
    svg {{ display: block; }}
    .lane-label {{ fill: #56625f; font-size: 11px; font-weight: 700; text-anchor: middle; pointer-events: none; }}
    .lane-line {{ stroke: #d7dfdb; stroke-width: 1; pointer-events: none; }}
    .source-line {{ fill: #7a8582; font-size: 10px; text-anchor: end; pointer-events: none; }}
    .edge {{ stroke: #9aa5a1; stroke-width: 1.4; opacity: .62; pointer-events: none; }}
    .edge--corresponds_to {{ stroke-dasharray: 5 4; }}
    .edge-hit {{ stroke: transparent; stroke-width: 10; cursor: pointer; pointer-events: stroke; }}
    .node-hit {{ fill: transparent; stroke: transparent; pointer-events: all; cursor: pointer; }}
    .node circle:not(.node-hit) {{ stroke: rgba(0,0,0,.28); stroke-width: 1.2; pointer-events: none; }}
    .node text {{ pointer-events: none; fill: #253032; font-size: 11px; text-anchor: middle; }}
    .node:hover circle {{ stroke: #172322; stroke-width: 2; }}
    .empty {{
      position: absolute;
      inset: 0;
      display: grid;
      place-items: center;
      color: #65716e;
      font-size: 14px;
      pointer-events: none;
    }}
    .empty[hidden] {{ display: none !important; }}
    pre {{
      margin: 10px 0 0;
      padding: 10px;
      overflow: auto;
      color: #253032;
      background: #eef2ef;
      border: 1px solid #d2dad6;
      border-radius: 8px;
      font-size: 11px;
      line-height: 1.45;
    }}
    .kv {{ display: grid; gap: 8px; margin-top: 12px; font-size: 12px; }}
    .kv div {{ min-width: 0; }}
    .kv strong {{ display: block; margin-bottom: 2px; color: #56625f; font-size: 10px; text-transform: uppercase; }}
    .kv span {{ overflow-wrap: anywhere; }}
  </style>
</head>
<body>
  <div class="shell">
    <aside class="panel">
      <h1>{escaped_title}</h1>
      <p class="meta" id="graphMeta"></p>
      <h2>Origins</h2>
      <div class="filter-list" id="originFilters"></div>
      <h2>Edge Kinds</h2>
      <div class="filter-list" id="edgeFilters"></div>
      <h2>Edge Origins</h2>
      <div class="filter-list" id="edgeOriginFilters"></div>
    </aside>
    <main class="canvas">
      <div class="toolbar">
        <strong id="visibleCounts">Graph</strong>
        <span>Click nodes or edges for details</span>
      </div>
      <svg id="graph" role="img" aria-label="Semantic CPG graph"></svg>
      <div class="empty" id="emptyState" hidden>No visible nodes for current filters.</div>
    </main>
    <aside class="panel details">
      <h1>Selection</h1>
      <div id="selection" class="meta">Nothing selected.</div>
    </aside>
  </div>
  <script>
    const GRAPH = {data_json};
    const ORIGIN_COLORS = {{
      semantic_ast: "#8a9290",
      semantic_cfg: "#3e7fbf",
      semantic_dfg: "#3f946c",
      call_graph: "#875db8",
      semantic_cpg: "#c69432",
      unknown: "#68716f"
    }};
    const EDGE_COLORS = {{
      contains: "#9aa5a1",
      controls: "#3e7fbf",
      depends_on: "#3f946c",
      calls: "#875db8",
      corresponds_to: "#c69432"
    }};
    const state = {{
      origins: new Set(GRAPH.origins),
      edgeKinds: new Set(GRAPH.edgeKinds),
      edgeOrigins: new Set(GRAPH.edgeOrigins)
    }};

    const svg = document.getElementById("graph");
    const selection = document.getElementById("selection");
    const visibleCounts = document.getElementById("visibleCounts");
    const graphMeta = document.getElementById("graphMeta");
    const emptyState = document.getElementById("emptyState");

    graphMeta.textContent = `${{GRAPH.nodes.length}} nodes, ${{GRAPH.edges.length}} edges` +
      (GRAPH.truncated ? ` · truncated from ${{GRAPH.originalNodeCount}} nodes` : "");

    function colorForOrigin(origin) {{
      return ORIGIN_COLORS[origin] || ORIGIN_COLORS.unknown;
    }}

    function colorForEdge(kind) {{
      return EDGE_COLORS[kind] || "#9aa5a1";
    }}

    function colorForNode(node) {{
      if (node.kind === "value_parameter") return "#e0b83f";
      return colorForOrigin(node.originTool || "unknown");
    }}

    function makeFilters(containerId, values, activeSet, colorFn) {{
      const container = document.getElementById(containerId);
      container.innerHTML = "";
      values.forEach((value) => {{
        const label = document.createElement("label");
        const input = document.createElement("input");
        input.type = "checkbox";
        input.checked = activeSet.has(value);
        input.addEventListener("change", () => {{
          if (input.checked) activeSet.add(value);
          else activeSet.delete(value);
          render();
        }});
        const text = document.createElement("span");
        text.textContent = value;
        const swatch = document.createElement("i");
        swatch.className = "swatch";
        swatch.style.background = colorFn(value);
        label.append(input, text, swatch);
        container.append(label);
      }});
    }}

    function orderedOrigins(nodes) {{
      const preferred = ["semantic_ast", "semantic_cfg", "semantic_dfg", "call_graph", "semantic_cpg", "unknown"];
      const present = new Set(nodes.map((node) => node.originTool || "unknown"));
      const ordered = preferred.filter((origin) => present.has(origin));
      Array.from(present).sort().forEach((origin) => {{
        if (!ordered.includes(origin)) ordered.push(origin);
      }});
      return ordered;
    }}

    function layout(nodes, viewportWidth, viewportHeight) {{
      const lanes = orderedOrigins(nodes);
      const laneWidth = 230;
      const top = 84;
      const bottom = 48;
      const left = 74;
      const lineHeight = 82;
      const lineValues = nodes
        .map((node) => Number.isInteger(node.line) ? node.line : null)
        .filter((line) => line !== null);
      const minLine = lineValues.length ? Math.min(...lineValues) : 1;
      const maxLine = lineValues.length ? Math.max(...lineValues) : 1;
      const visibleLines = Array.from(new Set(lineValues)).sort((left, right) => left - right);
      if (visibleLines.length === 0) visibleLines.push(1);
      const lineIndex = new Map(visibleLines.map((line, index) => [line, index]));
      const height = Math.max(viewportHeight, top + (visibleLines.length * lineHeight) + bottom + 80);
      const width = Math.max(viewportWidth, left + lanes.length * laneWidth + 60);
      const laneByOrigin = new Map(lanes.map((origin, index) => [origin, index]));
      const stackCounts = new Map();

      nodes
        .slice()
        .sort((leftNode, rightNode) => (
          (leftNode.line ?? 999999) - (rightNode.line ?? 999999) ||
          (leftNode.endLine ?? 999999) - (rightNode.endLine ?? 999999) ||
          (leftNode.kind || "").localeCompare(rightNode.kind || "") ||
          leftNode.id.localeCompare(rightNode.id)
        ))
        .forEach((node) => {{
          const origin = node.originTool || "unknown";
          const laneIndex = laneByOrigin.get(origin) ?? lanes.length;
          const line = Number.isInteger(node.line) ? node.line : maxLine + 1;
          const stackKey = `${{origin}}:${{line}}`;
          const stackIndex = stackCounts.get(stackKey) || 0;
          stackCounts.set(stackKey, stackIndex + 1);
          const compactIndex = lineIndex.has(line) ? lineIndex.get(line) : visibleLines.length;
          node.x = left + laneIndex * laneWidth + laneWidth / 2;
          node.y = top + compactIndex * lineHeight + stackIndex * 22;
        }});

      return {{ width, height, lanes, laneWidth, left, top, visibleLines, lineHeight }};
    }}

    function render() {{
      const viewportWidth = svg.parentElement.clientWidth || 800;
      const viewportHeight = svg.parentElement.clientHeight || 600;
      const nodes = GRAPH.nodes.filter((node) => state.origins.has(node.originTool || "unknown"));
      const nodeIds = new Set(nodes.map((node) => node.id));
      const edges = GRAPH.edges.filter((edge) => (
        state.edgeKinds.has(edge.kind) &&
        state.edgeOrigins.has(edge.originTool || "unknown") &&
        nodeIds.has(edge.source) &&
        nodeIds.has(edge.target)
      ));
      const layoutInfo = layout(nodes, viewportWidth, viewportHeight);
      const nodeById = new Map(nodes.map((node) => [node.id, node]));
      svg.setAttribute("width", layoutInfo.width);
      svg.setAttribute("height", layoutInfo.height);
      svg.setAttribute("viewBox", `0 0 ${{layoutInfo.width}} ${{layoutInfo.height}}`);
      svg.innerHTML = "";
      emptyState.hidden = nodes.length !== 0;
      visibleCounts.textContent = `${{nodes.length}} visible nodes · ${{edges.length}} visible edges`;

      layoutInfo.lanes.forEach((origin, index) => {{
        const x = layoutInfo.left + index * layoutInfo.laneWidth + layoutInfo.laneWidth / 2;
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", x);
        line.setAttribute("y1", 46);
        line.setAttribute("x2", x);
        line.setAttribute("y2", layoutInfo.height - 24);
        line.setAttribute("class", "lane-line");
        svg.append(line);
        const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
        label.setAttribute("x", x);
        label.setAttribute("y", 34);
        label.setAttribute("class", "lane-label");
        label.textContent = origin;
        svg.append(label);
      }});

      layoutInfo.visibleLines.forEach((line, index) => {{
        const y = layoutInfo.top + index * layoutInfo.lineHeight;
        const marker = document.createElementNS("http://www.w3.org/2000/svg", "text");
        marker.setAttribute("x", 58);
        marker.setAttribute("y", y + 4);
        marker.setAttribute("class", "source-line");
        marker.textContent = `L${{line}}`;
        svg.append(marker);
      }});

      edges.forEach((edge) => {{
        const source = nodeById.get(edge.source);
        const target = nodeById.get(edge.target);
        if (!source || !target) return;
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", source.x);
        line.setAttribute("y1", source.y);
        line.setAttribute("x2", target.x);
        line.setAttribute("y2", target.y);
        line.setAttribute("class", `edge edge--${{edge.kind}}`);
        line.setAttribute("stroke", colorForEdge(edge.kind));
        svg.append(line);

        const hit = document.createElementNS("http://www.w3.org/2000/svg", "line");
        hit.setAttribute("x1", source.x);
        hit.setAttribute("y1", source.y);
        hit.setAttribute("x2", target.x);
        hit.setAttribute("y2", target.y);
        hit.setAttribute("class", "edge-hit");
        hit.addEventListener("click", () => showEdge(edge));
        svg.append(hit);
      }});

      nodes.forEach((node) => {{
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("class", "node");
        g.setAttribute("transform", `translate(${{node.x}}, ${{node.y}})`);
        g.addEventListener("click", () => showNode(node));
        const hitBox = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        hitBox.setAttribute("class", "node-hit");
        hitBox.setAttribute("x", -82);
        hitBox.setAttribute("y", -18);
        hitBox.setAttribute("width", 164);
        hitBox.setAttribute("height", 54);
        hitBox.setAttribute("rx", 8);
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("r", node.kind === "function" ? 10 : node.kind === "call_edge" ? 8 : 7);
        circle.setAttribute("fill", colorForNode(node));
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("y", 24);
        text.textContent = shortLabel(node.label || node.id);
        g.append(hitBox, circle, text);
        svg.append(g);
      }});
    }}

    function shortLabel(value) {{
      return value.length > 24 ? value.slice(0, 21) + "..." : value;
    }}

    function showNode(node) {{
      selection.innerHTML = `
        <div class="kv">
          <div><strong>Node</strong><span>${{escapeHtml(node.label || node.id)}}</span></div>
          <div><strong>ID</strong><span>${{escapeHtml(node.id)}}</span></div>
          <div><strong>Kind</strong><span>${{escapeHtml(node.kind || "unknown")}}</span></div>
          <div><strong>Origin</strong><span>${{escapeHtml(node.originTool || "unknown")}}</span></div>
          <div><strong>Line</strong><span>${{escapeHtml(lineText(node))}}</span></div>
          <div><strong>Trace</strong><span>${{escapeHtml(traceText(node.trace))}}</span></div>
        </div>
        <pre>${{escapeHtml(JSON.stringify(node.raw, null, 2))}}</pre>
      `;
    }}

    function showEdge(edge) {{
      selection.innerHTML = `
        <div class="kv">
          <div><strong>Edge</strong><span>${{escapeHtml(edge.kind)}}</span></div>
          <div><strong>Source</strong><span>${{escapeHtml(edge.source)}}</span></div>
          <div><strong>Target</strong><span>${{escapeHtml(edge.target)}}</span></div>
          <div><strong>Origin</strong><span>${{escapeHtml(edge.originTool || "unknown")}}</span></div>
        </div>
        <pre>${{escapeHtml(JSON.stringify(edge.raw, null, 2))}}</pre>
      `;
    }}

    function traceText(trace) {{
      if (!trace) return "none";
      const path = trace.path || "";
      const line = trace.line || "";
      const endLine = trace.end_line || trace.endLine || line;
      return `${{path}}:${{line}}-${{endLine}}`;
    }}

    function lineText(node) {{
      if (!Number.isInteger(node.line)) return "unknown";
      if (Number.isInteger(node.endLine) && node.endLine !== node.line) {{
        return `${{node.line}}-${{node.endLine}}`;
      }}
      return String(node.line);
    }}

    function escapeHtml(value) {{
      return String(value).replace(/[&<>"']/g, (char) => ({{
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\\"": "&quot;",
        "'": "&#39;"
      }}[char]));
    }}

    makeFilters("originFilters", GRAPH.origins, state.origins, colorForOrigin);
    makeFilters("edgeFilters", GRAPH.edgeKinds, state.edgeKinds, colorForEdge);
    makeFilters("edgeOriginFilters", GRAPH.edgeOrigins, state.edgeOrigins, colorForOrigin);
    window.addEventListener("resize", render);
    render();
  </script>
</body>
</html>
"""


def render_cpg_file(
    path: str | Path,
    output_path: str | Path,
    title: str | None = None,
    max_nodes: int = _DEFAULT_MAX_NODES,
    encoding: str = "utf-8",
) -> dict[str, Any]:
    """Read a CPG JSON file and write a self-contained HTML debug graph."""
    source_path = Path(path)
    cpg = json.loads(source_path.read_text(encoding=encoding))
    html_text = render_cpg_html(cpg, title=title, max_nodes=max_nodes)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html_text, encoding=encoding)
    graph = _graph_model(cpg, max_nodes=max_nodes)
    return {
        "path": str(destination),
        "nodes": len(graph["nodes"]),
        "edges": len(graph["edges"]),
        "truncated": graph["truncated"],
        "originalNodeCount": graph["originalNodeCount"],
    }


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a semantic_graph_visualizer operation."""
    try:
        operation, params = _parse_request(input_data)
        if operation == "render_cpg_html":
            result = render_cpg_html(
                cpg=params["cpg"],
                title=params.get("title"),
                max_nodes=_int(params.get("max_nodes"), _DEFAULT_MAX_NODES),
            )
            message = "Rendered Semantic CPG HTML"
        elif operation == "render_cpg_file":
            result = render_cpg_file(
                path=params["path"],
                output_path=params["output_path"],
                title=params.get("title"),
                max_nodes=_int(params.get("max_nodes"), _DEFAULT_MAX_NODES),
                encoding=params.get("encoding", "utf-8"),
            )
            message = "Rendered Semantic CPG HTML file"
        else:
            raise ValueError(f"unknown operation: {operation}")
        return {
            "success": True,
            "message": message,
            "result": result,
            "meta": {"operation": operation},
        }
    except Exception as exc:
        return _error_envelope(exc)


def main() -> None:
    """Read stdin JSON, execute the tool, and print stdout JSON."""
    raw = sys.stdin.read().strip()
    if not raw:
        response = _error_envelope(ValueError("No input received"))
        print(json.dumps(response, ensure_ascii=False, indent=2))
        sys.exit(2)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        response = _error_envelope(ValueError(f"Invalid JSON: {exc.msg}"))
        print(json.dumps(response, ensure_ascii=False, indent=2))
        sys.exit(2)
    response = run(payload)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    sys.exit(_exit_code(response))


def _graph_model(cpg: Mapping[str, Any], max_nodes: int) -> dict[str, Any]:
    _validate_cpg(cpg)
    if max_nodes < 1:
        raise ValueError("max_nodes must be greater than 0")
    source_nodes = sorted(
        (node for node in _list(cpg.get("nodes")) if isinstance(node, Mapping)),
        key=_node_sort_key,
    )
    selected_nodes = source_nodes[:max_nodes]
    selected_ids = {_string(node.get("id"), "") for node in selected_nodes}
    nodes = [_adapt_node(node) for node in selected_nodes]
    base_edges = [
        _adapt_edge(edge)
        for edge in _list(cpg.get("edges"))
        if isinstance(edge, Mapping)
        and _string(edge.get("source"), "") in selected_ids
        and _string(edge.get("target"), "") in selected_ids
    ]
    nodes, edges = _add_call_graph_visual_nodes(nodes, base_edges)
    origins = sorted({_string(node.get("originTool"), "unknown") for node in nodes}) or ["unknown"]
    edge_kinds = sorted({_string(edge.get("kind"), "related") for edge in edges}) or ["related"]
    edge_origins = sorted({_string(edge.get("originTool"), "unknown") for edge in edges}) or ["unknown"]
    return {
        "type": "semantic_graph_visualizer_model",
        "nodes": nodes,
        "edges": edges,
        "origins": origins,
        "edgeKinds": edge_kinds,
        "edgeOrigins": edge_origins,
        "truncated": len(source_nodes) > len(selected_nodes),
        "originalNodeCount": len(source_nodes),
    }


def _adapt_node(node: Mapping[str, Any]) -> dict[str, Any]:
    origin = node.get("origin") if isinstance(node.get("origin"), Mapping) else {}
    trace = node.get("trace") if isinstance(node.get("trace"), Mapping) else {}
    return {
        "id": _string(node.get("id"), "unknown"),
        "kind": _string(node.get("kind"), "unknown"),
        "label": _string(node.get("label"), _string(node.get("id"), "unknown")),
        "originTool": _string(origin.get("tool"), "unknown"),
        "line": _optional_int(trace.get("line")),
        "endLine": _optional_int(trace.get("end_line")),
        "trace": trace,
        "raw": dict(node),
    }


def _adapt_edge(edge: Mapping[str, Any]) -> dict[str, Any]:
    origin = edge.get("origin") if isinstance(edge.get("origin"), Mapping) else {}
    return {
        "source": _string(edge.get("source"), ""),
        "target": _string(edge.get("target"), ""),
        "kind": _string(edge.get("kind"), "related"),
        "originTool": _string(origin.get("tool"), "unknown"),
        "raw": dict(edge),
    }


def _add_call_graph_visual_nodes(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    node_by_id = {node["id"]: node for node in nodes}
    next_nodes = list(nodes)
    next_edges: list[dict[str, Any]] = []
    call_index = 0

    for edge in edges:
        if not _is_call_graph_edge(edge):
            next_edges.append(edge)
            continue

        source = node_by_id.get(edge["source"])
        target = node_by_id.get(edge["target"])
        if source is None or target is None:
            next_edges.append(edge)
            continue

        call_index += 1
        call_node = _call_graph_visual_node(edge, source, target, call_index)
        next_nodes.append(call_node)
        node_by_id[call_node["id"]] = call_node
        next_edges.append(_visual_call_edge(edge, edge["source"], call_node["id"], "call_source"))
        next_edges.append(_visual_call_edge(edge, call_node["id"], edge["target"], "call_target"))

    return next_nodes, next_edges


def _is_call_graph_edge(edge: Mapping[str, Any]) -> bool:
    return edge.get("kind") == "calls" or edge.get("originTool") == "call_graph"


def _call_graph_visual_node(
    edge: Mapping[str, Any],
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    index: int,
) -> dict[str, Any]:
    raw = edge.get("raw") if isinstance(edge.get("raw"), Mapping) else {}
    origin = raw.get("origin") if isinstance(raw.get("origin"), Mapping) else {}
    call_name = _string(origin.get("call"), "call")
    source_label = _string(source.get("label"), _string(source.get("id"), "source"))
    target_label = _string(target.get("label"), _string(target.get("id"), "target"))
    source_line = source.get("line") if isinstance(source.get("line"), int) else None
    target_line = target.get("line") if isinstance(target.get("line"), int) else None
    line = source_line if source_line is not None else target_line
    end_line = target_line if target_line is not None else line
    trace = {}
    if line is not None:
        trace = {"line": line, "end_line": end_line or line}
    return {
        "id": f"visual:call_graph:{index}:{edge['source']}->{edge['target']}",
        "kind": "call_edge",
        "label": f"{call_name}: {source_label} -> {target_label}",
        "originTool": "call_graph",
        "line": line,
        "endLine": end_line,
        "trace": trace,
        "raw": {
            "visualization": "call_graph_edge",
            "source": edge["source"],
            "target": edge["target"],
            "edge": raw,
        },
    }


def _visual_call_edge(
    source_edge: Mapping[str, Any],
    source: str,
    target: str,
    role: str,
) -> dict[str, Any]:
    raw = source_edge.get("raw") if isinstance(source_edge.get("raw"), Mapping) else {}
    return {
        "source": source,
        "target": target,
        "kind": "calls",
        "originTool": "call_graph",
        "raw": {
            "visualization": role,
            "edge": raw,
        },
    }


def _validate_cpg(cpg: Mapping[str, Any]) -> None:
    if not isinstance(cpg, Mapping):
        raise TypeError("cpg must be a dictionary")
    if cpg.get("type") != "semantic_code_property_graph":
        raise ValueError("cpg must be a semantic_code_property_graph result")
    if not isinstance(cpg.get("nodes"), list):
        raise ValueError("cpg nodes must be a list")
    if not isinstance(cpg.get("edges"), list):
        raise ValueError("cpg edges must be a list")


def _node_sort_key(node: Mapping[str, Any]) -> tuple[int, int, str, str, str]:
    trace = node.get("trace") if isinstance(node.get("trace"), Mapping) else {}
    origin = node.get("origin") if isinstance(node.get("origin"), Mapping) else {}
    line = _optional_int(trace.get("line"))
    end_line = _optional_int(trace.get("end_line"))
    return (
        line if line is not None else 999999,
        end_line if end_line is not None else 999999,
        _string(origin.get("tool"), "unknown"),
        _string(node.get("kind"), "unknown"),
        _string(node.get("id"), ""),
    )


def _parse_request(input_data: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dictionary")
    operation = input_data.get("operation")
    if not isinstance(operation, str) or not operation:
        raise ValueError("operation must be a non-empty string")
    if operation not in _OPERATIONS:
        raise ValueError(f"unknown operation: {operation}")
    params = input_data.get("params")
    if params is None:
        params = {
            key: value
            for key, value in input_data.items()
            if key not in {"operation", "params", "meta"}
        }
    if not isinstance(params, dict):
        raise TypeError("params must be a dictionary")
    if operation == "render_cpg_html" and "cpg" not in params:
        raise ValueError("render_cpg_html requires cpg")
    if operation == "render_cpg_file":
        if "path" not in params:
            raise ValueError("render_cpg_file requires path")
        if "output_path" not in params:
            raise ValueError("render_cpg_file requires output_path")
    return operation, params


def _default_title(cpg: Mapping[str, Any]) -> str:
    path = cpg.get("path")
    if isinstance(path, str) and path:
        return f"Semantic CPG - {Path(path).name}"
    return "Semantic CPG"


def _script_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def _error_envelope(exc: Exception) -> dict[str, Any]:
    message = str(exc)
    return {
        "success": False,
        "message": message,
        "error": {
            "type": exc.__class__.__name__,
            "message": message,
        },
    }


def _exit_code(response: dict[str, Any]) -> int:
    if response.get("success") is True:
        return 0
    error = response.get("error") or {}
    if error.get("type") in {
        "TypeError",
        "ValueError",
        "FileNotFoundError",
        "NotADirectoryError",
        "JSONDecodeError",
    }:
        return 2
    return 3


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string(value: Any, default: str) -> str:
    return value if isinstance(value, str) and value else default


def _int(value: Any, default: int) -> int:
    return value if isinstance(value, int) else default


def _optional_int(value: Any) -> int | None:
    return value if isinstance(value, int) else None


if __name__ == "__main__":
    main()
