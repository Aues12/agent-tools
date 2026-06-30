"""Local API server for Semantic Observatory UI analysis requests."""

from __future__ import annotations

import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


HOST = "127.0.0.1"
PORT = 8765
MAX_SOURCE_BYTES = 1_000_000

_UI_DIR = Path(__file__).resolve().parent
_PIPELINE_PATH = _UI_DIR.parent / "semantic_observatory_pipeline" / "tool.py"


def _load_pipeline() -> Any:
    """Load the local semantic observatory pipeline module."""
    spec = importlib.util.spec_from_file_location(
        "semantic_observatory_pipeline_tool",
        _PIPELINE_PATH,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load pipeline from {_PIPELINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_pipeline = _load_pipeline()


class ObservatoryRequestHandler(BaseHTTPRequestHandler):
    """Handle local Semantic Observatory API requests."""

    server_version = "SemanticObservatoryAPI/0.1"

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self._send_json({"success": True}, status=204)

    def do_GET(self) -> None:
        """Return health status for the local API."""
        if self.path == "/api/health":
            self._send_json({"success": True, "message": "ok"})
            return
        self._send_json(_error("Not found", "NotFound"), status=404)

    def do_POST(self) -> None:
        """Analyze uploaded Python source through the semantic pipeline."""
        if self.path != "/api/analyze":
            self._send_json(_error("Not found", "NotFound"), status=404)
            return

        content_length = int(self.headers.get("Content-Length", "0") or "0")
        if content_length <= 0:
            self._send_json(_error("Request body is required", "ValueError"), status=400)
            return
        if content_length > MAX_SOURCE_BYTES:
            self._send_json(_error("Source file is too large", "ValueError"), status=413)
            return

        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            filename = _string(payload.get("filename"), "uploaded.py")
            source = payload.get("source")
            include_statements = bool(payload.get("includeStatements", False))
            include_blocks = bool(payload.get("includeBlocks", False))

            if not filename.endswith(".py"):
                raise ValueError("Only .py files are supported")
            if not isinstance(source, str) or not source.strip():
                raise ValueError("source must be a non-empty string")

            response = _pipeline.run(
                {
                    "operation": "analyze_source",
                    "params": {
                        "source": source,
                        "path": filename,
                        "display_path": filename,
                        "include_statements": include_statements,
                        "include_blocks": include_blocks,
                    },
                }
            )
        except Exception as exc:
            self._send_json(_error(str(exc), exc.__class__.__name__), status=400)
            return

        self._send_json(response, status=200 if response.get("success") else 422)

    def log_message(self, format: str, *args: Any) -> None:
        """Silence default HTTP request logging."""
        return

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        """Send a JSON response with local-development CORS headers."""
        body = b"" if status == 204 else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", self._allowed_origin())
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _allowed_origin(self) -> str:
        """Allow localhost Vite origins and fall back to the default dev URL."""
        origin = self.headers.get("Origin", "")
        if origin.startswith("http://127.0.0.1:") or origin.startswith("http://localhost:"):
            return origin
        return "http://127.0.0.1:5173"


def _error(message: str, error_type: str) -> dict[str, Any]:
    """Build a structured error response."""
    return {
        "success": False,
        "message": message,
        "error": {
            "type": error_type,
            "message": message,
        },
    }


def _string(value: Any, default: str) -> str:
    """Return a non-empty string value or a default."""
    return value if isinstance(value, str) and value else default


def main() -> None:
    """Start the local Semantic Observatory API server."""
    server = ThreadingHTTPServer((HOST, PORT), ObservatoryRequestHandler)
    print(f"Semantic Observatory API listening on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
