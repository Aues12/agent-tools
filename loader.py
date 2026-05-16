"""Small registry loader for JSON-backed capability metadata."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REGISTRY_DIR = Path(__file__).resolve().parent


def load_registry(name: str) -> dict[str, Any]:
    """Load a registry JSON file by base name.

    Example: `load_registry("tool")` loads `tool_registry.json`.
    """
    path = REGISTRY_DIR / f"{name}_registry.json"
    if not path.exists():
        raise FileNotFoundError(f"registry not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
