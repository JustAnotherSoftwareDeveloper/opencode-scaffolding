"""XML runbook loader with v2 workspace support and legacy v1 JSON compatibility.

Canonical v2 workspaces use `.runbooks/<id>/main.xml` plus `steps/*.xml`.
Legacy v1 workspaces continue to use `.runbooks/<id>/runbook.json`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lxml import etree


class RunbookLoadError(Exception):
    """Raised when runbook loading or validation fails."""

    def __init__(self, message: str, path: Path | None = None, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.path = path
        self.details = details or {}


class InvariantViolation(RunbookLoadError):
    """Raised when a safety invariant check fails."""


class XmlValidationError(RunbookLoadError):
    """Raised when XML parsing or XSD validation fails."""


@dataclass
class LoadedStep:
    id: str
    source_file: Path
    data: dict[str, Any]


@dataclass
class RunbookLoadResult:
    runbook_id: str
    format_version: int
    source_path: Path
    data: dict[str, Any]
    steps: list[LoadedStep] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _text(parent: etree._Element, name: str, default: str | None = "") -> str | None:
    child = parent.find(name)
    if child is None:
        return default
    value = child.text
    return value.strip() if value else default


def _items(parent: etree._Element, name: str) -> list[str]:
    container = parent.find(name)
    if container is None:
        return []
    return [(item.text or "").strip() for item in container.findall("item") if (item.text or "").strip()]


def _secure_parser() -> etree.XMLParser:
    return etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        load_dtd=False,
        huge_tree=False,
        remove_blank_text=True,
    )


def _schema_path() -> Path:
    return Path(__file__).resolve().parents[3] / "skills" / "runbook" / "schemas" / "runbook.xsd"


def _load_schema() -> etree.XMLSchema:
    try:
        return etree.XMLSchema(etree.parse(str(_schema_path()), parser=_secure_parser()))
    except (OSError, etree.XMLSyntaxError, etree.XMLSchemaParseError) as exc:
        raise XmlValidationError(f"Failed to load runbook XSD: {exc}", path=_schema_path())


def _parse_xml(path: Path, expected_root: str) -> etree._Element:
    try:
        tree = etree.parse(str(path), parser=_secure_parser())
    except OSError:
        raise XmlValidationError(f"XML file not found: {path}", path=path)
    except etree.XMLSyntaxError as exc:
        raise XmlValidationError(f"Malformed XML: {exc}", path=path)

    root = tree.getroot()
    if root.tag != expected_root:
        raise XmlValidationError(f"Expected XML root <{expected_root}>, got <{root.tag}>", path=path)

    schema = _load_schema()
    if not schema.validate(tree):
        errors = [str(error) for error in schema.error_log]
        raise XmlValidationError("XML failed XSD validation", path=path, details={"errors": errors})
    return root


def detect_runbook_format(runbook_path: Path) -> int:
    if runbook_path.name == "runbook.json":
        return 1
    if runbook_path.name == "main.xml":
        return 2
    if runbook_path.name == "main.toon":
        raise RunbookLoadError("TOON runbooks are no longer supported; use main.xml", path=runbook_path)
    raise RunbookLoadError(
        f"Cannot detect runbook format from filename: {runbook_path.name}. Expected 'runbook.json' (v1) or 'main.xml' (v2).",
        path=runbook_path,
    )


def load_json_runbook(runbook_path: Path) -> dict[str, Any]:
    try:
        with runbook_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise RunbookLoadError(f"Runbook file not found: {runbook_path}", path=runbook_path)
    except json.JSONDecodeError as exc:
        raise RunbookLoadError("Invalid JSON in runbook", path=runbook_path, details={"line": exc.lineno, "column": exc.colno})


def validate_path_shape(runbook_path: Path) -> tuple[str, Path]:
    resolved = runbook_path.resolve()
    if resolved.parent.parent.name != ".runbooks":
        raise InvariantViolation(
            f"Runbook must be in .runbooks/<id>/ directory, got: {resolved}",
            path=runbook_path,
            details={"expected": ".runbooks/<id>/main.xml or .runbooks/<id>/runbook.json"},
        )
    return resolved.parent.name, resolved.parent


def validate_runbook_id_matches(runbook_data: dict[str, Any], expected_id: str, runbook_path: Path) -> None:
    actual_id = runbook_data.get("id")
    if actual_id != expected_id:
        raise InvariantViolation(
            f"Runbook id mismatch: directory is '{expected_id}' but runbook has '{actual_id}'",
            path=runbook_path,
            details={"expected_id": expected_id, "actual_id": actual_id},
        )


def validate_state_dir(runbook_data: dict[str, Any], runbook_id: str, runbook_path: Path) -> None:
    expected = f"../../.state/{runbook_id}/"
    actual = runbook_data.get("state_dir")
    if actual != expected:
        raise InvariantViolation("Invalid state_dir", path=runbook_path, details={"expected": expected, "actual": actual})


class StrictStepPathValidator:
    def validate(self, runbook_dir: Path, ref_path: str, context: str) -> Path:
        if not ref_path:
            raise InvariantViolation(f"Empty step reference path in {context}", path=runbook_dir)
        if ref_path.startswith("/"):
            raise InvariantViolation(f"Absolute step path not allowed in {context}: {ref_path}", path=runbook_dir)
        if ".." in ref_path.split("/"):
            raise InvariantViolation(f"Parent directory traversal not allowed in {context}: {ref_path}", path=runbook_dir)
        if not ref_path.startswith("steps/"):
            raise InvariantViolation(f"Step reference must be under 'steps/' in {context}: {ref_path}", path=runbook_dir)
        if not ref_path.endswith(".xml"):
            raise InvariantViolation(f"Step file must end with '.xml' in {context}: {ref_path}", path=runbook_dir)
        step_path = (runbook_dir / ref_path).resolve()
        try:
            step_path.relative_to(runbook_dir.resolve())
        except ValueError:
            raise InvariantViolation(f"Step path escapes runbook directory in {context}: {ref_path}", path=runbook_dir)
        return step_path


def _parse_step_xml(step_path: Path) -> dict[str, Any]:
    root = _parse_xml(step_path, "step")
    worker = root.find("worker")
    context = root.find("context_package")
    if worker is None or context is None:
        raise InvariantViolation("Step XML missing worker or context_package", path=step_path)
    return {
        "id": root.get("id"),
        "depends_on": _items(root, "depends_on"),
        "parallel_group": _text(root, "parallel_group"),
        "worker": {"family": worker.get("family"), "size": worker.get("size")},
        "skill": _text(root, "skill", None) or None,
        "minimum_capable_tier": _text(root, "minimum_capable_tier"),
        "context_package": {
            "user_requirement_slice": _text(context, "user_requirement_slice"),
            "relevant_proposal_sections": _items(context, "relevant_proposal_sections"),
            "relevant_state_files": _items(context, "relevant_state_files"),
            "files_in_scope": _items(context, "files_in_scope"),
            "files_out_scope": _items(context, "files_out_scope"),
            "expected_return_format": _text(context, "expected_return_format"),
        },
        "objective": _text(root, "objective"),
        "expected_output": _text(root, "expected_output"),
        "state_updates": _items(root, "state_updates"),
        "acceptance_criteria": _items(root, "acceptance_criteria"),
        "verification": _text(root, "verification"),
        "recovery": _text(root, "recovery"),
    }


def _parse_runbook_xml(runbook_path: Path) -> dict[str, Any]:
    root = _parse_xml(runbook_path, "runbook")
    delegation_map = {entry.get("role"): entry.get("worker") for entry in root.findall("delegation_map/entry")}
    steps_index = [{"id": item.get("id"), "file": item.get("file")} for item in root.findall("steps/step_ref")]
    dep_graph = {
        item.get("id"): [dep.get("id") for dep in item.findall("depends_on") if dep.get("id")]
        for item in root.findall("dependency_graph/step")
    }
    parallel_groups = {
        group.get("id"): [step.get("id") for step in group.findall("step") if step.get("id")]
        for group in root.findall("parallel_groups/group")
    }
    state = root.find("state_initialization")
    eqc = root.find("embedded_quality_check")
    return {
        "artifact_type": root.get("artifact_type"),
        "format_version": int(root.get("format_version", "2")),
        "id": root.get("id"),
        "title": _text(root, "title"),
        "status": _text(root, "status"),
        "created_at": _text(root, "created_at"),
        "updated_at": _text(root, "updated_at"),
        "proposal": _text(root, "proposal"),
        "plan": _text(root, "plan"),
        "state_dir": _text(root, "state_dir"),
        "active_step": _text(root, "active_step", None) or None,
        "objective": _text(root, "objective"),
        "plan_summary": _text(root, "plan_summary"),
        "inputs": _items(root, "inputs"),
        "constraints": _items(root, "constraints"),
        "execution_strategy": _text(root, "execution_strategy"),
        "delegation_map": delegation_map,
        "steps": steps_index,
        "dependency_graph": dep_graph,
        "parallel_groups": parallel_groups,
        "state_initialization": {
            "metadata_schema_version": int(_text(state, "metadata_schema_version", "1")) if state is not None else 1,
            "require_step_files": (_text(state, "require_step_files", "true") == "true") if state is not None else True,
            "step_file_extension": _text(state, "step_file_extension", ".json") if state is not None else ".json",
            "main_dashboard": _text(state, "main_dashboard", "MAIN.json") if state is not None else "MAIN.json",
        },
        "verification_gates": _items(root, "verification_gates"),
        "embedded_quality_check": {
            "performed_by": _text(eqc, "performed_by", None) if eqc is not None else None,
            "findings": _text(eqc, "findings", None) if eqc is not None else None,
            "status": _text(eqc, "status", "pending") if eqc is not None else "pending",
        },
        "rollback_recovery": _text(root, "rollback_recovery"),
        "final_report_contract": _text(root, "final_report_contract"),
    }


def load_step_files(runbook_dir: Path, steps_index: list[dict[str, Any]]) -> list[LoadedStep]:
    validator = StrictStepPathValidator()
    loaded: list[LoadedStep] = []
    seen: set[str] = set()
    for idx, step_ref in enumerate(steps_index):
        step_id = step_ref.get("id")
        file_ref = step_ref.get("file")
        if not step_id or not file_ref:
            raise InvariantViolation(f"Step index entry {idx} missing id or file", path=runbook_dir)
        if step_id in seen:
            raise InvariantViolation(f"Duplicate step id in index: '{step_id}'", path=runbook_dir)
        seen.add(step_id)
        step_path = validator.validate(runbook_dir, file_ref, f"step '{step_id}' at index {idx}")
        if not step_path.exists():
            raise InvariantViolation(f"Step file not found for '{step_id}': {file_ref}", path=runbook_dir)
        data = _parse_step_xml(step_path)
        if data.get("id") != step_id:
            raise InvariantViolation(f"Step ID mismatch: index has '{step_id}' but file has '{data.get('id')}'", path=step_path)
        if step_path.stem != step_id:
            raise InvariantViolation(f"Step filename mismatch: step id '{step_id}' should have filename '{step_id}.xml'", path=step_path)
        loaded.append(LoadedStep(id=step_id, source_file=step_path, data=data))
    return loaded


def check_unreferenced_step_files(runbook_dir: Path, loaded_steps: list[LoadedStep], allow_unreferenced: bool = False) -> list[str]:
    steps_dir = runbook_dir / "steps"
    if not steps_dir.exists():
        return []
    referenced = {step.source_file.resolve() for step in loaded_steps}
    warnings: list[str] = []
    for xml_file in steps_dir.glob("*.xml"):
        if xml_file.resolve() not in referenced:
            msg = f"Unreferenced step file: {xml_file.relative_to(runbook_dir)}"
            if allow_unreferenced:
                warnings.append(msg)
            else:
                raise InvariantViolation(f"{msg}. Either reference it in main.xml or remove it.", path=xml_file)
    return warnings


def validate_dependency_graph(runbook_data: dict[str, Any], valid_step_ids: set[str], runbook_path: Path) -> None:
    combined: dict[str, list[str]] = {step_id: list(deps) for step_id, deps in runbook_data.get("dependency_graph", {}).items()}
    for step in runbook_data.get("steps", []):
        step_id = step.get("id")
        if step_id:
            combined.setdefault(step_id, []).extend(step.get("depends_on", []))
    for step_id, deps in combined.items():
        if step_id not in valid_step_ids:
            raise InvariantViolation(f"Dependency references unknown step: '{step_id}'", path=runbook_path)
        for dep in deps:
            if dep not in valid_step_ids:
                raise InvariantViolation(f"Step '{step_id}' depends_on unknown step: '{dep}'", path=runbook_path)

    def visit(node: str, visited: set[str], stack: set[str]) -> None:
        visited.add(node)
        stack.add(node)
        for dep in combined.get(node, []):
            if dep not in visited:
                visit(dep, visited, stack)
            elif dep in stack:
                raise InvariantViolation(f"Circular dependency detected involving '{dep}'", path=runbook_path)
        stack.remove(node)

    visited: set[str] = set()
    for step_id in combined:
        if step_id not in visited:
            visit(step_id, visited, set())


def validate_parallel_groups(runbook_data: dict[str, Any], valid_step_ids: set[str], runbook_path: Path) -> None:
    for group, steps in runbook_data.get("parallel_groups", {}).items():
        for step_id in steps:
            if step_id not in valid_step_ids:
                raise InvariantViolation(f"Parallel group '{group}' references unknown step: '{step_id}'", path=runbook_path)


def validate_required_fields(runbook_data: dict[str, Any], runbook_path: Path, format_version: int) -> None:
    required = [
        "id", "title", "objective", "plan_summary", "inputs", "constraints", "execution_strategy",
        "delegation_map", "steps", "dependency_graph", "parallel_groups", "state_initialization",
        "verification_gates", "embedded_quality_check", "rollback_recovery", "final_report_contract",
        "status", "created_at", "updated_at", "proposal", "plan", "active_step",
    ]
    for field in required:
        if field not in runbook_data:
            raise InvariantViolation(f"Runbook missing required field: '{field}'", path=runbook_path)
    if format_version == 1 and not runbook_data.get("schema_version"):
        raise InvariantViolation("v1 runbook must specify 'schema_version' field", path=runbook_path)
    if format_version == 2 and runbook_data.get("format_version") != 2:
        raise InvariantViolation("v2 runbook must specify format_version 2", path=runbook_path)


def validate_active_step(runbook_data: dict[str, Any], valid_step_ids: set[str], runbook_path: Path) -> None:
    active = runbook_data.get("active_step")
    if active is not None and active not in valid_step_ids:
        raise InvariantViolation(f"active_step references unknown step: '{active}'", path=runbook_path)


def merge_step_data(main_data: dict[str, Any], loaded_steps: list[LoadedStep]) -> list[dict[str, Any]]:
    by_id = {step.id: step.data for step in loaded_steps}
    return [by_id[ref["id"]] for ref in main_data.get("steps", []) if ref.get("id") in by_id]


def load_runbook(runbook_path: str | Path, allow_unreferenced_steps: bool = False) -> RunbookLoadResult:
    path = Path(runbook_path).resolve()
    format_version = detect_runbook_format(path)
    runbook_id, runbook_dir = validate_path_shape(path)
    warnings: list[str] = []
    if format_version == 1:
        data = load_json_runbook(path)
        steps: list[LoadedStep] = []
    else:
        main_data = _parse_runbook_xml(path)
        validate_runbook_id_matches(main_data, runbook_id, path)
        validate_state_dir(main_data, runbook_id, path)
        steps = load_step_files(runbook_dir, main_data.get("steps", []))
        warnings = check_unreferenced_step_files(runbook_dir, steps, allow_unreferenced_steps)
        data = dict(main_data)
        data["steps"] = merge_step_data(main_data, steps)

    validate_runbook_id_matches(data, runbook_id, path)
    validate_state_dir(data, runbook_id, path)
    validate_required_fields(data, path, format_version)
    valid_step_ids = {step.id for step in steps} if format_version == 2 else {s.get("id") for s in data.get("steps", []) if s.get("id")}
    validate_dependency_graph(data, valid_step_ids, path)
    validate_parallel_groups(data, valid_step_ids, path)
    validate_active_step(data, valid_step_ids, path)
    return RunbookLoadResult(runbook_id=runbook_id, format_version=format_version, source_path=path, data=data, steps=steps, warnings=warnings)


def validate_runbook(runbook_path: str | Path, strict: bool = True) -> tuple[bool, list[str]]:
    messages: list[str] = []
    try:
        result = load_runbook(runbook_path, allow_unreferenced_steps=not strict)
        messages.append(f"✓ Runbook loaded successfully: {result.runbook_id}")
        messages.append(f"✓ Format: v{result.format_version}")
        messages.append(f"✓ Steps: {len(result.steps) if result.steps else len(result.data.get('steps', []))}")
        if result.warnings:
            messages.extend(f"⚠ {warning}" for warning in result.warnings)
            if strict:
                return False, messages
        return True, messages
    except RunbookLoadError as exc:
        messages.append(f"✗ Validation failed: {exc}")
        for key, value in exc.details.items():
            messages.append(f"  {key}: {value}")
        return False, messages
    except Exception as exc:
        messages.append(f"✗ Unexpected error: {exc}")
        return False, messages


__all__ = [
    "load_runbook",
    "validate_runbook",
    "RunbookLoadResult",
    "LoadedStep",
    "RunbookLoadError",
    "InvariantViolation",
    "XmlValidationError",
    "detect_runbook_format",
    "StrictStepPathValidator",
]
