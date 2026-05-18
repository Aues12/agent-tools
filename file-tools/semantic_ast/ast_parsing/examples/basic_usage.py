"""Basic semantic_ast usage example."""

from __future__ import annotations

import json
import sys
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from ast_parser import parse_source  # noqa: E402


def main() -> None:
    source = """
import ast

VALUE = 1 + 2

def run(input_data):
    return VALUE
"""

    result = parse_source(source, path="example.py")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
