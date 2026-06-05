"""Basic semantic_ast dispatcher usage example."""

from __future__ import annotations

import json
import sys
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import run


def main() -> None:
    source = """
def helper():
    return 1

def main():
    return helper()
"""

    response = run(
        {
            "operation": "parse_and_build_call_graph",
            "params": {"source": source, 
                       "path": "example.py"},
        }
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
