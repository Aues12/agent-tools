"""Check and update the tool registry from local SKILL.yaml files."""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from metadata import discover_specs, load_spec, registry_entry

DEFAULT_ROOT = Path(__file__).resolve().parents[2]


def plan(root: str | Path = DEFAULT_ROOT) -> dict:
    base = Path(root).expanduser().resolve()
    registry_path = base / "registry" / "tool_registry.json"
    current_bytes = registry_path.read_bytes()
    current = json.loads(current_bytes)
    if not isinstance(current, dict) or not isinstance(current.get("tools"), list):
        raise ValueError("tool_registry.json must contain a tools list")
    old = {}
    for item in current["tools"]:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise ValueError("Invalid registry tool entry")
        if item["name"] in old:
            raise ValueError(f"Duplicate registry name: {item['name']}")
        old[item["name"]] = item

    projected = {}
    for path in discover_specs(base):
        spec = load_spec(path)
        if spec.get("type") != "tool":
            continue
        entry = registry_entry(base, path, spec)
        name = entry["name"]
        if name in projected:
            raise ValueError(f"Duplicate local tool name: {name}")
        projected[name] = entry
    changes = []
    next_tools = []
    for item in current["tools"]:
        name = item["name"]
        if name not in projected:
            next_tools.append(item)
            continue
        selected = dict(projected[name])
        # Older entries may intentionally advertise a different declared
        # interface as their primary transport (for example a terminal session).
        if item.get("transport") in {iface.get("transport") for iface in selected["interfaces"]}:
            selected["transport"] = item["transport"]
        if item.get("entrypoint") in {iface.get("entrypoint", "").split()[0]
                                      for iface in selected["interfaces"]}:
            selected["entrypoint"] = item["entrypoint"]
        updated = {**item, **selected}
        next_tools.append(updated)
        if updated != item:
            changes.append({"kind": "update", "name": name,
                            "fields": [key for key in selected if updated[key] != item.get(key)]})
    for name in sorted(projected.keys() - old.keys()):
        next_tools.append(projected[name])
        changes.append({"kind": "add", "name": name})
    unrepresented = sorted(old.keys() - projected.keys())
    proposed = {**current, "tools": next_tools}
    subject = {"current": current, "proposed": proposed}
    digest = sha256(json.dumps(subject, sort_keys=True, ensure_ascii=False,
                               separators=(",", ":")).encode("utf-8")).hexdigest()
    return {"root": str(base), "registry": str(registry_path), "changes": changes,
            "unrepresented": unrepresented, "plan_sha256": digest,
            "current_count": len(old), "discovered_count": len(projected),
            "proposed_count": len(next_tools), "_proposed": proposed,
            "_current_sha256": sha256(current_bytes).hexdigest()}


def sync(operation: str, *, root: str | Path = DEFAULT_ROOT,
         expected_plan_sha256: str | None = None) -> dict:
    if operation not in {"check", "plan", "apply"}:
        raise ValueError("operation must be check, plan, or apply")
    report = plan(root)
    proposed = report.pop("_proposed")
    current_sha256 = report.pop("_current_sha256")
    if operation == "apply":
        if not expected_plan_sha256 or expected_plan_sha256 != report["plan_sha256"]:
            raise ValueError("expected_plan_sha256 must match a fresh plan")
        if report["changes"]:
            destination = Path(report["registry"])
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix=".tool-registry-",
                                                 suffix=".json", dir=destination.parent,
                                                 delete=False) as handle:
                    temporary = Path(handle.name)
                    json.dump(proposed, handle, ensure_ascii=False, indent=2)
                    handle.write("\n")
                if sha256(destination.read_bytes()).hexdigest() != current_sha256:
                    raise ValueError("Registry changed during apply; rerun plan")
                os.replace(temporary, destination)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
    report["applied"] = operation == "apply"
    report["valid"] = not report["changes"] and not report["unrepresented"]
    return report


def run(payload: dict) -> dict:
    try:
        if not isinstance(payload, dict) or payload.get("operation") not in {"check", "plan", "apply"}:
            raise ValueError("Expected operation check, plan, or apply")
        params = payload.get("params", {})
        if not isinstance(params, dict):
            raise ValueError("params must be an object")
        operation = payload["operation"]
        result = sync(operation, **params)
        return {"success": True, "message": f"registry_sync {operation} completed",
                "result": result, "meta": {"operation": operation, "read_only": operation != "apply"}}
    except (TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        return {"success": False, "message": str(exc), "result": None,
                "error": {"type": type(exc).__name__, "message": str(exc)}}


if __name__ == "__main__":
    try:
        request = json.load(sys.stdin)
    except (ValueError, OSError):
        request = {}
    response = run(request)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    clean_check = not isinstance(request, dict) or request.get("operation") != "check" or (
        response["success"] and response["result"]["valid"])
    raise SystemExit(0 if response["success"] and clean_check else 1)
