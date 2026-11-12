"""Run the repository's read-only Python and registry checks."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def main() -> int:
    checks = [
        ("Ruff lint", [sys.executable, "-m", "ruff", "check", "."], None),
        ("Ruff format", [sys.executable, "-m", "ruff", "format", "--check", "."], None),
        ("Python tests", [sys.executable, "test_all.py"], None),
        (
            "Registry consistency",
            [sys.executable, "meta-tools/registry_sync/tool.py"],
            '{"operation":"check","params":{}}\n',
        ),
    ]
    failed = []
    for name, command, input_text in checks:
        print(f"\n=== {name} ===", flush=True)
        result = subprocess.run(
            command, cwd=ROOT, input=input_text, text=True, check=False
        )
        if result.returncode:
            failed.append(name)
    if failed:
        print(f"\nFailed: {', '.join(failed)}", flush=True)
        return 1
    print("\nAll checks passed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
