"""Basic semantic_cards usage example."""

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


class Worker:
    def run(self):
        return helper()
"""

    response = run(
        {
            "operation": "cards_from_source",
            "params": {
                "source": source,
                "path": "file-tools/example.py",
            },
        }
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
