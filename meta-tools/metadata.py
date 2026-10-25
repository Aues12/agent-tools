"""Shared, read-only loading of local tool metadata."""
from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise RuntimeError("PyYAML is required; install the meta-tools extra") from exc


TOOL_DIRS = ("file-tools", "book-editing-tools", "meta-tools")


def load_spec(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping: {path}")
    return data


def discover_specs(root: Path):
    """Yield implemented tools; templates and draft skills are not tools."""
    for directory in TOOL_DIRS:
        base = root / directory
        if base.is_dir():
            for path in sorted(base.rglob("SKILL.yaml")):
                yield path


def registry_entry(root: Path, spec_path: Path, spec: dict) -> dict:
    """Project locally declared fields into the registry's current shape."""
    interfaces = spec.get("interfaces")
    operations = spec.get("operations")
    if not isinstance(interfaces, list) or not interfaces:
        raise ValueError(f"Missing interfaces: {spec_path}")
    if not isinstance(operations, list) or not operations:
        raise ValueError(f"Missing operations: {spec_path}")
    names = [item.get("name") for item in operations if isinstance(item, dict)]
    if len(names) != len(operations) or any(not isinstance(name, str) for name in names):
        raise ValueError(f"Invalid operations: {spec_path}")
    compact = []
    for item in interfaces:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise ValueError(f"Invalid interface: {spec_path}")
        fields = {key: item[key] for key in ("name", "entrypoint", "transport", "callables") if key in item}
        compact.append(fields)
    preferred = next((item for item in compact if item["name"] == "stdin_json"), compact[0])
    entry = {
        "name": spec.get("name"),
        "capability": spec.get("capability"),
        "path": spec_path.parent.relative_to(root).as_posix(),
        "entrypoint": preferred.get("entrypoint"),
        "transport": preferred.get("transport"),
        "status": spec.get("status"),
        "operations": names,
        "interfaces": compact,
    }
    if any(not isinstance(entry[key], str) or not entry[key] for key in
           ("name", "capability", "entrypoint", "transport", "status")):
        raise ValueError(f"Incomplete registry metadata: {spec_path}")
    return entry
