from __future__ import annotations

import json
from pathlib import Path

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
