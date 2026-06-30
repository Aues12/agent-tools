"""Run the local API and Vite dev server together."""

from __future__ import annotations

import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
API_HEALTH_URL = "http://127.0.0.1:8765/api/health"


def _api_is_running() -> bool:
    """Return whether the local analysis API is already reachable."""
    try:
        with urlopen(API_HEALTH_URL, timeout=0.5) as response:
            return response.status == 200
    except (OSError, URLError):
        return False


def _start_process(command: list[str], label: str) -> subprocess.Popen[str]:
    """Start a child process and label the launch in stdout."""
    print(f"[dev] starting {label}: {' '.join(command)}", flush=True)
    return subprocess.Popen(command, cwd=ROOT, text=True)


def _terminate(processes: list[subprocess.Popen[str]]) -> None:
    """Terminate child processes that are still running."""
    for process in processes:
        if process.poll() is None:
            process.terminate()
    deadline = time.time() + 5
    for process in processes:
        remaining = max(0.1, deadline - time.time())
        try:
            process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            process.kill()


def main() -> int:
    """Start API if needed, then run Vite until interrupted."""
    processes: list[subprocess.Popen[str]] = []

    if _api_is_running():
        print("[dev] API already running at http://127.0.0.1:8765", flush=True)
    else:
        processes.append(_start_process(["python3", "server.py"], "api"))

    processes.append(_start_process(["npm", "run", "dev"], "ui"))

    def handle_signal(signum: int, _frame: object) -> None:
        print(f"\n[dev] received signal {signum}; shutting down", flush=True)
        _terminate(processes)
        raise SystemExit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        while True:
            for process in processes:
                return_code = process.poll()
                if return_code is not None:
                    _terminate(processes)
                    return return_code
            time.sleep(0.2)
    finally:
        _terminate(processes)


if __name__ == "__main__":
    sys.exit(main())
