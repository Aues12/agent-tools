from __future__ import annotations

from pathlib import Path
import sys
from textwrap import dedent


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import build_cfg_from_source, summarize_cfg  # noqa: E402


source = dedent(
    """
    def choose(flag):
        if flag:
            return 1
        return 0
    """
).strip() + "\n"

cfg = build_cfg_from_source(source, path="example.py")
summary = summarize_cfg(cfg)

print(summary["functions"][0]["text"])
