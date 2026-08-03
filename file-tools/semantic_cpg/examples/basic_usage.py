from __future__ import annotations

from pathlib import Path
import sys
from textwrap import dedent


TOOL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_DIR))

from tool import build_cpg_from_source, summarize_cpg  # noqa: E402


source = dedent(
    """
    def helper(value):
        return value

    def choose(flag, a, b):
        if flag:
            value = helper(a)
        else:
            value = b
        return value
    """
).strip() + "\n"

cpg = build_cpg_from_source(source, path="example.py")
summary = summarize_cpg(cpg)

print(summary["text"])
