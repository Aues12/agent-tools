"""Statically check the locally declared contract of one tool."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from metadata import load_spec

NAME = re.compile(r"^[a-z][a-z0-9_]*$")
STATUSES = {"draft", "experimental", "stable"}


def validate(path: str | Path) -> dict:
    directory = Path(path).expanduser().resolve()
    findings = []

    def report(code: str, level: str, location: Path | str, detail: str):
        findings.append({"code": code, "level": level, "location": str(location),
                         "message": detail})

    if not directory.is_dir():
        raise ValueError(f"Not a tool directory: {directory}")
    for name in ("AGENTS.md", "SKILL.yaml"):
        if not (directory / name).is_file():
            report("missing_file", "error", directory / name, f"Required file is missing: {name}")
    for name in ("tests", "examples"):
        if not (directory / name).is_dir():
            report("missing_directory", "error", directory / name, f"Required directory is missing: {name}")
    spec_path = directory / "SKILL.yaml"
    if not spec_path.is_file():
        return _result(directory, findings)
    try:
        spec = load_spec(spec_path)
    except (ValueError, OSError, RuntimeError) as exc:
        report("invalid_metadata", "error", spec_path, str(exc))
        return _result(directory, findings)
    for key in ("name", "capability", "purpose"):
        if not isinstance(spec.get(key), str) or not spec[key].strip():
            report("missing_field", "error", f"{spec_path}:{key}", f"{key} must be non-empty text")
    if isinstance(spec.get("name"), str):
        if not NAME.fullmatch(spec["name"]):
            report("invalid_name", "error", f"{spec_path}:name", "Use snake_case")
        if spec["name"] != directory.name:
            report("name_mismatch", "error", f"{spec_path}:name", "Name differs from directory")
    if spec.get("type") != "tool":
        report("invalid_type", "error", f"{spec_path}:type", "type must be tool")
    if not isinstance(spec.get("status"), str) or spec["status"] not in STATUSES:
        report("invalid_status", "error", f"{spec_path}:status", "Unknown lifecycle status")

    interfaces = spec.get("interfaces")
    if not isinstance(interfaces, list) or not interfaces:
        report("missing_interfaces", "error", f"{spec_path}:interfaces", "Declare at least one interface")
        interfaces = []
    interface_names = set()
    for index, interface in enumerate(interfaces):
        location = f"{spec_path}:interfaces[{index}]"
        if not isinstance(interface, dict) or not isinstance(interface.get("name"), str):
            report("invalid_interface", "error", location, "Interface must have a name")
            continue
        name = interface["name"]
        if name in interface_names:
            report("duplicate_interface", "error", location, f"Duplicate interface: {name}")
        interface_names.add(name)
        entrypoint = interface.get("entrypoint")
        if not isinstance(entrypoint, str) or not entrypoint.strip():
            report("missing_entrypoint", "error", location, "Interface needs an entrypoint")
            continue
        target = directory / entrypoint.split()[0]
        if not target.is_file():
            report("missing_entrypoint_file", "error", target, "Entrypoint file is absent")
        if name == "python_api":
            callables = interface.get("callables")
            if not isinstance(callables, list) or not callables:
                report("missing_callables", "error", location, "python_api needs callables")
            elif target.is_file() and target.suffix == ".py":
                try:
                    tree = ast.parse(target.read_text(encoding="utf-8"))
                    exposed = {node.name for node in tree.body
                               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
                    exposed.update(alias.asname or alias.name
                                   for node in tree.body if isinstance(node, ast.ImportFrom)
                                   for alias in node.names)
                    exposed.update(target.id for node in tree.body
                                   if isinstance(node, (ast.Assign, ast.AnnAssign))
                                   for target in (node.targets if isinstance(node, ast.Assign)
                                                  else [node.target])
                                   if isinstance(target, ast.Name))
                    for callable_name in callables:
                        if callable_name not in exposed:
                            report("callable_not_found", "warning", target,
                                   f"Could not statically find callable: {callable_name}")
                except (SyntaxError, UnicodeError, OSError) as exc:
                    report("unreadable_entrypoint", "error", target, str(exc))

    operations = spec.get("operations")
    if not isinstance(operations, list) or not operations:
        report("missing_operations", "error", f"{spec_path}:operations", "Declare at least one operation")
        operations = []
    operation_names = set()
    for index, operation in enumerate(operations):
        location = f"{spec_path}:operations[{index}]"
        if not isinstance(operation, dict) or not isinstance(operation.get("name"), str):
            report("invalid_operation", "error", location, "Operation must have a name")
            continue
        name = operation["name"]
        if name in operation_names:
            report("duplicate_operation", "error", location, f"Duplicate operation: {name}")
        operation_names.add(name)
        via = operation.get("available_via")
        if not isinstance(via, list) or not via or any(
                not isinstance(v, str) or v not in interface_names for v in via):
            report("invalid_available_via", "error", location, "Reference declared interfaces")
        params = operation.get("params")
        if not isinstance(params, dict):
            report("invalid_params", "error", location, "params must be a mapping")
        else:
            for param, declaration in params.items():
                if not isinstance(declaration, dict) or not isinstance(declaration.get("type"), str):
                    report("invalid_param", "error", f"{location}.params.{param}", "Parameter needs a type")
                elif not isinstance(declaration.get("required"), bool):
                    report("missing_required", "warning", f"{location}.params.{param}",
                           "Declare whether the parameter is required")
        if not isinstance(operation.get("returns"), dict):
            report("invalid_returns", "error", location, "returns must be a mapping")
    effects = spec.get("side_effects")
    if not isinstance(effects, dict) or any(
            not isinstance(effects.get(key), list) for key in ("reads", "writes")):
        report("invalid_side_effects", "error", f"{spec_path}:side_effects",
               "Declare reads and writes lists")

    examples = directory / "examples"
    for example in sorted(examples.glob("*.json")) if examples.is_dir() else []:
        try:
            request = json.loads(example.read_text(encoding="utf-8"))
            if not isinstance(request, dict):
                report("invalid_example_json", "error", example, "Example must be a JSON object")
            elif "operation" not in request and not example.name.startswith("request"):
                continue  # Data examples need not be executable requests.
            elif request.get("operation") not in operation_names:
                report("invalid_example_operation", "error", example, "Example must name a declared operation")
            elif not isinstance(request.get("params"), dict):
                report("invalid_example_params", "error", example, "Example params must be an object")
        except (ValueError, UnicodeError, OSError) as exc:
            report("invalid_example_json", "error", example, str(exc))
    return _result(directory, findings)


def _result(directory: Path, findings: list[dict]) -> dict:
    return {"path": str(directory), "valid": not any(x["level"] == "error" for x in findings),
            "errors": sum(x["level"] == "error" for x in findings),
            "warnings": sum(x["level"] == "warning" for x in findings),
            "findings": findings,
            "note": "Static checks cannot prove runtime behavior or semantic correctness."}


def run(payload: dict) -> dict:
    try:
        if not isinstance(payload, dict) or payload.get("operation") != "validate":
            raise ValueError("Expected operation validate")
        params = payload.get("params")
        if not isinstance(params, dict):
            raise ValueError("params must be an object")
        result = validate(**params)
        return {"success": True, "message": "contract_validator completed",
                "result": result, "meta": {"operation": "validate", "read_only": True}}
    except (TypeError, ValueError, OSError) as exc:
        return {"success": False, "message": str(exc), "result": None,
                "error": {"type": type(exc).__name__, "message": str(exc)}}


if __name__ == "__main__":
    try:
        request = json.load(sys.stdin)
    except (ValueError, OSError):
        request = {}
    response = run(request)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    raise SystemExit(0 if response["success"] and response["result"]["valid"] else 1)
