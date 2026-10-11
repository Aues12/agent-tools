import { useCallback, useEffect, useMemo, useRef, useState, type KeyboardEvent, type PointerEvent, type WheelEvent } from "react";
import type { SemanticGraph } from "../data/graph.ts";
import { colorForKind } from "../data/graph.ts";
import { layoutGraph, NODE_HEIGHT, NODE_WIDTH } from "../data/layout.ts";
import { nextNodeId, type ArrowDirection } from "../data/navigation.ts";

interface Viewport { x: number; y: number; width: number; height: number }
interface Props {
  graph: SemanticGraph;
  selectedId: number | null;
  matchedIds: Set<number>;
  onSelect: (id: number | null) => void;
  focus: { id: number; serial: number } | null;
}

function lines(label: string): string[] {
  const result: string[] = [];
  let line = "";
  for (const word of label.split(/\s+/)) {
    if (`${line} ${word}`.trim().length > 32 && line) { result.push(line); line = word; }
    else line = `${line} ${word}`.trim();
  }
  if (line) result.push(line);
  return result.slice(0, 2).map((part, index) => index === 1 && result.length > 2 ? `${part.slice(0, 29)}…` : part);
}

export function GraphCanvas({ graph, selectedId, matchedIds, onSelect, focus }: Props) {
  const layout = useMemo(() => layoutGraph(graph), [graph]);
  const container = useRef<HTMLDivElement>(null);
  const drag = useRef<{ x: number; y: number; view: Viewport } | null>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  const previousSize = useRef<{ width: number; height: number } | null>(null);
  const previousLayout = useRef<typeof layout | null>(null);
  const [view, setView] = useState<Viewport>({ x: 0, y: 0, width: layout.width, height: layout.height });
  const positions = layout.positions;
  const activeEdges = useMemo(() => new Set(graph.edges.filter((edge) => edge.source === selectedId || edge.target === selectedId).map((edge) => edge.unique_id)), [graph, selectedId]);
  const neighbors = useMemo(() => new Set(graph.edges.flatMap((edge) => edge.source === selectedId ? [edge.target] : edge.target === selectedId ? [edge.source] : [])), [graph, selectedId]);

  const fit = useCallback(() => {
    if (size.width <= 0 || size.height <= 0) return;
    const aspect = size.width / Math.max(1, size.height);
    const width = Math.max(layout.width, layout.height * aspect);
    const height = width / aspect;
    setView({ x: (layout.width - width) / 2, y: (layout.height - height) / 2, width, height });
  }, [layout, size]);

  useEffect(() => {
    const element = container.current;
    if (!element) return;
    const observer = new ResizeObserver(([entry]) => setSize({ width: entry.contentRect.width, height: entry.contentRect.height }));
    observer.observe(element);
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    if (size.width <= 0 || size.height <= 0) return;
    const oldSize = previousSize.current;
    if (previousLayout.current !== layout || !oldSize) {
      fit();
    } else if (oldSize.width !== size.width || oldSize.height !== size.height) {
      setView((current) => {
        const scale = current.width / oldSize.width;
        const width = size.width * scale;
        const height = size.height * scale;
        return {
          x: current.x + (current.width - width) / 2,
          y: current.y + (current.height - height) / 2,
          width,
          height,
        };
      });
    }
    previousSize.current = size;
    previousLayout.current = layout;
  }, [fit, layout, size]);
  useEffect(() => {
    if (focus === null) return;
    const point = positions.get(focus.id);
    if (!point) return;
    setView((previous) => {
      const width = Math.min(previous.width, 1200);
      const height = width * previous.height / previous.width;
      return { x: point.x + NODE_WIDTH / 2 - width / 2, y: point.y + NODE_HEIGHT / 2 - height / 2, width, height };
    });
  }, [focus, positions]);

  function revealNode(id: number) {
    const point = positions.get(id);
    if (!point) return;
    setView((current) => {
      const marginX = Math.max(0, Math.min(24, (current.width - NODE_WIDTH) / 2));
      const marginY = Math.max(0, Math.min(24, (current.height - NODE_HEIGHT) / 2));
      let x = current.x;
      let y = current.y;
      if (point.x < x + marginX) x = point.x - marginX;
      else if (point.x + NODE_WIDTH > x + current.width - marginX) x = point.x + NODE_WIDTH + marginX - current.width;
      if (point.y < y + marginY) y = point.y - marginY;
      else if (point.y + NODE_HEIGHT > y + current.height - marginY) y = point.y + NODE_HEIGHT + marginY - current.height;
      return x === current.x && y === current.y ? current : { ...current, x, y };
    });
  }

  function keyDown(event: KeyboardEvent<HTMLDivElement>) {
    const directions: ArrowDirection[] = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];
    if (!directions.includes(event.key as ArrowDirection)) return;
    event.preventDefault();
    const next = nextNodeId(positions, matchedIds, selectedId, event.key as ArrowDirection, {
      x: view.x + view.width / 2 - NODE_WIDTH / 2,
      y: view.y + view.height / 2 - NODE_HEIGHT / 2,
    });
    if (next === null) return;
    onSelect(next);
    revealNode(next);
  }

  function zoom(factor: number, clientX?: number, clientY?: number) {
    setView((previous) => {
      const bounds = container.current?.getBoundingClientRect();
      const fx = bounds && clientX !== undefined ? (clientX - bounds.left) / bounds.width : .5;
      const fy = bounds && clientY !== undefined ? (clientY - bounds.top) / bounds.height : .5;
      const width = Math.max(280, Math.min(40000, previous.width * factor));
      const height = width * (previous.height / previous.width);
      return { x: previous.x + (previous.width - width) * fx, y: previous.y + (previous.height - height) * fy, width, height };
    });
  }
  function wheel(event: WheelEvent<HTMLDivElement>) { event.preventDefault(); zoom(event.deltaY > 0 ? 1.12 : .89, event.clientX, event.clientY); }
  function down(event: PointerEvent<HTMLDivElement>) {
    if (event.button !== 0) return;
    drag.current = { x: event.clientX, y: event.clientY, view };
    event.currentTarget.focus({ preventScroll: true });
    event.currentTarget.setPointerCapture(event.pointerId);
  }
  function move(event: PointerEvent<HTMLDivElement>) {
    const start = drag.current;
    if (!start) return;
    setView({ ...start.view, x: start.view.x - (event.clientX - start.x) * start.view.width / size.width, y: start.view.y - (event.clientY - start.y) * start.view.height / size.height });
  }
  function end() { drag.current = null; }

  return <section className="canvas-section" aria-label="Directed graph canvas">
    <div className="canvas-toolbar">
      <div><strong>Graph canvas</strong><span className="toolbar-sub">{layout.cyclic ? "Cycles shown in layout" : "Layered directed layout"}</span></div>
      <div className="canvas-actions">
        <button onClick={() => zoom(1.25)} aria-label="Zoom out">−</button>
        <button onClick={() => zoom(.8)} aria-label="Zoom in">+</button>
        <button onClick={fit}>Fit view</button>
        <button onClick={() => { onSelect(null); fit(); }}>Reset</button>
      </div>
    </div>
    <div className="canvas" ref={container} tabIndex={0} role="group" aria-label="Graph navigation" aria-keyshortcuts="ArrowLeft ArrowRight ArrowUp ArrowDown" onKeyDown={keyDown} onWheel={wheel} onPointerDown={down} onPointerMove={move} onPointerUp={end} onPointerCancel={end}>
      <svg viewBox={`${view.x} ${view.y} ${view.width} ${view.height}`} role="img" aria-label={`${graph.nodes.length} nodes and ${graph.edges.length} directed relationships`}>
        <defs><marker id="edge-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0 0 L8 4 L0 8 Z" fill="context-stroke" /></marker></defs>
        <g className="edges">{graph.edges.map((edge) => {
          const source = positions.get(edge.source)!;
          const target = positions.get(edge.target)!;
          const active = activeEdges.has(edge.unique_id);
          const dim = !matchedIds.has(edge.source) || !matchedIds.has(edge.target) || (selectedId !== null && !active);
          const self = edge.source === edge.target;
          const forward = target.x > source.x;
          const x1 = forward ? source.x + NODE_WIDTH : source.x + NODE_WIDTH / 2;
          const y1 = source.y + NODE_HEIGHT / 2;
          const x2 = forward ? target.x - 7 : target.x + NODE_WIDTH / 2;
          const y2 = forward ? target.y + NODE_HEIGHT / 2 : target.y - 7;
          const bend = Math.max(52, Math.abs(x2 - x1) / 2);
          const path = self
            ? `M ${source.x + NODE_WIDTH * .75} ${source.y} C ${source.x + NODE_WIDTH * .75} ${source.y - 75}, ${source.x + NODE_WIDTH * .25} ${source.y - 75}, ${source.x + NODE_WIDTH * .25} ${source.y - 7}`
            : forward ? `M ${x1} ${y1} C ${x1 + bend} ${y1}, ${x2 - bend} ${y2}, ${x2} ${y2}`
            : `M ${x1} ${y1} C ${x1 + 65} ${y1 + 72}, ${x2 - 65} ${y2 - 72}, ${x2} ${y2}`;
          return <path key={edge.unique_id} d={path} className={`edge ${active ? "active" : ""} ${dim ? "dim" : ""}`} markerEnd="url(#edge-arrow)"><title>#{edge.unique_id} · {edge.kind}{edge.label ? `: ${edge.label}` : ""} · #{edge.source} → #{edge.target}</title></path>;
        })}</g>
        <g className="nodes">{graph.nodes.map((node) => {
          const point = positions.get(node.unique_id)!;
          const color = colorForKind(node.kind);
          const dim = !matchedIds.has(node.unique_id) || (selectedId !== null && selectedId !== node.unique_id && !neighbors.has(node.unique_id));
          return <g key={node.unique_id} transform={`translate(${point.x} ${point.y})`} className={`graph-node ${selectedId === node.unique_id ? "selected" : ""} ${dim ? "dim" : ""}`} onPointerDown={(event) => event.stopPropagation()} onClick={() => { onSelect(node.unique_id); container.current?.focus({ preventScroll: true }); }} role="button" tabIndex={0} aria-label={`Node ${node.unique_id}: ${node.label}`} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); onSelect(node.unique_id); container.current?.focus({ preventScroll: true }); } }}>
            <rect className="node-body" width={NODE_WIDTH} height={NODE_HEIGHT} rx="12" />
            <rect x="0" y="13" width="4" height="58" rx="2" fill={color} />
            <text className="node-kind" x="16" y="22" fill={color}>{node.kind.toLocaleUpperCase()}</text>
            <text className="node-id" x={NODE_WIDTH - 15} y="22" textAnchor="end">#{node.unique_id}</text>
            {lines(node.label).map((line, index) => <text className="node-label" key={index} x="16" y={47 + index * 18}>{line}</text>)}
            <title>{node.label}</title>
          </g>;
        })}</g>
      </svg>
      <div className="canvas-hint">Drag to pan · Scroll to zoom · Arrow keys to move between nodes</div>
    </div>
  </section>;
}
