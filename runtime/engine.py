"""Lightweight runtime engine that coordinates planning and execution."""

from __future__ import annotations

from typing import Any

from .executor import execute_tool
from .planner import create_plan


def run_task(task: dict[str, Any]) -> dict[str, Any]:
    """Create and execute a plan for an explicit task request."""
    try:
        plan = create_plan(task)
        results = []
        for step in plan:
            result = execute_tool(step)
            results.append(result)
            if result.get("success") is not True:
                return _task_result(False, plan, results, "Task stopped after a failed step")
        return _task_result(True, plan, results, "Task completed")
    except Exception as exc:
        return {
            "success": False,
            "message": str(exc),
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
            },
            "plan": [],
            "results": [],
        }


def _task_result(
    success: bool,
    plan: list[dict[str, Any]],
    results: list[dict[str, Any]],
    message: str,
) -> dict[str, Any]:
    return {
        "success": success,
        "message": message,
        "plan": plan,
        "results": results,
    }
