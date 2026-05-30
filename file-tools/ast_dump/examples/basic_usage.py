"""Basic examples for ast_dump."""

from __future__ import annotations

from tool import dump_source


if __name__ == "__main__":
    result = dump_source("def add(a, b):\n    return a + b\n", path="example.py")
    print(result["ast_dump"])
