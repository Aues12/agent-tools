"""Basic semantic_observatory_pipeline usage."""

from pathlib import Path
import importlib.util


TOOL_PATH = Path(__file__).resolve().parents[1] / "tool.py"
spec = importlib.util.spec_from_file_location("semantic_observatory_pipeline_tool", TOOL_PATH)
tool = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(tool)


SOURCE = """\
def calculate_total(price, quantity):
    subtotal = price * quantity
    return subtotal
"""


if __name__ == "__main__":
    analysis = tool.analyze_source(SOURCE, path="example.py")
    print(analysis["source"])
    for card in analysis["ui"]["semanticCards"]:
        print(card["title"], card["classification"])
