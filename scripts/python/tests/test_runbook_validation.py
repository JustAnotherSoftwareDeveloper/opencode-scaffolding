"""Regression tests for v1 JSON and v2 XML runbook validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from lib.runbook_state import seed_runbook_state
from lib.runbook_xml import load_runbook, validate_runbook


def _step(step_id: str, depends_on: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": step_id,
        "depends_on": depends_on or [],
        "parallel_group": "group-1",
        "worker": {"family": "coding", "size": "md"},
        "skill": None,
        "minimum_capable_tier": "md",
        "context_package": {
            "user_requirement_slice": f"Test requirement for {step_id}",
            "relevant_proposal_sections": [],
            "relevant_state_files": [],
            "files_in_scope": [],
            "files_out_scope": [],
            "expected_return_format": "Test format",
        },
        "objective": f"Test step {step_id}",
        "expected_output": f"Test output {step_id}",
        "state_updates": [],
        "acceptance_criteria": ["Test criterion"],
        "verification": f"Test verification {step_id}",
        "recovery": f"Test recovery {step_id}",
    }


def _runbook_data(runbook_id: str, steps: list[dict[str, Any]]) -> dict[str, Any]:
    step_ids = [step["id"] for step in steps]
    return {
        "artifact_type": "runbook",
        "schema_version": 1,
        "id": runbook_id,
        "title": "Test Runbook",
        "status": "executing",
        "created_at": "2026-05-15T00:00:00Z",
        "updated_at": "2026-05-15T00:00:00Z",
        "proposal": "../../.proposals/test.md",
        "plan": "../../.plans/test.md",
        "state_dir": f"../../.state/{runbook_id}/",
        "active_step": step_ids[0] if step_ids else None,
        "objective": "Test runbook validation",
        "plan_summary": "Testing runbook validation",
        "inputs": [],
        "constraints": [],
        "execution_strategy": "Test strategy",
        "delegation_map": {},
        "steps": steps,
        "dependency_graph": {},
        "parallel_groups": {"group-1": step_ids} if step_ids else {},
        "state_initialization": {
            "metadata_schema_version": 1,
            "require_step_files": True,
            "step_file_extension": ".json",
            "main_dashboard": "MAIN.json",
        },
        "verification_gates": [],
        "embedded_quality_check": {"performed_by": None, "findings": [], "status": "pending"},
        "rollback_recovery": "Test recovery",
        "final_report_contract": "Test contract",
    }


def _items(values: list[str]) -> str:
    return "".join(f"<item>{escape(value)}</item>" for value in values)


def _step_xml(step: dict[str, Any]) -> str:
    ctx = step["context_package"]
    skill = step.get("skill") or ""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<step id="{step['id']}">
  <depends_on>{_items(step['depends_on'])}</depends_on>
  <parallel_group>{escape(step['parallel_group'])}</parallel_group>
  <worker family="{step['worker']['family']}" size="{step['worker']['size']}" />
  <skill>{escape(skill)}</skill>
  <minimum_capable_tier>{escape(step['minimum_capable_tier'])}</minimum_capable_tier>
  <context_package>
    <user_requirement_slice>{escape(ctx['user_requirement_slice'])}</user_requirement_slice>
    <relevant_proposal_sections>{_items(ctx['relevant_proposal_sections'])}</relevant_proposal_sections>
    <relevant_state_files>{_items(ctx['relevant_state_files'])}</relevant_state_files>
    <files_in_scope>{_items(ctx['files_in_scope'])}</files_in_scope>
    <files_out_scope>{_items(ctx['files_out_scope'])}</files_out_scope>
    <expected_return_format>{escape(ctx['expected_return_format'])}</expected_return_format>
  </context_package>
  <objective>{escape(step['objective'])}</objective>
  <expected_output>{escape(step['expected_output'])}</expected_output>
  <state_updates>{_items(step['state_updates'])}</state_updates>
  <acceptance_criteria>{_items(step['acceptance_criteria'])}</acceptance_criteria>
  <verification>{escape(step['verification'])}</verification>
  <recovery>{escape(step['recovery'])}</recovery>
</step>
'''


def _write_v1_runbook(tmp_path: Path, runbook_id: str = "test-legacy-runbook") -> Path:
    runbook_dir = tmp_path / ".runbooks" / runbook_id
    runbook_dir.mkdir(parents=True)
    runbook_file = runbook_dir / "runbook.json"
    runbook_file.write_text(json.dumps(_runbook_data(runbook_id, [_step("01-example")]), indent=2), encoding="utf-8")
    return runbook_file


def _write_v2_runbook(
    tmp_path: Path,
    runbook_id: str = "test-v2-runbook",
    steps: list[dict[str, Any]] | None = None,
    *,
    step_refs: list[dict[str, str]] | None = None,
    state_dir: str | None = None,
) -> Path:
    steps = steps or [_step("01-example"), _step("02-another", ["01-example"])]
    runbook_dir = tmp_path / ".runbooks" / runbook_id
    steps_dir = runbook_dir / "steps"
    steps_dir.mkdir(parents=True)
    refs = step_refs or [{"id": step["id"], "file": f"steps/{step['id']}.xml"} for step in steps]
    dep_steps = "".join(
        f'''<step id="{step['id']}">{''.join(f'<depends_on id="{dep}" />' for dep in step['depends_on'])}</step>'''
        for step in steps
    )
    ref_xml = "".join(f'<step_ref id="{ref["id"]}" file="{ref["file"]}" />' for ref in refs)
    group_steps = "".join(f'<step id="{step["id"]}" />' for step in steps)
    main_file = runbook_dir / "main.xml"
    main_file.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<runbook artifact_type="runbook" format_version="2" id="{runbook_id}">
  <title>Test Runbook</title><status>executing</status><created_at>2026-05-15T00:00:00Z</created_at><updated_at>2026-05-15T00:00:00Z</updated_at>
  <proposal>../../.proposals/test.md</proposal><plan>../../.plans/test.md</plan><state_dir>{state_dir or f'../../.state/{runbook_id}/'}</state_dir><active_step>{steps[0]['id'] if steps else ''}</active_step>
  <objective>Test runbook validation</objective><plan_summary>Testing runbook validation</plan_summary>
  <inputs/><constraints/><execution_strategy>Test strategy</execution_strategy><delegation_map/>
  <steps>{ref_xml}</steps><dependency_graph>{dep_steps}</dependency_graph><parallel_groups><group id="group-1">{group_steps}</group></parallel_groups>
  <state_initialization><metadata_schema_version>1</metadata_schema_version><require_step_files>true</require_step_files><step_file_extension>.json</step_file_extension><main_dashboard>MAIN.json</main_dashboard></state_initialization>
  <verification_gates/><embedded_quality_check><performed_by/><findings/><status>pending</status></embedded_quality_check>
  <rollback_recovery>Test recovery</rollback_recovery><final_report_contract>Test contract</final_report_contract>
</runbook>
''', encoding="utf-8")
    for step in steps:
        (steps_dir / f"{step['id']}.xml").write_text(_step_xml(step), encoding="utf-8")
    return main_file


def test_legacy_v1_compatibility(tmp_path: Path) -> None:
    runbook_file = _write_v1_runbook(tmp_path)
    is_valid, messages = validate_runbook(runbook_file)
    assert is_valid, messages
    result = load_runbook(runbook_file)
    assert result.runbook_id == "test-legacy-runbook"
    assert result.format_version == 1


def test_valid_v2_xml_runbook_loads_and_seeds_state(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(tmp_path)
    is_valid, messages = validate_runbook(main_file)
    assert is_valid, messages
    result = load_runbook(main_file)
    assert result.runbook_id == "test-v2-runbook"
    assert result.format_version == 2
    assert [step.id for step in result.steps] == ["01-example", "02-another"]
    assert [step["id"] for step in result.data["steps"]] == ["01-example", "02-another"]
    state_dir = tmp_path / ".state" / "test-v2-runbook"
    state_dir.mkdir(parents=True)
    seed_runbook_state(result.data, main_file, state_dir)
    assert (state_dir / "metadata.json").exists()
    assert (state_dir / "MAIN.json").exists()
    assert (state_dir / "01-example.json").exists()
    assert (state_dir / "02-another.json").exists()


def test_v2_dependency_cycle_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(tmp_path, "test-cycle-runbook", [_step("01-example", ["02-another"]), _step("02-another", ["01-example"])])
    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("circular dependency" in msg.lower() for msg in messages), messages


def test_v2_filename_stem_mismatch_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(tmp_path, "test-mismatch-runbook", [_step("01-example")], step_refs=[{"id": "01-example", "file": "steps/02-wrong-name.xml"}])
    (main_file.parent / "steps" / "02-wrong-name.xml").write_text(_step_xml(_step("01-example")), encoding="utf-8")
    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("filename mismatch" in msg.lower() for msg in messages), messages


def test_v2_wrong_state_dir_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(tmp_path, "test-wrong-state-runbook", [_step("01-example")], state_dir="../../.state/wrong-runbook/")
    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("state_dir" in msg.lower() for msg in messages), messages


def test_v2_missing_step_file_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(tmp_path, "test-missing-step-runbook", [_step("01-example")], step_refs=[{"id": "01-example", "file": "steps/01-example.xml"}, {"id": "02-missing", "file": "steps/02-missing.xml"}])
    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("not found" in msg.lower() for msg in messages), messages


def test_v2_unknown_dependency_reference_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(tmp_path, "test-unknown-dependency-runbook", [_step("01-example", ["99-missing"])])
    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("unknown step" in msg.lower() for msg in messages), messages


def test_v2_unsafe_step_path_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(tmp_path, "test-unsafe-path-runbook", [_step("01-example")], step_refs=[{"id": "01-example", "file": "../01-example.xml"}])
    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("traversal" in msg.lower() or "steps/" in msg.lower() for msg in messages), messages


def test_v2_malformed_xml_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(tmp_path, "test-malformed-runbook", [_step("01-example")])
    (main_file.parent / "steps" / "01-example.xml").write_text("<step><broken></step>", encoding="utf-8")
    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("malformed xml" in msg.lower() or "validation failed" in msg.lower() for msg in messages), messages


def test_v2_unreferenced_step_file_fails(tmp_path: Path) -> None:
    main_file = _write_v2_runbook(tmp_path, "test-unreferenced-runbook", [_step("01-example")])
    (main_file.parent / "steps" / "02-extra.xml").write_text(_step_xml(_step("02-extra")), encoding="utf-8")
    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("unreferenced" in msg.lower() for msg in messages), messages


def test_v2_dtd_entity_input_fails(tmp_path: Path) -> None:
    runbook_dir = tmp_path / ".runbooks" / "test-malicious-runbook"
    runbook_dir.mkdir(parents=True)
    main_file = runbook_dir / "main.xml"
    main_file.write_text('''<?xml version="1.0"?>
<!DOCTYPE runbook [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<runbook artifact_type="runbook" format_version="2" id="test-malicious-runbook"><title>&xxe;</title></runbook>
''', encoding="utf-8")
    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("xml" in msg.lower() or "entity" in msg.lower() or "validation failed" in msg.lower() for msg in messages), messages


def test_main_toon_is_rejected_after_hard_cutover(tmp_path: Path) -> None:
    runbook_dir = tmp_path / ".runbooks" / "test-toon-rejected"
    runbook_dir.mkdir(parents=True)
    main_file = runbook_dir / "main.toon"
    main_file.write_text("id: test-toon-rejected\n", encoding="utf-8")
    is_valid, messages = validate_runbook(main_file)
    assert not is_valid
    assert any("no longer supported" in msg.lower() for msg in messages), messages
