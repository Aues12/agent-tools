"""JSON and Python entrypoint for manuscript_inventory."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import cli, run_request


def run(payload: dict) -> dict:
    return run_request("manuscript_inventory", payload)


if __name__ == "__main__":
    cli("manuscript_inventory")
