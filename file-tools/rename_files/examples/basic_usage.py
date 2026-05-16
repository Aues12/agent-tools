from __future__ import annotations

import json
import sys
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import rename_files


def main() -> None:
    result = rename_files(
        directory=Path("."),
        find_text="draft",
        replace_text="final",
        dry_run=True,
        extensions=["md", ".txt"],
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
