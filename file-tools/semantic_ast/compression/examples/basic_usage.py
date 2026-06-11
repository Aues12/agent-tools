"""Basic compression sub-tool usage example."""

from __future__ import annotations

import json
import sys
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from compression import compress_ast


def main() -> None:
    tree = {
        "type": "function",
        "name": "main",
        "args": {
            "positional_or_keyword": [
                {"type": "argument", "name": "value"},
            ],
        },
        "body": [
            {
                "type": "return",
                "value": {"type": "name", "id": "value"},
            }
        ],
        "line": 1,
        "end_line": 2,
    }

    print(json.dumps(compress_ast(tree), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
