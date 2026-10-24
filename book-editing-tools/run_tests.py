"""Run each sub-tool's self-contained unittest suite."""
from pathlib import Path
import subprocess
import sys

base = Path(__file__).resolve().parent
folders = ["manuscript_inventory", "index_audit", "chronology_audit", "overlap_audit", "edition_diff", "ebook_preflight", "chapter_plan", "docx_assemble"]
for folder in folders:
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(base / folder / "tests"), "-v"], check=False)
    if result.returncode:
        raise SystemExit(result.returncode)
