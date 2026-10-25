"""JSON and Python entrypoint for chapter_plan validation."""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from chapter_plan_core import validate_plan


def run(payload: dict) -> dict:
    try:
        if not isinstance(payload, dict) or payload.get("operation") != "chapter_plan" or not isinstance(payload.get("params"), dict):
            raise ValueError("Expected {'operation': 'chapter_plan', 'params': {...}}")
        result = validate_plan(**payload["params"])
        return {"success": True, "message": "chapter_plan completed", "result": result,
                "meta": {"operation": "chapter_plan", "read_only": True}}
    except (TypeError, ValueError, OSError) as exc:
        return {"success": False, "message": str(exc), "result": None,
                "error": {"type": type(exc).__name__, "message": str(exc)},
                "meta": {"operation": "chapter_plan", "read_only": True}}


if __name__ == "__main__":
    try:
        request = json.load(sys.stdin)
    except (ValueError, OSError):
        request = {}
    response = run(request)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    raise SystemExit(0 if response["success"] else 1)
