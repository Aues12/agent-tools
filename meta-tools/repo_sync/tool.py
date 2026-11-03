"""Plan and apply a reviewed, one-way copy of selected repository files."""

from __future__ import annotations

import argparse
from fnmatch import fnmatch
from hashlib import sha256
import json
import difflib
import subprocess
import os
from pathlib import Path
import stat
import sys
import tempfile


PROTECTED_PARTS = frozenset({
    ".git", ".venv", "venv", "node_modules", "dist", ".pycache",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "build",
})


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _root(value: str | Path, label: str) -> Path:
    path = Path(value).expanduser()
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"{label} must be an existing, non-symlink directory")
    return path.resolve()


def _relative(value: str, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"{label} must be a non-empty relative POSIX path")
    path = Path(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
        raise ValueError(f"{label} must not be absolute or traverse directories")
    return path


def _protected(rel: Path) -> bool:
    return (any(part in PROTECTED_PARTS or part == ".DS_Store" or part.endswith(".egg-info")
                for part in rel.parts)
            or rel.name == ".env" or rel.name.startswith(".env.")
            or ("skills" in rel.parts and rel.name == "preferences.md"))


def _manifest(path: str | Path, source: Path) -> tuple[Path, list[Path], list[str], str]:
    file = Path(path).expanduser()
    if not file.is_absolute():
        file = source / file
    if file.is_symlink() or not file.is_file():
        raise ValueError("manifest_path must name an existing, non-symlink JSON file")
    raw = file.read_bytes()
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get("version") not in {"0.1.0", "0.2.0"}:
        raise ValueError("Manifest version must be 0.1.0 or 0.2.0")
    include = data.get("include")
    exclude = data.get("exclude", [])
    if not isinstance(include, list) or not include or not all(isinstance(x, str) for x in include):
        raise ValueError("Manifest include must be a non-empty list of paths")
    if not isinstance(exclude, list) or not all(isinstance(x, str) for x in exclude):
        raise ValueError("Manifest exclude must be a list of patterns")
    paths = [Path(".") if item == "." else _relative(item, "include item") for item in include]
    if len(set(paths)) != len(paths):
        raise ValueError("Manifest include paths must be unique")
    if any(_protected(item) for item in paths):
        raise ValueError("Manifest includes a protected private or generated path")
    for item in exclude:
        _relative(item, "exclude pattern")
    return file.resolve(), paths, exclude, _digest(raw), data


def _excluded(rel: Path, patterns: list[str]) -> bool:
    return _protected(rel) or any(fnmatch(rel.as_posix(), pattern) or rel.as_posix() == pattern.rstrip("/") or rel.as_posix().startswith(pattern.rstrip("/") + "/") for pattern in patterns)


def _check_ancestors(root: Path, path: Path) -> None:
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"Symlink in selected path: {current}")


def _selected(root: Path, include: list[Path], exclude: list[str], *, require: bool) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for item in include:
        _check_ancestors(root, item)
        selected = root / item
        if not selected.exists():
            if require:
                raise ValueError(f"Included source path is missing: {item}")
            continue
        if selected.is_file():
            if not _excluded(item, exclude):
                result[item.as_posix()] = selected
            continue
        if not selected.is_dir():
            raise ValueError(f"Included path is neither a regular file nor directory: {item}")
        for directory, dirs, files in os.walk(selected, followlinks=False):
            base = Path(directory)
            for name in list(dirs):
                rel = (base / name).relative_to(root)
                if (base / name).is_symlink():
                    raise ValueError(f"Symlink in selected tree: {rel}")
                if _excluded(rel, exclude):
                    dirs.remove(name)
            for name in files:
                file = base / name
                rel = file.relative_to(root)
                if file.is_symlink():
                    raise ValueError(f"Symlink in selected tree: {rel}")
                if not _excluded(rel, exclude):
                    result[rel.as_posix()] = file
    return result


def plan(source_root: str | Path, target_root: str | Path, manifest_path: str | Path, *, include_diff: bool = False) -> dict:
    """Return all proposed copies and a digest tied to current source and target bytes."""
    source = _root(source_root, "source_root")
    target = _root(target_root, "target_root")
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("Source and target directories must not overlap")
    manifest, include, exclude, manifest_sha, _ = _manifest(manifest_path, source)
    sources = _selected(source, include, exclude, require=True)
    targets = _selected(target, include, exclude, require=False)
    changes = []
    for rel, file in sorted(sources.items()):
        source_sha = _digest(file.read_bytes())
        target_file = targets.get(rel)
        target_sha = _digest(target_file.read_bytes()) if target_file else None
        if source_sha != target_sha:
            changes.append({"path": rel, "kind": "update" if target_file else "add",
                            "source_sha256": source_sha, "target_sha256": target_sha})
    target_only = sorted(targets.keys() - sources.keys())
    subject = {"source_root": str(source), "target_root": str(target),
               "manifest_sha256": manifest_sha, "changes": changes,
               "target_only": target_only}
    digest = _digest(json.dumps(subject, sort_keys=True, separators=(",", ":")).encode())
    if include_diff:
        for change in changes:
            try:
                before = targets[change["path"]].read_text(encoding="utf-8").splitlines(keepends=True) if change["path"] in targets else []
                after = sources[change["path"]].read_text(encoding="utf-8").splitlines(keepends=True)
                change["diff"] = "".join(difflib.unified_diff(before, after, fromfile="target/" + change["path"], tofile="source/" + change["path"]))
            except UnicodeError:
                change["diff"] = None
    return {"source_root": str(source), "target_root": str(target),
            "manifest_path": str(manifest), "changes": changes,
            "target_only": target_only, "plan_sha256": digest,
            "source_count": len(sources), "target_count": len(targets),
            "valid": not changes and not target_only,
            "excluded_patterns": exclude, "comparison": "byte equality; functional equivalence requires verification"}


def sync(operation: str, *, source_root: str | Path, target_root: str | Path,
         manifest_path: str | Path, expected_plan_sha256: str | None = None,
         include_diff: bool = False) -> dict:
    """Check, plan, or apply selected files after a fresh plan comparison."""
    if operation not in {"check", "plan", "apply"}:
        raise ValueError("operation must be check, plan, or apply")
    report = plan(source_root, target_root, manifest_path, include_diff=include_diff)
    if operation == "apply":
        if not expected_plan_sha256 or expected_plan_sha256 != report["plan_sha256"]:
            raise ValueError("expected_plan_sha256 must match a fresh plan")
        source = Path(report["source_root"])
        target = Path(report["target_root"])
        for change in report["changes"]:
            rel = Path(change["path"])
            _check_ancestors(target, rel)
            source_file = source / rel
            destination = target / rel
            data = source_file.read_bytes()
            if _digest(data) != change["source_sha256"]:
                raise ValueError(f"Source changed during apply: {rel}")
            observed = _digest(destination.read_bytes()) if destination.is_file() else None
            if observed != change["target_sha256"]:
                raise ValueError(f"Target changed during apply: {rel}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".repo-sync-",
                                                 delete=False) as handle:
                    temporary = Path(handle.name)
                    handle.write(data)
                os.chmod(temporary, stat.S_IMODE(source_file.stat().st_mode))
                os.replace(temporary, destination)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        report["applied_count"] = len(report["changes"])
        report["valid"] = not report["target_only"]
    report["applied"] = operation == "apply"
    return report


def verify(*, source_root: str | Path, target_root: str | Path,
           manifest_path: str | Path, timeout: int = 120) -> dict:
    """Explicitly run manifest-provided argv commands in both checkouts."""
    source = _root(source_root, "source_root")
    target = _root(target_root, "target_root")
    if source == target or source in target.parents or target in source.parents:
        raise ValueError("Source and target directories must not overlap")
    _, _, _, _, manifest = _manifest(manifest_path, source)
    commands = manifest.get("verify_commands", [])
    if not isinstance(commands, list) or not commands or any(
        not isinstance(command, list) or not command or
        not all(isinstance(arg, str) and arg for arg in command) for command in commands
    ):
        raise ValueError("verify_commands must be a non-empty list of argument lists")
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 3600:
        raise ValueError("timeout must be an integer between 1 and 3600 seconds")
    results = []
    for root in (source, target):
        for command in commands:
            try:
                completed = subprocess.run(command, cwd=root, capture_output=True,
                                           text=True, errors="replace", timeout=timeout,
                                           check=False)
                results.append({"root": str(root), "command": command,
                                "returncode": completed.returncode,
                                "stdout": completed.stdout, "stderr": completed.stderr})
            except (OSError, subprocess.TimeoutExpired) as exc:
                results.append({"root": str(root), "command": command,
                                "returncode": None, "error": str(exc)})
    return {"results": results, "valid": all(item["returncode"] == 0 for item in results)}


def _manifest_roots(manifest_path: str | Path, source_root: str | Path | None,
                    target_root: str | Path | None) -> tuple[str | Path, str | Path]:
    """Resolve optional checkout roots relative to the manifest directory."""
    path = Path(manifest_path).expanduser().resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Manifest must be a JSON object")
    roots = []
    for name, explicit in (("source_root", source_root), ("target_root", target_root)):
        value = explicit if explicit is not None else data.get(name)
        if not isinstance(value, (str, Path)) or not str(value):
            raise ValueError(f"{name} must be passed or defined in the manifest")
        value = Path(value).expanduser()
        roots.append(value if value.is_absolute() or explicit is not None else path.parent / value)
    return roots[0], roots[1]


def _format_report(operation: str, response: dict) -> str:
    if not response["success"]:
        return f"Error: {response['message']}"
    result = response["result"]
    if operation == "verify":
        lines = [f"Verification: {'passed' if result['valid'] else 'failed'}"]
        for entry in result["results"]:
            lines.append(f"  {entry['root']}: {' '.join(entry['command'])} -> {entry['returncode']}")
        return "\n".join(lines)
    changes = result["changes"]
    lines = [f"{operation}: {len(changes)} copy candidate(s), {len(result['target_only'])} target-only file(s)"]
    for entry in changes:
        lines.append(f"  {entry['kind']}: {entry['path']}")
        if entry.get("diff"):
            lines.append(entry["diff"].rstrip())
    lines.extend(f"  target-only: {path}" for path in result["target_only"])
    if operation == "plan":
        lines.append(f"Plan SHA-256: {result['plan_sha256']}")
    if operation == "apply":
        lines.append(f"Copied: {result['applied_count']}")
    lines.append(f"Shared files equal: {'yes' if result['valid'] else 'no'}")
    return "\n".join(lines)


def cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare or copy selected files between local checkouts")
    parser.add_argument("operation", choices=["check", "plan", "apply", "verify"])
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--source-root")
    parser.add_argument("--target-root")
    parser.add_argument("--expected-plan-sha256")
    parser.add_argument("--include-diff", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print the full machine-readable result")
    args = parser.parse_args(argv)
    try:
        source, target = _manifest_roots(args.manifest, args.source_root, args.target_root)
        params = {"source_root": source, "target_root": target, "manifest_path": args.manifest}
        if args.operation == "apply":
            params["expected_plan_sha256"] = args.expected_plan_sha256
        if args.operation in {"check", "plan", "apply"}:
            params["include_diff"] = args.include_diff
        response = run({"operation": args.operation, "params": params})
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        response = {"success": False, "message": str(exc), "result": None}
    print(json.dumps(response, ensure_ascii=False, indent=2) if args.json else
          _format_report(args.operation, response))
    return 0 if response["success"] and response["result"]["valid"] else 1


def run(payload: dict) -> dict:
    """Execute a JSON request and return the repository's standard envelope."""
    try:
        if not isinstance(payload, dict) or payload.get("operation") not in {"check", "plan", "apply", "verify"}:
            raise ValueError("Expected operation check, plan, apply, or verify")
        params = payload.get("params", {})
        if not isinstance(params, dict):
            raise ValueError("params must be an object")
        operation = payload["operation"]
        result = verify(**params) if operation == "verify" else sync(operation, **params)
        return {"success": True, "message": f"repo_sync {operation} completed",
                "result": result, "meta": {"operation": operation, "read_only": operation in {"check", "plan"}}}
    except (TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
        return {"success": False, "message": str(exc), "result": None,
                "error": {"type": type(exc).__name__, "message": str(exc)}}


if __name__ == "__main__" and len(sys.argv) > 1:
    raise SystemExit(cli())


if __name__ == "__main__":
    try:
        request = json.load(sys.stdin)
    except (ValueError, OSError):
        request = {}
    response = run(request)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    clean_check = not isinstance(request, dict) or request.get("operation") not in {"check", "verify"} or (
        response["success"] and response["result"]["valid"])
    raise SystemExit(0 if response["success"] and clean_check else 1)
