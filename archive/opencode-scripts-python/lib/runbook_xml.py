"""Runbook loader/validator with v3 XML target support and legacy compatibility.

Target v3 workspaces use `.runbooks/<id>/main.xml`, runbook-local
`state.xml`, `steps/<step-id>.xml`, and manifest indexes. Legacy v1 JSON and
transitional v2 XML are detected explicitly so imports and existing artifacts do
not fail merely because v3 became the target contract.
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


HARNESS_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = HARNESS_ROOT / "skills" / "runbook" / "schemas"


def _text(parent: etree._Element | None, name: str, default: str | None = "") -> str | None:
    if parent is None:
        return default
    child = parent.find(name)
    if child is None:
        return default
    value = child.text
    return value.strip() if value else default


def _items(parent: etree._Element | None, name: str) -> list[str]:
    if parent is None:
        return []
    container = parent.find(name)
    if container is None:
        return []
    return [(item.text or "").strip() for item in container.findall("item") if (item.text or "").strip()]


def _secure_parser() -> etree.XMLParser:
    return etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False, huge_tree=False, remove_blank_text=True)


def _schema_path(name: str = "runbook.xsd") -> Path:
    return SCHEMA_DIR / name


def _load_schema(name: str = "runbook.xsd") -> etree.XMLSchema:
    path = _schema_path(name)
    try:
        return etree.XMLSchema(etree.parse(str(path), parser=_secure_parser()))
    except (OSError, etree.XMLSyntaxError, etree.XMLSchemaParseError) as exc:
        raise XmlValidationError(f"Failed to load {name}: {exc}", path=path)


def _parse_xml(path: Path, expected_root: str, schema_name: str | None = None) -> tuple[etree._ElementTree, etree._Element]:
    try:
        tree = etree.parse(str(path), parser=_secure_parser())
    except OSError:
        raise XmlValidationError(f"XML file not found: {path}", path=path)
    except etree.XMLSyntaxError as exc:
        raise XmlValidationError(f"Malformed XML: {exc}", path=path)

    root = tree.getroot()
    if root.tag != expected_root:
        raise XmlValidationError(f"Expected XML root <{expected_root}>, got <{root.tag}>", path=path)

    if schema_name:
        schema = _load_schema(schema_name)
        if not schema.validate(tree):
            errors = [str(error) for error in schema.error_log]
            raise XmlValidationError("XML failed XSD validation", path=path, details={"errors": errors})
    return tree, root


def _validate_xml(path: Path, expected_root: str, schema_name: str) -> None:
    _parse_xml(path, expected_root, schema_name)


def detect_runbook_format(runbook_path: Path) -> int:
    if runbook_path.name == "runbook.json":
        return 1
    if runbook_path.name == "main.xml":
        _, root = _parse_xml(runbook_path, "runbook", None)
        raw = root.get("format_version")
        try:
            return int(raw) if raw is not None else 2
        except ValueError:
            raise RunbookLoadError(f"Invalid format_version on main.xml: {raw!r}", path=runbook_path)
    if runbook_path.name == "main.toon":
        raise RunbookLoadError("TOON runbooks are no longer supported; use main.xml", path=runbook_path)
    raise RunbookLoadError(
        f"Cannot detect runbook format from filename: {runbook_path.name}. Expected 'runbook.json' or 'main.xml'.",
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
    if runbook_data.get("format_version") == 3:
        expected = "state.xml"
        actual = runbook_data.get("state")
        if actual != expected:
            raise InvariantViolation("Invalid v3 state reference", path=runbook_path, details={"expected": expected, "actual": actual})
        return
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


def _parse_step_xml(step_path: Path, validate_xsd: bool = True) -> dict[str, Any]:
    _, root = _parse_xml(step_path, "step", "runbook.xsd" if validate_xsd else None)
    worker = root.find("worker")
    context = root.find("context_package")
    if worker is None or context is None:
        raise InvariantViolation("Step XML missing worker or context_package", path=step_path)
    return {
        "id": root.get("id"),
        "depends_on": _items(root, "depends_on"),
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


def _parse_runbook_xml(runbook_path: Path, format_version: int) -> dict[str, Any]:
    _, root = _parse_xml(runbook_path, "runbook", "runbook.xsd" if format_version == 3 else None)
    delegation_map = {entry.get("role"): entry.get("worker") for entry in root.findall("delegation_map/entry")}
    steps_index = [{"id": item.get("id"), "file": item.get("file")} for item in root.findall("steps/step_ref")]
    dep_graph = {item.get("id"): [dep.get("id") for dep in item.findall("depends_on") if dep.get("id")] for item in root.findall("dependency_graph/step")}
    eqc = root.find("embedded_quality_check")
    state_init = root.find("state_initialization")
    data: dict[str, Any] = {
        "artifact_type": root.get("artifact_type"),
        "format_version": format_version,
        "id": root.get("id"),
        "title": _text(root, "title"),
        "status": _text(root, "status"),
        "created_at": _text(root, "created_at"),
        "updated_at": _text(root, "updated_at"),
        "proposal": _text(root, "proposal"),
        "plan": _text(root, "plan"),
        "active_step": _text(root, "active_step", None) or None,
        "objective": _text(root, "objective"),
        "plan_summary": _text(root, "plan_summary"),
        "inputs": _items(root, "inputs"),
        "constraints": _items(root, "constraints"),
        "execution_strategy": _text(root, "execution_strategy"),
        "delegation_map": delegation_map,
        "steps": steps_index,
        "dependency_graph": dep_graph,
        "verification_gates": _items(root, "verification_gates"),
        "embedded_quality_check": {
            "performed_by": _text(eqc, "performed_by", None),
            "findings": _text(eqc, "findings", None),
            "status": _text(eqc, "status", "pending"),
        },
        "rollback_recovery": _text(root, "rollback_recovery"),
        "final_report_contract": _text(root, "final_report_contract"),
    }
    if format_version == 3:
        data.update(
            {
                "state": _text(root, "state"),
                "evidence_manifest": _text(root, "evidence_manifest", "evidence/index.xml"),
                "snippets_manifest": _text(root, "snippets_manifest", "snippets/index.xml"),
                "reference_manifest": _text(root, "reference_manifest", "reference/index.xml"),
            }
        )
    else:
        data.update(
            {
                "state_dir": _text(root, "state_dir"),
                "state_initialization": {
                    "metadata_schema_version": int(_text(state_init, "metadata_schema_version", "1")),
                    "require_step_files": _text(state_init, "require_step_files", "true") == "true",
                    "step_file_extension": _text(state_init, "step_file_extension", ".json"),
                    "main_dashboard": _text(state_init, "main_dashboard", "MAIN.json"),
                },
            }
        )
    return data


def load_step_files(runbook_dir: Path, steps_index: list[dict[str, Any]], validate_xsd: bool = True) -> list[LoadedStep]:
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
        data = _parse_step_xml(step_path, validate_xsd=validate_xsd)
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


def validate_required_fields(runbook_data: dict[str, Any], runbook_path: Path, format_version: int) -> None:
    common = [
        "id",
        "title",
        "objective",
        "plan_summary",
        "inputs",
        "constraints",
        "execution_strategy",
        "delegation_map",
        "steps",
        "dependency_graph",
        "verification_gates",
        "embedded_quality_check",
        "rollback_recovery",
        "final_report_contract",
        "status",
        "created_at",
        "updated_at",
        "proposal",
        "plan",
        "active_step",
    ]
    required = common + (["state", "evidence_manifest", "snippets_manifest", "reference_manifest"] if format_version == 3 else ["state_dir", "state_initialization"])
    for field in required:
        if field not in runbook_data:
            raise InvariantViolation(f"Runbook missing required field: '{field}'", path=runbook_path)


def validate_active_step(runbook_data: dict[str, Any], valid_step_ids: set[str], runbook_path: Path) -> None:
    active = runbook_data.get("active_step")
    if active is not None and active not in valid_step_ids:
        raise InvariantViolation(f"active_step references unknown step: '{active}'", path=runbook_path)


def _safe_workspace_ref(runbook_dir: Path, ref_path: str, expected_suffix: str, context: str) -> Path:
    if not ref_path or ref_path.startswith("/") or ".." in ref_path.split("/") or not ref_path.endswith(expected_suffix):
        raise InvariantViolation(f"Invalid {context} path: {ref_path}", path=runbook_dir)
    resolved = (runbook_dir / ref_path).resolve()
    try:
        resolved.relative_to(runbook_dir.resolve())
    except ValueError:
        raise InvariantViolation(f"{context} path escapes runbook directory: {ref_path}", path=runbook_dir)
    return resolved


def validate_v3_workspace_xml(runbook_dir: Path, runbook_data: dict[str, Any], require_workspace_xml: bool = True) -> None:
    state_path = _safe_workspace_ref(runbook_dir, runbook_data["state"], ".xml", "state")
    if state_path.exists():
        _validate_xml(state_path, "state", "state.xsd")
    elif require_workspace_xml:
        raise InvariantViolation(f"Required v3 state file not found: {state_path.relative_to(runbook_dir)}", path=runbook_dir)
    manifests = [
        ("evidence_manifest", "evidence-manifest", "evidence-manifest.xsd"),
        ("snippets_manifest", "snippets-manifest", "snippets-manifest.xsd"),
        ("reference_manifest", "reference-manifest", "reference-manifest.xsd"),
    ]
    for field, root, schema in manifests:
        path = _safe_workspace_ref(runbook_dir, runbook_data[field], "index.xml", field)
        if path.exists():
            _validate_xml(path, root, schema)
        elif require_workspace_xml:
            raise InvariantViolation(f"Required v3 manifest not found: {path.relative_to(runbook_dir)}", path=runbook_dir)


def merge_step_data(main_data: dict[str, Any], loaded_steps: list[LoadedStep]) -> list[dict[str, Any]]:
    by_id = {step.id: step.data for step in loaded_steps}
    return [by_id[ref["id"]] for ref in main_data.get("steps", []) if ref.get("id") in by_id]


def load_runbook(runbook_path: str | Path, allow_unreferenced_steps: bool = False, require_workspace_xml: bool = True) -> RunbookLoadResult:
    path = Path(runbook_path).resolve()
    format_version = detect_runbook_format(path)
    runbook_id, runbook_dir = validate_path_shape(path)
    warnings: list[str] = []
    if format_version == 1:
        data = load_json_runbook(path)
        steps: list[LoadedStep] = []
    else:
        if format_version not in {2, 3}:
            raise RunbookLoadError(f"Unsupported XML runbook format_version: {format_version}", path=path)
        main_data = _parse_runbook_xml(path, format_version)
        validate_runbook_id_matches(main_data, runbook_id, path)
        validate_state_dir(main_data, runbook_id, path)
        steps = load_step_files(runbook_dir, main_data.get("steps", []), validate_xsd=True)
        warnings = check_unreferenced_step_files(runbook_dir, steps, allow_unreferenced_steps)
        data = dict(main_data)
        data["steps"] = merge_step_data(main_data, steps)
        if format_version == 3:
            validate_v3_workspace_xml(runbook_dir, data, require_workspace_xml=require_workspace_xml)

    validate_runbook_id_matches(data, runbook_id, path)
    validate_state_dir(data, runbook_id, path)
    validate_required_fields(data, path, format_version)
    valid_step_ids = {step.id for step in steps} if format_version in {2, 3} else {s.get("id") for s in data.get("steps", []) if s.get("id")}
    validate_dependency_graph(data, valid_step_ids, path)
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
