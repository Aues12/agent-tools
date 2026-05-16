"""Minimal rule-based planner for explicit tool execution requests."""

from __future__ import annotations

from typing import Any


def create_plan(task: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize an explicit task into ordered execution steps.

    The initial planner intentionally avoids reasoning about tool internals. It
    accepts either a single tool call or a pre-built list of tool-call steps.
    """
    if not isinstance(task, dict):
        raise TypeError("task must be a dictionary")

    if "steps" in task:
        steps = task["steps"]
        if not isinstance(steps, list):
            raise TypeError("steps must be a list")
        return [_normalize_step(step) for step in steps]

    return [_normalize_step(task)]


def _normalize_step(step: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(step, dict):
        raise TypeError("each step must be a dictionary")

    tool = step.get("tool")
    operation = step.get("operation")
    params = step.get("params", {})

    if not isinstance(tool, str) or not tool:
        raise ValueError("step requires a non-empty tool name")
    if not isinstance(operation, str) or not operation:
        raise ValueError("step requires a non-empty operation")
    if not isinstance(params, dict):
        raise TypeError("step params must be a dictionary")

    return {
        "tool": tool,
        "operation": operation,
        "params": params,
        "meta": step.get("meta", {}),
    }
