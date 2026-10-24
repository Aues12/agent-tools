"""Compatibility entrypoint and JSON CLI for the read-only book tools.

Implementations live in manuscript_sources, inventory_core, and audit_core.
Existing Python callers may continue to import public functions from common.
"""
from __future__ import annotations

import json

from manuscript_sources import normalize, read_docx, require_path
from inventory_core import inventory
from audit_core import (
    chronology_audit, ebook_preflight, edition_diff, index_audit, overlap_audit,
)

OPERATIONS = {"manuscript_inventory": inventory, "index_audit": index_audit,
              "chronology_audit": chronology_audit, "overlap_audit": overlap_audit,
              "edition_diff": edition_diff, "ebook_preflight": ebook_preflight}


def run_request(operation: str, payload: dict) -> dict:
    try:
        if not isinstance(payload, dict) or payload.get("operation") != operation or not isinstance(payload.get("params"), dict):
            raise ValueError(f"Expected {{'operation': '{operation}', 'params': {{...}}}}")
        result = OPERATIONS[operation](**payload["params"])
        return {"success": True, "message": f"{operation} completed", "result": result,
                "meta": {"operation": operation, "read_only": True}}
    except (TypeError, ValueError, OSError) as exc:
        return {"success": False, "message": str(exc), "result": None,
                "error": {"type": type(exc).__name__, "message": str(exc)},
                "meta": {"operation": operation, "read_only": True}}


def cli(operation: str) -> None:
    import sys
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError) as exc:
        payload = {}
    response = run_request(operation, payload)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    raise SystemExit(0 if response["success"] else 1)
