"""Basic copy_paste usage example."""

from __future__ import annotations

import sys
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import extract_range, find_text, insert_text  # noqa: E402


def main() -> None:
    source = Path("source.txt")
    target = Path("target.txt")

    source.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    target.write_text("header\nfooter\n", encoding="utf-8")

    print(find_text(source, "beta"))
    block = extract_range(source, 2, 2)
    insert_text(target, 2, block)
    print(target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
