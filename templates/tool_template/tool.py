"""Template for a narrow, deterministic tool."""

from __future__ import annotations

import json
import sys
from typing import Any


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool operation from a structured request payload.

    Replace the placeholder operation with the tool's real public interface.
    """
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dictionary")

    operation = input_data.get("operation")
    params = input_data.get("params", {})
    if operation != "example_operation":
        raise ValueError(f"unknown operation: {operation}")
    if not isinstance(params, dict):
        raise TypeError("params must be a dictionary")

    return {
        "success": True,
        "message": "Executed example_operation",
        "result": params,
        "meta": {"operation": operation},
    }


def main() -> None:
    """Read stdin JSON, execute the tool, and print stdout JSON."""
    try:
        payload = json.loads(sys.stdin.read())
        response = run(payload)
    except Exception as exc:
        response = {
            "success": False,
            "message": str(exc),
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
            },
        }

    print(json.dumps(response, ensure_ascii=False, indent=2))
    sys.exit(0 if response.get("success") is True else 1)


if __name__ == "__main__":
    main()
