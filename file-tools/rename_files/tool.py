"""Deterministic file-renaming primitives for directory-scoped workflows."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def make_result(**overrides: Any) -> dict[str, Any]:
    """Return a stable result shape for dry runs and applied renames."""
    base: dict[str, Any] = {
        "success": True,
        "message": "",
        "directory": "",
        "dry_run": True,
        "recursive": False,
        "scanned_count": 0,
        "matched_count": 0,
        "renamed_count": 0,
        "skipped_count": 0,
        "conflict_count": 0,
        "renamed": [],
        "skipped": [],
        "conflicts": [],
    }
    base.update(overrides)
    return base


def normalize_extensions(extensions: list[str] | None) -> list[str]:
    """Normalize extensions to lowercase dot-prefixed values."""
    if extensions is None:
        return []

    normalized: list[str] = []
    for item in extensions:
        if not isinstance(item, str):
            raise TypeError("extensions must contain only strings")
        ext = item.strip()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        normalized.append(ext.lower())
    return normalized


def rename_files(
    directory: str | Path,
    find_text: str,
    replace_text: str = "",
    *,
    recursive: bool = False,
    dry_run: bool = True,
    extensions: list[str] | None = None,
    targets: list[str] | None = None,
) -> dict[str, Any]:
    """Plan or apply file renames inside one directory boundary."""
    root = _as_directory_path(directory)
    _validate_rename_inputs(find_text, replace_text, targets)

    normalized_extensions = normalize_extensions(extensions)
    resolved_targets = _resolve_targets(root, targets or [])
    candidates, scanned_count, skipped = _build_candidates(
        directory=root,
        recursive=recursive,
        find_text=find_text,
        extensions=normalized_extensions,
        targets=resolved_targets,
    )
    renamed, conflicts = _plan_renames(candidates, find_text, replace_text)

    if not dry_run and renamed:
        _apply_renames(renamed)

    action = "Prepared" if dry_run else "Applied"
    return make_result(
        message=f"{action} {len(renamed)} rename(s)",
        directory=str(root),
        dry_run=dry_run,
        recursive=recursive,
        scanned_count=scanned_count,
        matched_count=len(candidates),
        renamed_count=len(renamed),
        skipped_count=len(skipped),
        conflict_count=len(conflicts),
        renamed=renamed,
        skipped=skipped,
        conflicts=conflicts,
    )


def run(input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute the rename_files tool from a structured request payload."""
    try:
        params = _parse_request(input_data)
        result = rename_files(**params)
        return {
            "success": True,
            "message": result["message"],
            "result": result,
            "meta": {"operation": "rename_files"},
        }
    except Exception as exc:
        return _error_envelope(exc)


def main() -> None:
    """Read a JSON payload from stdin and print a JSON result."""
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            raise ValueError("No input received")
        payload = json.loads(raw)
    except Exception as exc:
        result = _error_envelope(exc)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(_exit_code(result))

    result = run(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(_exit_code(result))


def _as_directory_path(path: str | Path) -> Path:
    if isinstance(path, Path):
        candidate = path
    elif isinstance(path, str):
        candidate = Path(path)
    else:
        raise TypeError("directory must be a string or Path")

    resolved = candidate.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Directory does not exist: {resolved}")
    if not resolved.is_dir():
        raise NotADirectoryError(f"Provided path is not a directory: {resolved}")
    return resolved


def _validate_rename_inputs(
    find_text: Any,
    replace_text: Any,
    targets: list[str] | None,
) -> None:
    if not isinstance(find_text, str) or find_text == "":
        raise ValueError("find_text must be a non-empty string")
    if not isinstance(replace_text, str):
        raise TypeError("replace_text must be a string")
    if targets is not None and not isinstance(targets, list):
        raise TypeError("targets must be a list when provided")


def _parse_request(input_data: Any) -> dict[str, Any]:
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dictionary")

    operation = input_data.get("operation", "rename_files")
    if not isinstance(operation, str) or not operation:
        raise ValueError("operation must be a non-empty string")
    if operation != "rename_files":
        raise ValueError(f"unknown operation: {operation}")

    params = input_data.get("params")
    if params is None:
        params = {
            key: value
            for key, value in input_data.items()
            if key not in {"operation", "params", "meta"}
        }
    if not isinstance(params, dict):
        raise TypeError("params must be a dictionary")

    return params


def _error_envelope(exc: Exception) -> dict[str, Any]:
    return {
        "success": False,
        "message": str(exc),
        "error": {
            "type": exc.__class__.__name__,
            "message": str(exc),
        },
    }


def _exit_code(response: dict[str, Any]) -> int:
    if response.get("success") is True:
        return 0

    error = response.get("error") or {}
    if error.get("type") in {
        "TypeError",
        "ValueError",
        "FileNotFoundError",
        "NotADirectoryError",
    }:
        return 2
    return 3


def _collect_files(directory: Path, recursive: bool) -> list[Path]:
    iterator = directory.rglob("*") if recursive else directory.iterdir()
    return sorted(path.resolve() for path in iterator if path.is_file())


def _resolve_targets(directory: Path, targets: list[str]) -> list[Path]:
    resolved: list[Path] = []
    for raw_target in targets:
        if not isinstance(raw_target, str):
            raise TypeError("targets must contain only strings")
        candidate = Path(raw_target)
        if not candidate.is_absolute():
            candidate = directory / candidate
        candidate = candidate.resolve()
        try:
            candidate.relative_to(directory)
        except ValueError as exc:
            raise ValueError(f"Target is outside the directory: {raw_target}") from exc
        if not candidate.exists():
            raise FileNotFoundError(f"Target does not exist: {raw_target}")
        if not candidate.is_file():
            raise ValueError(f"Target is not a file: {raw_target}")
        resolved.append(candidate)
    return sorted(resolved)


def _build_candidates(
    directory: Path,
    recursive: bool,
    find_text: str,
    extensions: list[str],
    targets: list[Path],
) -> tuple[list[Path], int, list[dict[str, str]]]:
    skipped: list[dict[str, str]] = []
    files = targets or _collect_files(directory, recursive)
    scanned_count = len(files)
    candidates: list[Path] = []

    for path in files:
        if extensions and path.suffix.lower() not in extensions:
            skipped.append({"path": str(path), "reason": "extension filter mismatch"})
            continue
        if find_text not in path.name:
            skipped.append({"path": str(path), "reason": "find_text not found in file name"})
            continue
        candidates.append(path)

    return candidates, scanned_count, skipped


def _plan_renames(
    paths: list[Path],
    find_text: str,
    replace_text: str,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    renamed: list[dict[str, str]] = []
    conflicts: list[dict[str, str]] = []
    destination_map: dict[Path, Path] = {}
    source_paths = {path.resolve() for path in paths}

    for source in paths:
        target = source.with_name(source.name.replace(find_text, replace_text)).resolve()

        if target == source.resolve():
            conflicts.append(
                {
                    "old_path": str(source),
                    "new_path": str(target),
                    "reason": "new name is identical to current name",
                }
            )
            continue

        if target in destination_map:
            conflicts.append(
                {
                    "old_path": str(source),
                    "new_path": str(target),
                    "reason": f"conflicts with another planned rename: {destination_map[target]}",
                }
            )
            continue

        if target.exists() and target not in source_paths:
            conflicts.append(
                {
                    "old_path": str(source),
                    "new_path": str(target),
                    "reason": "target path already exists",
                }
            )
            continue

        destination_map[target] = source
        renamed.append({"old_path": str(source), "new_path": str(target)})

    return renamed, conflicts


def _apply_renames(renamed: list[dict[str, str]]) -> None:
    staged: list[tuple[Path, Path, Path]] = []

    try:
        for index, item in enumerate(renamed):
            source = Path(item["old_path"])
            target = Path(item["new_path"])
            temp_path = _temporary_rename_path(source, index)
            source.rename(temp_path)
            staged.append((temp_path, source, target))

        for temp_path, _source, target in staged:
            temp_path.rename(target)
    except Exception:
        _rollback_staged_renames(staged)
        raise


def _temporary_rename_path(source: Path, index: int) -> Path:
    """Return a non-existing sibling path for two-phase rename application."""
    base_name = f".{source.name}.rename_files_tmp_{index}"
    candidate = source.with_name(base_name)
    attempt = 1
    while candidate.exists():
        candidate = source.with_name(f"{base_name}_{attempt}")
        attempt += 1
    return candidate


def _rollback_staged_renames(staged: list[tuple[Path, Path, Path]]) -> None:
    for temp_path, source, target in reversed(staged):
        if temp_path.exists() and not source.exists():
            temp_path.rename(source)
        elif target.exists() and not source.exists():
            target.rename(source)


if __name__ == "__main__":
    main()
