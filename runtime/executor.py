"""Tool execution through registry-backed stdin/stdout JSON transport."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from registry.loader import load_registry


REPO_ROOT = Path(__file__).resolve().parents[1]


def execute_tool(step: dict[str, Any]) -> dict[str, Any]:
    """Execute one normalized tool step and return its JSON response."""
    tool_entry = _resolve_tool(step.get("tool"))
    operation = step.get("operation")
    params = step.get("params", {})

    if not isinstance(operation, str) or not operation:
        raise ValueError("step requires a non-empty operation")
    if operation not in tool_entry.get("operations", []):
        raise ValueError(f"tool {tool_entry['name']} does not expose operation: {operation}")
    if tool_entry.get("transport") != "stdin_json":
        raise ValueError(f"unsupported transport for tool {tool_entry['name']}: {tool_entry.get('transport')}")
    if not isinstance(params, dict):
        raise TypeError("step params must be a dictionary")

    payload = {
        "operation": operation,
        "params": params,
        "meta": {
            "runtime": "agent-tools",
            **(step.get("meta") if isinstance(step.get("meta"), dict) else {}),
        },
    }
    completed = subprocess.run(
        [sys.executable, str(_entrypoint_path(tool_entry))],
        input=json.dumps(payload).encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    response = _parse_response(completed.stdout)
    response.setdefault("meta", {})
    if isinstance(response["meta"], dict):
        response["meta"].update(
            {
                "tool": tool_entry["name"],
                "returncode": completed.returncode,
            }
        )
    if completed.stderr:
        response["stderr"] = completed.stderr.decode("utf-8", errors="replace")
    if completed.returncode != 0 and response.get("success") is True:
        response["success"] = False
        response["message"] = f"tool exited with code {completed.returncode}"

    return response


def _resolve_tool(name: Any) -> dict[str, Any]:
    if not isinstance(name, str) or not name:
        raise ValueError("step requires a non-empty tool name")

    registry = load_registry("tool")
    for tool in registry.get("tools", []):
        if tool.get("name") == name:
            return tool
    raise ValueError(f"unknown tool: {name}")


def _entrypoint_path(tool_entry: dict[str, Any]) -> Path:
    path = tool_entry.get("path")
    entrypoint = tool_entry.get("entrypoint")
    if not isinstance(path, str) or not isinstance(entrypoint, str):
        raise ValueError(f"tool {tool_entry.get('name')} is missing path or entrypoint")

    resolved = (REPO_ROOT / path / entrypoint).resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"tool entrypoint is outside repository: {resolved}") from exc
    if not resolved.exists():
        raise FileNotFoundError(f"tool entrypoint not found: {resolved}")
    return resolved


def _parse_response(stdout: bytes) -> dict[str, Any]:
    if not stdout:
        return {
            "success": False,
            "message": "tool produced no stdout",
            "error": {
                "type": "EmptyOutput",
                "message": "tool produced no stdout",
            },
        }

    try:
        response = json.loads(stdout.decode("utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "success": False,
            "message": f"tool produced invalid JSON: {exc.msg}",
            "error": {
                "type": "InvalidToolOutput",
                "message": f"tool produced invalid JSON: {exc.msg}",
            },
        }
    if not isinstance(response, dict):
        raise TypeError("tool response must be a dictionary")
    return response
