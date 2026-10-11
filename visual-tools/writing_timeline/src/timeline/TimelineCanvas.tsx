import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
  type WheelEvent as ReactWheelEvent,
} from "react";
import type { SemanticGraph } from "../types/semanticGraph";
import { buildTimelineLayout, type TimelineNode } from "./layout";

interface TimelineCanvasProps {
  graph: SemanticGraph;
  query: string;
  selectedId?: string;
  onSelect: (nodeId: string) => void;
}

interface ViewTransform {
  scale: number;
  offsetX: number;
  offsetY: number;
}

interface PointerDrag {
  pointerId: number;
  x: number;
  y: number;
  startX: number;
  startY: number;
}

function normalized(value: string): string {
  return value.trim().toLocaleLowerCase("tr");
}

export function TimelineCanvas({ graph, query, selectedId, onSelect }: TimelineCanvasProps) {
  const hostRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [size, setSize] = useState({ width: 1000, height: 700 });
  const [transform, setTransform] = useState<ViewTransform>({ scale: 1, offsetX: 0, offsetY: 0 });
  const [drag, setDrag] = useState<PointerDrag>();
  const layout = useMemo(() => buildTimelineLayout(graph), [graph]);
  const queryText = normalized(query);

  const connectedIds = useMemo(() => {
    const ids = new Set<string>();
    if (!selectedId) return ids;
    ids.add(selectedId);
    for (const edge of graph.edges) {
      if (edge.source === selectedId) ids.add(edge.target);
      if (edge.target === selectedId) ids.add(edge.source);
    }
    return ids;
  }, [graph.edges, selectedId]);

  const fitTimeline = useCallback(() => {
    const scale = Math.min(1, (size.width - 48) / layout.width);
    const verticalScale = Math.max(0.62, scale);
    setTransform({
      scale,
      offsetX: 24,
      offsetY: Math.max(24, (size.height - layout.height * verticalScale) / 2),
    });
  }, [layout.height, layout.width, size.height, size.width]);

  useEffect(() => {
    if (!hostRef.current) return;
    const observer = new ResizeObserver(([entry]) => {
      setSize({
        width: Math.max(360, entry.contentRect.width),
        height: Math.max(420, entry.contentRect.height),
      });
    });
    observer.observe(hostRef.current);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    fitTimeline();
  }, [fitTimeline]);

  useEffect(() => {
    if (!selectedId) return;
    const item = layout.byId.get(selectedId);
    if (!item) return;
    setTransform((current) => {
      const screenX = item.x * current.scale + current.offsetX;
      if (screenX >= 90 && screenX <= size.width - 90) return current;
      return { ...current, offsetX: size.width / 2 - item.x * current.scale };
    });
  }, [layout.byId, selectedId, size.width]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.floor(size.width * dpr);
    canvas.height = Math.floor(size.height * dpr);
    canvas.style.width = `${size.width}px`;
    canvas.style.height = `${size.height}px`;
    context.setTransform(dpr, 0, 0, dpr, 0, 0);
    context.clearRect(0, 0, size.width, size.height);
    context.fillStyle = "#f8f6f0";
    context.fillRect(0, 0, size.width, size.height);

    const verticalScale = Math.max(0.62, transform.scale);
    const screen = (x: number, y: number) => ({
      x: x * transform.scale + transform.offsetX,
      y: y * verticalScale + transform.offsetY,
    });
    const matches = (item: TimelineNode) =>
      queryText.length > 0 && normalized(`${item.node.label} ${item.node.id}`).includes(queryText);
    const dimmed = (item: TimelineNode) => {
      if (selectedId) return !connectedIds.has(item.node.id);
      if (queryText) return !matches(item);
      return false;
    };

    const axisStart = screen(0, layout.axisY);
    const axisEnd = screen(layout.width, layout.axisY);
    context.strokeStyle = "rgba(66, 75, 70, 0.28)";
    context.lineWidth = 1;
    context.beginPath();
    context.moveTo(axisStart.x, axisStart.y);
    context.lineTo(axisEnd.x, axisEnd.y);
    context.stroke();

    for (const tick of layout.years) {
      const point = screen(tick.x, layout.axisY);
      context.strokeStyle = "rgba(88, 99, 93, 0.16)";
      context.beginPath();
      context.moveTo(point.x, point.y - 18);
      context.lineTo(point.x, screen(0, layout.height).y);
      context.stroke();
      if (point.x > -80 && point.x < size.width + 80) {
        context.fillStyle = "#64706a";
        context.font = "700 12px Inter, sans-serif";
        context.fillText(String(tick.year), point.x + 7, point.y - 8);
      }
    }

    for (const edge of graph.edges) {
      const source = layout.byId.get(edge.source);
      const target = layout.byId.get(edge.target);
      if (!source || !target) continue;
      const from = screen(source.x, source.y);
      const to = screen(target.x, target.y);
      const highlighted = selectedId === edge.source || selectedId === edge.target;
      const edgeDimmed = dimmed(source) || dimmed(target);
      context.strokeStyle = highlighted
        ? "rgba(176, 91, 54, 0.78)"
        : edgeDimmed
          ? "rgba(79, 107, 98, 0.035)"
          : "rgba(79, 107, 98, 0.22)";
      context.lineWidth = highlighted ? 1.8 : 1;
      const distance = Math.abs(to.x - from.x);
      const axisScreenY = screen(0, layout.axisY).y;
      const archY = axisScreenY - Math.min(120, 26 + distance / 8);
      context.beginPath();
      context.moveTo(from.x, from.y);
      context.bezierCurveTo(from.x, archY, to.x, archY, to.x, to.y);
      context.stroke();

      if (highlighted) {
        const angle = Math.atan2(to.y - archY, to.x - to.x || 0.001);
        context.fillStyle = context.strokeStyle;
        context.beginPath();
        context.moveTo(to.x, to.y);
        context.lineTo(to.x - 7 * Math.cos(angle - 0.45), to.y - 7 * Math.sin(angle - 0.45));
        context.lineTo(to.x - 7 * Math.cos(angle + 0.45), to.y - 7 * Math.sin(angle + 0.45));
        context.closePath();
        context.fill();
      }
    }

    for (const item of layout.nodes) {
      const point = screen(item.x, item.y);
      if (point.x < -80 || point.x > size.width + 80) continue;
      const selected = item.node.id === selectedId;
      const matched = matches(item);
      const radius = Math.max(3.2, item.radius * Math.max(0.55, transform.scale));
      context.globalAlpha = dimmed(item) ? 0.12 : 1;
      context.fillStyle = selected ? "#b05b36" : matched ? "#c89b3c" : "#356f65";
      context.beginPath();
      context.arc(point.x, point.y, selected ? radius + 2.5 : radius, 0, Math.PI * 2);
      context.fill();
      if (selected || matched || (transform.scale > 0.55 && item.degree >= 4)) {
        context.fillStyle = "#27312e";
        context.font = `${selected ? 700 : 600} ${selected ? 12 : 10}px Inter, sans-serif`;
        const drawOnLeft = point.x > size.width * 0.68;
        context.textAlign = drawOnLeft ? "right" : "left";
        context.fillText(
          item.node.label,
          drawOnLeft ? point.x - radius - 6 : point.x + radius + 6,
          point.y + 1,
        );
        context.textAlign = "left";
      }
    }
    context.globalAlpha = 1;
  }, [connectedIds, graph.edges, layout, queryText, selectedId, size, transform]);

  function point(event: ReactPointerEvent<HTMLCanvasElement> | ReactWheelEvent<HTMLCanvasElement>) {
    const rect = event.currentTarget.getBoundingClientRect();
    return { x: event.clientX - rect.left, y: event.clientY - rect.top };
  }

  function hitNode(x: number, y: number): TimelineNode | undefined {
    const worldX = (x - transform.offsetX) / transform.scale;
    const worldY = (y - transform.offsetY) / Math.max(0.62, transform.scale);
    return [...layout.nodes].reverse().find(
      (item) => Math.hypot(item.x - worldX, item.y - worldY) <= Math.max(14, item.radius + 7),
    );
  }

  function handlePointerDown(event: ReactPointerEvent<HTMLCanvasElement>) {
    event.currentTarget.setPointerCapture(event.pointerId);
    const current = point(event);
    setDrag({ pointerId: event.pointerId, x: current.x, y: current.y, startX: current.x, startY: current.y });
  }

  function handlePointerMove(event: ReactPointerEvent<HTMLCanvasElement>) {
    if (!drag || drag.pointerId !== event.pointerId) return;
    const current = point(event);
    setTransform((view) => ({
      ...view,
      offsetX: view.offsetX + current.x - drag.x,
      offsetY: view.offsetY + current.y - drag.y,
    }));
    setDrag({ ...drag, x: current.x, y: current.y });
  }

  function handlePointerUp(event: ReactPointerEvent<HTMLCanvasElement>) {
    if (!drag || drag.pointerId !== event.pointerId) return;
    const current = point(event);
    if (Math.hypot(current.x - drag.startX, current.y - drag.startY) < 4) {
      const item = hitNode(current.x, current.y);
      if (item) onSelect(item.node.id);
    }
    setDrag(undefined);
  }

  function handleWheel(event: ReactWheelEvent<HTMLCanvasElement>) {
    event.preventDefault();
    const cursor = point(event);
    setTransform((view) => {
      const nextScale = Math.min(2.8, Math.max(0.12, view.scale * (event.deltaY < 0 ? 1.12 : 0.9)));
      const currentVerticalScale = Math.max(0.62, view.scale);
      const nextVerticalScale = Math.max(0.62, nextScale);
      const worldX = (cursor.x - view.offsetX) / view.scale;
      const worldY = (cursor.y - view.offsetY) / currentVerticalScale;
      return {
        scale: nextScale,
        offsetX: cursor.x - worldX * nextScale,
        offsetY: cursor.y - worldY * nextVerticalScale,
      };
    });
  }

  return (
    <div className="timeline-stage">
      <div className="timeline-toolbar">
        <span>{layout.minDate.getFullYear()}—{layout.maxDate.getFullYear()}</span>
        <span>{Math.round(transform.scale * 100)}%</span>
        <button type="button" onClick={fitTimeline}>Tüm zaman çizgisi</button>
      </div>
      <div ref={hostRef} className="timeline-canvas-host">
        <canvas
          ref={canvasRef}
          aria-label="Yazıların kronolojik bağlantı haritası"
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onPointerCancel={() => setDrag(undefined)}
          onWheel={handleWheel}
        />
      </div>
      <p className="timeline-hint">Sürükle: gezin · kaydır: yakınlaş · node: yazı · kavis: referans</p>
    </div>
  );
}
