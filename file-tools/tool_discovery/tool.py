"""Read-only discovery of registered tools and their local contracts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml  # pyright: ignore[reportMissingModuleSource]


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
OPERATIONS = {"list_tools", "search_tools", "inspect_tool"}
_STOP_WORDS = {
    "a", "an", "and", "are", "by", "for", "from", "in", "into", "of",
    "on", "or", "the", "their", "to", "with",
}


def _search_terms(value: str) -> set[str]:
    """Normalize words for deterministic retrieval, not semantic selection."""
    words = re.findall(r"[^\W_]+", value.casefold(), flags=re.UNICODE)
    result = set()
    for word in words:
        if word in _STOP_WORDS:
            continue
        if len(word) > 4 and word.endswith("ies"):
            word = word[:-3] + "y"
        elif len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
            word = word[:-1]
        result.add(word)
    return result


def _as_root(root: str | Path | None) -> Path:
    if root is None:
        return DEFAULT_ROOT
    if not isinstance(root, (str, Path)):
        raise TypeError("root must be a path")
    return Path(root).resolve()


def _catalog(root: str | Path | None) -> list[dict[str, Any]]:
    base = _as_root(root)
    registry = base / "registry" / "tool_registry.json"
    document = json.loads(registry.read_text(encoding="utf-8"))
    entries = document.get("tools")
    if not isinstance(entries, list):
        raise ValueError("registry tools must be a list")

    seen: set[str] = set()
    catalog: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each registry tool must be an object")
        name, relative = entry.get("name"), entry.get("path")
        if not isinstance(name, str) or not name:
            raise ValueError("each registry tool needs a non-empty name")
        if name in seen:
            raise ValueError(f"duplicate registry tool: {name}")
        seen.add(name)
        if not isinstance(relative, str) or not relative:
            raise ValueError(f"{name}: path must be a non-empty string")
        directory = (base / relative).resolve()
        if not directory.is_relative_to(base):
            raise ValueError(f"{name}: tool path escapes repository root")

        issues: list[str] = []
        local: dict[str, Any] = {}
        metadata_path = directory / "SKILL.yaml"
        if not metadata_path.is_file():
            issues.append(f"missing local metadata: {relative}/SKILL.yaml")
        else:
            parsed = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
            if not isinstance(parsed, dict):
                issues.append("local SKILL.yaml must contain a mapping")
            else:
                local = parsed

        if local:
            aliases = local.get("search_terms")
            if aliases is not None and (
                not isinstance(aliases, list)
                or not all(isinstance(alias, str) and alias.strip() for alias in aliases)
            ):
                issues.append("local search_terms must be a list of non-empty strings")
            for field in ("name", "capability", "status"):
                if entry.get(field) != local.get(field):
                    issues.append(f"registry/local {field} mismatch")
            registered_ops = entry.get("operations", [])
            local_ops = local.get("operations", [])
            local_names = [item.get("name") for item in local_ops if isinstance(item, dict)] if isinstance(local_ops, list) else []
            if set(registered_ops) != set(local_names):
                issues.append("registry/local operations mismatch")
            registered_interfaces = entry.get("interfaces", [])
            local_interfaces = local.get("interfaces", [])
            local_by_name = {part.get("name"): part for part in local_interfaces if isinstance(part, dict)} if isinstance(local_interfaces, list) else {}
            if not isinstance(registered_interfaces, list) or len(registered_interfaces) != len(local_by_name) or any(
                not isinstance(part, dict)
                or part.get("name") not in local_by_name
                or any(local_by_name[part["name"]].get(key) != value for key, value in part.items())
                for part in registered_interfaces
            ):
                issues.append("registry/local interfaces mismatch")

        catalog.append({"registry": entry, "local": local, "issues": issues})
    return catalog


def _summary(item: dict[str, Any]) -> dict[str, Any]:
    entry, local = item["registry"], item["local"]
    return {
        "name": entry["name"],
        "capability": entry.get("capability"),
        "purpose": local.get("purpose") or entry.get("description"),
        "status": entry.get("status"),
        "path": entry["path"],
        "operations": entry.get("operations", []),
        "issues": item["issues"],
    }


def list_tools(root: str | Path | None = None) -> dict[str, Any]:
    """List registered tools in registry order with local purpose and issues."""
    tools = [_summary(item) for item in _catalog(root)]
    return {"count": len(tools), "tools": tools}


def search_tools(query: str | None = None, capability: str | None = None, root: str | Path | None = None) -> dict[str, Any]:
    """Order all eligible tools by lexical coverage, keeping registry ties stable."""
    if query is not None and (not isinstance(query, str) or not query.strip()):
        raise ValueError("query must be a non-empty string when provided")
    if capability is not None and (not isinstance(capability, str) or not capability.strip()):
        raise ValueError("capability must be a non-empty string when provided")
    if query is None and capability is None:
        raise ValueError("query or capability is required")
    words = _search_terms(query) if query else set()
    if query is not None and not words and capability is None:
        raise ValueError("query has no searchable terms")
    matches = []
    for item in _catalog(root):
        summary = _summary(item)
        if capability is not None and str(summary["capability"]).casefold() != capability.casefold():
            continue
        aliases = item["local"].get("search_terms", [])
        if not isinstance(aliases, list) or not all(isinstance(term, str) for term in aliases):
            aliases = []
        corpus = " ".join(str(value) for value in (
            summary["name"], summary["capability"], summary["purpose"],
            *summary["operations"], *aliases,
        ))
        matched = words & _search_terms(corpus)
        matches.append({
            **summary,
            "matched_terms": sorted(matched),
            "match_ratio": round(len(matched) / len(words), 3) if words else None,
        })
    if words:
        matches.sort(key=lambda tool: -len(tool["matched_terms"]))
    return {"query": query, "capability": capability, "query_terms": sorted(words), "count": len(matches), "tools": matches}


def inspect_tool(name: str, root: str | Path | None = None) -> dict[str, Any]:
    """Return registered access surfaces and detailed local operation contracts."""
    if not isinstance(name, str) or not name:
        raise ValueError("name must be a non-empty string")
    for item in _catalog(root):
        entry, local = item["registry"], item["local"]
        if entry["name"] == name:
            return {
                **_summary(item),
                "entrypoint": entry.get("entrypoint"),
                "transport": entry.get("transport"),
                "interfaces": entry.get("interfaces", []),
                "operation_details": local.get("operations", []),
                "side_effects": local.get("side_effects"),
                "metadata_path": f"{entry['path']}/SKILL.yaml" if local else None,
            }
    raise ValueError(f"unknown tool: {name}")


def run(input_data: dict[str, Any], root: str | Path | None = None) -> dict[str, Any]:
    """Dispatch an operation using the repository JSON request envelope."""
    try:
        if not isinstance(input_data, dict):
            raise TypeError("input_data must be an object")
        operation = input_data.get("operation")
        if operation not in OPERATIONS:
            raise ValueError(f"unknown operation: {operation}")
        params = input_data.get("params", {})
        if not isinstance(params, dict):
            raise TypeError("params must be an object")
        allowed = {"list_tools": set(), "search_tools": {"query", "capability"}, "inspect_tool": {"name"}}[operation]
        extra = set(params) - allowed
        if extra:
            raise ValueError(f"unexpected params: {', '.join(sorted(extra))}")
        if operation == "list_tools":
            result = list_tools(root)
        elif operation == "search_tools":
            result = search_tools(params.get("query"), params.get("capability"), root)
        else:
            name = params.get("name")
            if not isinstance(name, str):
                raise ValueError("name must be a non-empty string")
            result = inspect_tool(name, root)
        return {"success": True, "message": f"Completed {operation}", "result": result, "meta": {"operation": operation}}
    except (OSError, ValueError, TypeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        return _error(exc)


def _error(exc: Exception) -> dict[str, Any]:
    return {"success": False, "message": str(exc), "error": {"type": type(exc).__name__, "message": str(exc)}}


def main() -> None:
    """Read one JSON request from stdin and emit one JSON response."""
    raw = sys.stdin.read().strip()
    try:
        if not raw:
            raise ValueError("No input received")
        response = run(json.loads(raw))
    except (ValueError, json.JSONDecodeError) as exc:
        response = _error(exc)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    sys.exit(0 if response["success"] else 1)


if __name__ == "__main__":
    main()
