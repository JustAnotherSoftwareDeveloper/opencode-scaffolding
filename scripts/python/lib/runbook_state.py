from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from lib.json_validation import JsonValidationError, validate_json_path

HARNESS_ROOT = Path(__file__).resolve().parents[3]


def create_runbook_state_directory(state_dir: Path) -> None:
    """Create the state directory if it doesn't exist."""
    state_dir.mkdir(parents=True, exist_ok=True)


def utc_timestamp() -> str:
    """Return an RFC 3339 UTC timestamp with a trailing Z."""
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def seed_runbook_state(runbook_data: Any, runbook_path: Path, state_dir: Path, harness_root: Path | None = None) -> None:
    """Seed the state directory with metadata, main, and step files."""
    # Extract state initialization configuration from runbook
    state_init = runbook_data.get("state_initialization", {})
    metadata_schema_version = state_init.get("metadata_schema_version", 1)
    require_step_files = state_init.get("require_step_files", False)
    step_file_extension = state_init.get("step_file_extension", ".json")
    main_dashboard = state_init.get("main_dashboard", "MAIN.json")
    
    harness_root = harness_root or HARNESS_ROOT
    steps = runbook_data.get("steps", [])
    step_statuses = {step["id"]: "pending" for step in steps if step.get("id")}
    worker_assignments = {
        step["id"]: f"{step.get('worker', {}).get('family', 'generic')}-{step.get('worker', {}).get('size', 'sm')}"
        for step in steps
        if step.get("id")
    }
    timestamp = utc_timestamp()

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
        "parallel_groups": runbook_data.get("parallel_groups", {}),
        "blockers": [],
        "latest_verification": None,
    }
    
    # Validate metadata against schema
    metadata_path = state_dir / "metadata.json"
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    # Validate metadata.json against schema
    metadata_schema_path = harness_root / "skills/runbook/schemas/state-metadata.schema.json"
    validate_json_path(metadata_path, metadata_schema_path)
    
    # Create main dashboard
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
    with main_path.open("w", encoding="utf-8") as f:
        json.dump(main_data, f, indent=2)
    
    # Validate main dashboard against schema
    main_schema_path = harness_root / "skills/runbook/schemas/state-main.schema.json"
    validate_json_path(main_path, main_schema_path)
    
    # Create step files if required
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
                "verification": {
                    "status": "pending",
                    "commands": []
                },
                "blockers": [],
                "next_action": "",
                "worker": f"{step.get('worker', {}).get('family', 'generic')}-{step.get('worker', {}).get('size', 'sm')}"
            }
            
            # Validate step data against schema
            step_path = state_dir / f"{step_id}{step_file_extension}"
            with step_path.open("w", encoding="utf-8") as f:
                json.dump(step_data, f, indent=2)
            
            step_schema_path = harness_root / "skills/runbook/schemas/state-step.schema.json"
            validate_json_path(step_path, step_schema_path)