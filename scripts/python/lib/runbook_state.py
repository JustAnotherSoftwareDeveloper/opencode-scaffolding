from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

try:
    from lib.json_validation import validate_json_path
except Exception:  # pragma: no cover - keeps v3 imports independent of retired JSON schemas
    validate_json_path = None  # type: ignore[assignment]


HARNESS_ROOT = Path(__file__).resolve().parents[3]


def create_runbook_state_directory(state_dir: Path) -> None:
    """Create the legacy state directory if it doesn't exist."""
    state_dir.mkdir(parents=True, exist_ok=True)


def utc_timestamp() -> str:
    """Return an RFC 3339 UTC timestamp with a trailing Z."""
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _worker_name(step: dict[str, Any]) -> str:
    worker = step.get("worker", {})
    return f"{worker.get('family', 'worker')}-{worker.get('size', 'dynamic')}"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _manifest_xml(root: str, runbook_id: str, item_type: str) -> str:
    timestamp = utc_timestamp()
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<{root}>
  <generated>{timestamp}</generated>
  <updated>{timestamp}</updated>
  <runbook_id>{escape(runbook_id)}</runbook_id>
  <items>
    <item id="initial" path="." type="{item_type}" description="Initial empty manifest placeholder" />
  </items>
</{root}>
'''


def create_default_manifest(path: Path, root: str, runbook_id: str, item_type: str | None = None) -> None:
    """Create one default manifest if absent (compatibility helper)."""
    if not path.exists():
        _write_text(path, _manifest_xml(root, runbook_id, item_type or root.replace("-manifest", "")))


def create_default_manifests_for_v3(runbook_dir: Path, runbook_id: str) -> None:
    """Create default v3 manifest indexes if absent (compatibility helper)."""
    create_default_manifest(runbook_dir / "evidence" / "index.xml", "evidence-manifest", runbook_id, "evidence")
    create_default_manifest(runbook_dir / "snippets" / "index.xml", "snippets-manifest", runbook_id, "snippets")
    create_default_manifest(runbook_dir / "reference" / "index.xml", "reference-manifest", runbook_id, "reference")


def seed_runbook_local_state(runbook_data: Any, runbook_path: Path) -> Path:
    """Seed v3 runbook-local state.xml and default manifest indexes."""
    runbook_dir = runbook_path.parent.resolve()
    runbook_id = runbook_data.get("id") or runbook_dir.name
    timestamp = utc_timestamp()
    steps = runbook_data.get("steps", [])

    step_xml = []
    dep_xml = []
    assignment_xml = []
    for step in steps:
        step_id = step.get("id")
        if not step_id:
            continue
        worker = _worker_name(step)
        inputs = "".join(f"\n        <inputs>{escape(str(item))}</inputs>" for item in step.get("context_package", {}).get("files_in_scope", []))
        step_xml.append(
            f'''    <step id="{escape(step_id)}">
      <status>pending</status>
      <objective>{escape(step.get('objective', ''))}</objective>{inputs}
      <context_summary></context_summary>
      <verification>
        <status>pending</status>
      </verification>
      <next_action></next_action>
      <worker>{escape(worker)}</worker>
    </step>'''
        )
        deps = runbook_data.get("dependency_graph", {}).get(step_id, [])
        dep_items = "".join(f"\n        <depends_on>{escape(str(dep))}</depends_on>" for dep in deps)
        dep_xml.append(f'''    <step id="{escape(step_id)}">{dep_items}
    </step>''')
        assignment_xml.append(f'''    <assignment step="{escape(step_id)}">{escape(worker)}</assignment>''')

    state_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<state>
  <metadata_schema_version>1</metadata_schema_version>
  <runbook>{escape(str(runbook_path))}</runbook>
  <plan>{escape(str(runbook_data.get('plan', '')))}</plan>
  <proposal>{escape(str(runbook_data.get('proposal', '')))}</proposal>
  <status>{escape(str(runbook_data.get('status', 'approved')))}</status>
  <created_at>{timestamp}</created_at>
  <updated_at>{timestamp}</updated_at>
  <steps>
{chr(10).join(step_xml)}
  </steps>
  <dependency_graph>
{chr(10).join(dep_xml)}
  </dependency_graph>
  <worker_assignments>
{chr(10).join(assignment_xml)}
  </worker_assignments>
</state>
'''
    state_path = runbook_dir / (runbook_data.get("state") or "state.xml")
    _write_text(state_path, state_xml)

    manifest_specs = [
        (runbook_data.get("evidence_manifest") or "evidence/index.xml", "evidence-manifest", "evidence"),
        (runbook_data.get("snippets_manifest") or "snippets/index.xml", "snippets-manifest", "snippets"),
        (runbook_data.get("reference_manifest") or "reference/index.xml", "reference-manifest", "reference"),
    ]
    for rel_path, root, item_type in manifest_specs:
        manifest_path = runbook_dir / rel_path
        if not manifest_path.exists():
            _write_text(manifest_path, _manifest_xml(root, runbook_id, item_type))
    return state_path


def seed_runbook_state_xml(runbook_data: Any, runbook_dir: Path) -> Path:
    """Compatibility wrapper for earlier v3 state seeding name."""
    return seed_runbook_local_state(runbook_data, runbook_dir / "main.xml")


def seed_runbook_state(runbook_data: Any, runbook_path: Path, state_dir: Path | None = None, harness_root: Path | None = None) -> None:
    """Seed runbook state.

    v3 writes runbook-local `state.xml` and manifest indexes. Legacy v1/v2 keeps
    the historical `.state/<id>/` JSON behavior when the retired JSON schemas are
    still available.
    """
    if runbook_data.get("format_version") == 3:
        seed_runbook_local_state(runbook_data, runbook_path)
        return

    if state_dir is None:
        raise ValueError("state_dir is required for legacy v1/v2 state seeding")
    harness_root = harness_root or HARNESS_ROOT
    state_init = runbook_data.get("state_initialization", {})
    metadata_schema_version = state_init.get("metadata_schema_version", 1)
    require_step_files = state_init.get("require_step_files", False)
    step_file_extension = state_init.get("step_file_extension", ".json")
    main_dashboard = state_init.get("main_dashboard", "MAIN.json")

    steps = runbook_data.get("steps", [])
    step_statuses = {step["id"]: "pending" for step in steps if step.get("id")}
    worker_assignments = {step["id"]: _worker_name(step) for step in steps if step.get("id")}
    timestamp = utc_timestamp()

    state_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "metadata_schema_version": metadata_schema_version,
        "runbook": str(runbook_path),
        "plan": runbook_data.get("plan"),
        "proposal": runbook_data.get("proposal"),
        "status": runbook_data.get("status", "draft"),
        "active_step": runbook_data.get("active_step"),
        "created_at": timestamp,
        "updated_at": timestamp,
        "steps": step_statuses,
        "dependency_graph": runbook_data.get("dependency_graph", {}),
        "blockers": [],
        "latest_verification": None,
    }
    metadata_path = state_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    metadata_schema_path = harness_root / "skills/runbook/schemas/state-metadata.schema.json"
    if validate_json_path and metadata_schema_path.exists():
        validate_json_path(metadata_path, metadata_schema_path)

    main_data = {
        "runbook_id": runbook_data.get("id"),
        "title": runbook_data.get("title"),
        "objective": runbook_data.get("objective"),
        "status": runbook_data.get("status", "draft"),
        "active_step": runbook_data.get("active_step"),
        "step_statuses": step_statuses,
        "blockers": [],
        "latest_verification": None,
        "worker_assignments": worker_assignments,
    }
    main_path = state_dir / main_dashboard
    main_path.write_text(json.dumps(main_data, indent=2), encoding="utf-8")
    main_schema_path = harness_root / "skills/runbook/schemas/state-main.schema.json"
    if validate_json_path and main_schema_path.exists():
        validate_json_path(main_path, main_schema_path)

    if require_step_files:
        for step in steps:
            step_id = step.get("id")
            if not step_id:
                continue
            context_package = step.get("context_package", {})
            step_inputs = []
            step_inputs.extend(context_package.get("relevant_state_files", []))
            step_inputs.extend(context_package.get("files_in_scope", []))
            step_data = {
                "step_id": step_id,
                "status": "pending",
                "objective": step.get("objective", ""),
                "inputs": step_inputs,
                "context_summary": "",
                "work_log": [],
                "outputs": [],
                "verification": {"status": "pending", "commands": []},
                "blockers": [],
                "next_action": "",
                "worker": _worker_name(step),
            }
            step_path = state_dir / f"{step_id}{step_file_extension}"
            step_path.write_text(json.dumps(step_data, indent=2), encoding="utf-8")
            step_schema_path = harness_root / "skills/runbook/schemas/state-step.schema.json"
            if validate_json_path and step_schema_path.exists():
                validate_json_path(step_path, step_schema_path)
