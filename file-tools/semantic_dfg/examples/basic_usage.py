from pathlib import Path
import importlib.util
import sys


TOOL_PATH = Path(__file__).resolve().parents[1] / "tool.py"
sys.path.insert(0, str(TOOL_PATH.parent))
spec = importlib.util.spec_from_file_location("semantic_dfg_tool", TOOL_PATH)
tool = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(tool)


source = """
def parse_file(path):
    text = read_file(path)
    tree = ast.parse(text)
    return tree
"""

dfg = tool.build_dfg_from_source(source, path="parse_file.py")
summary = tool.summarize_dfg(dfg)

print(summary["functions"][0]["text"])
