"""Generate and verify an ISBN-13 SVG in a temporary directory."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import write_svg


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / "isbn-9786253798338.svg"
        result = write_svg(
            isbn="9786253798338",
            display_text="ISBN 978-625-379-833-8",
            output_path=output,
        )
        print(result)
