"""Inspect a registered tool through the Python API."""

from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tool import inspect_tool, search_tools  # noqa: E402


print(search_tools("call graph"))
print(inspect_tool("call_graph"))
