"""Two-operation stdin JSON and Python API for guarded manuscript edits."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import search, replace


def run(payload):
    operation = payload.get("operation") if isinstance(payload, dict) else None
    try:
        if operation not in ("search", "replace") or not isinstance(
            payload.get("params"), dict
        ):
            raise ValueError(
                "Expected operation search or replace and an object params"
            )
        result = (search if operation == "search" else replace)(**payload["params"])
        return {
            "success": True,
            "message": operation + " completed",
            "result": result,
            "meta": {"operation": operation, "read_only": operation == "search"},
        }
    except (TypeError, ValueError, OSError, UnicodeError) as exc:
        return {
            "success": False,
            "message": str(exc),
            "result": None,
            "error": {"type": type(exc).__name__, "message": str(exc)},
            "meta": {"operation": operation},
        }


if __name__ == "__main__":
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        payload = {}
    result = run(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["success"] else 1)
