"""JSON and Python entrypoint for safe DOCX assembly."""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from docx_assemble_core import assemble


def run(payload: dict) -> dict:
    try:
        if not isinstance(payload, dict) or payload.get("operation") != "docx_assemble" or not isinstance(payload.get("params"), dict):
            raise ValueError("Expected {'operation': 'docx_assemble', 'params': {...}}")
        result = assemble(**payload["params"])
        return {"success": True, "message": "docx_assemble completed", "result": result,
                "meta": {"operation": "docx_assemble", "read_only": result["dry_run"]}}
    except (TypeError, ValueError, OSError) as exc:
        return {"success": False, "message": str(exc), "result": None,
                "error": {"type": type(exc).__name__, "message": str(exc)},
                "meta": {"operation": "docx_assemble"}}


if __name__ == "__main__":
    try:
        request = json.load(sys.stdin)
    except (ValueError, OSError):
        request = {}
    response = run(request)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    raise SystemExit(0 if response["success"] else 1)
