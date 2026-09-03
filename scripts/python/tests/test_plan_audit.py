"""Focused fixtures for the read-only plan-audit operation.

All proposal fixtures use the one-document monolithic PROPOSAL.md format
introduced during the single-file migration.  Historical multi-file strings
are not used here; coverage for multi-file input path handling is exercised
through the parser's structured section extraction, source-documents
resolution, and connection of declared names to indexed sources.
"""
# ruff: noqa: E501

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "skills" / "plan-audit" / "scripts" / "plan_audit.py"
SPEC = importlib.util.spec_from_file_location("plan_audit_under_test", MODULE_PATH)
assert SPEC and SPEC.loader
plan_audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = plan_audit
SPEC.loader.exec_module(plan_audit)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


PROPOSAL_BASE = """---
title: audit fixture
slug: audit-fixture
created: "1725148800000"
created-at: "2024-09-01T00:00:00Z"
status: draft
readiness: review-ready
decision-owner: test-engineer
source-documents:
  - analysis/source.md
---
# Audit fixture

## Table of Contents

- [Recommendation](#recommendation)
- [Technical Rationale](#technical-rationale)
- [Questions](#questions)
- [Options Considered](#options-considered)
- [Implementation Details](#implementation-details)
- [Verification Criteria](#verification-criteria)
- [Sources](#sources)

## Recommendation
Adopt a read-only plan audit.

## Technical Rationale
The current plan needs independent evidence. The decision selects the audit behavior. Use stable, reproducible evidence.

## Questions

None.

## Options Considered
A read-only report is preferred.

## Implementation Details
Implement the audit report and collector provenance. Include the plan audit; exclude repair and approval. Preserve immutable inputs and write only the external report.{drift}

## Verification Criteria
The report exposes all three checks and stable findings.

## Sources
- [Source](./analysis/source.md)
"""


def _proposal(root: Path, *, drift: bool = False) -> None:
    """Create a one-document monolithic PROPOSAL.md with one copied source."""
    _write(root / "PROPOSAL.md", PROPOSAL_BASE.format(drift=" drift" if drift else ""))
    _write(root / "analysis" / "source.md", "# Source\nThe source supports the selected direction.\n")


def _task(*, skills: list[str] | None = None, compound: bool = False) -> dict[str, Any]:
    return {
        "taskId": "audit-report",
        "purpose": "Produce the immutable audit report" if not compound else "Audit the plan and repair the report",
        "context": (
            "Trace the Recommendation, Scope and Exclusions, Design Constraints, "
            "Implementation Details, and Verification Criteria from PROPOSAL.md. "
            "Preserve the Open Question: label and copied source identity. "
            "The task is read-only and writes only the external audit report."
        ),
        "filesToRead": ["PROPOSAL.md", "analysis/source.md"],
        "filesToWrite": ["audit-report.md"],
        "skills": skills or ["plan-audit"],
        "executionInstructions": [
            {"step": 1, "action": "Read the immutable plan snapshot."},
            {"step": 2, "action": "Write the external report."},
        ],
        "verification": ["The report contains all three independently statused checks."],
        "expectedOutput": "One UTF-8 Markdown audit report.",
        "verificationCoverage": {"observable": ["Report sections and disposition are present."], "coverage": "complete"},
        "antiPatternSignals": ["implementation-plus-tests"] if compound else ["none"],
        "purposeOutputAlignment": {"status": "aligned", "evidence": "The purpose names the one Markdown report."},
    }


def _plan(root: Path, tasks: list[dict[str, Any]], *, include_brief: bool = True) -> None:
    if include_brief:
        _write(root / "PLAN.md", "# Plan brief\nThe plan preserves recommendation, scope and exclusions, design constraints, implementation targets, and verification tests.\n")
    _write(root / "tasks.md", "# Tasks\n\nProduce the immutable audit report\n")
    (root / "analysis").mkdir(parents=True, exist_ok=True)
    _write(root / "analysis/source.md", "# Copied source\nThe source supports the selected direction.\n")
    _write(root / "tasks.json", json.dumps({"summary": "audit fixture", "tasks": tasks}, indent=2))


def _collector(root: Path, *, task_contract: bool = False) -> list[dict[str, Any]]:
    del root, task_contract
    records = [
        {
            "name": "plan-audit",
            "description": "Use when auditing one immutable proposal-derived plan snapshot without changing audited inputs.",
            "selection": {"role": "owner"},
            "class": "operation",
            "path": str(ROOT / "skills" / "plan-audit" / "SKILL.md"),
            "source": "project",
        },
        {
            "name": "plan-writer",
            "description": "Use when creating a source-document plan workspace that produces executable task JSON.",
            "selection": {"role": "owner"},
            "class": "operation",
            "path": str(ROOT / "skills" / "plan-writer" / "SKILL.md"),
            "source": "project",
        },
    ]
    records.append(
        {
            "name": "task-contract",
            "description": "Use when referencing shared task semantics.",
            "selection": {"role": "reference"},
            "class": "documentation",
            "path": str(ROOT / "skills" / "task-contract" / "SKILL.md"),
            "source": "project",
        }
    )
    return records


def _input(tmp_path: Path, *, copied: bool = False, comparison: Path | None = None) -> tuple[dict[str, Any], Path, Path]:
    plan = tmp_path / "plan"
    proposal = tmp_path / "proposal"
    _proposal(proposal)
    _plan(plan, [_task()])
    output = tmp_path / "reports" / "audit.md"
    output.parent.mkdir()
    baseline: dict[str, Any] = {"mode": "authoritative", "root": str(proposal)}
    if copied:
        manifest = []
        for path in sorted(proposal.rglob("*")):
            if path.is_file():
                data = path.read_bytes()
                manifest.append({"path": path.relative_to(proposal).as_posix(), "bytes": len(data), "sha256": plan_audit.hashlib.sha256(data).hexdigest()})
        baseline = {"mode": "copied-snapshot", "root": str(proposal), "unavailableReason": "authoritative unavailable", "originIdentity": "fixture-origin", "captureTime": "2026-08-24T00:00:00Z", "manifest": manifest}
    if comparison:
        baseline["comparisonSnapshot"] = {"root": str(comparison)}
    return {"planWorkspace": str(plan), "proposalBaseline": baseline, "assignmentInventory": None, "auditOutput": str(output)}, plan, proposal


def test_clean_report_is_composite_and_read_only(tmp_path: Path) -> None:
    raw, plan, proposal = _input(tmp_path)
    before = {path: path.read_bytes() for path in [*plan.rglob("*"), *proposal.rglob("*")] if path.is_file()}
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    assert result.overall == "PASS"
    assert [check.name for check in result.checks] == ["Proposal compliance", "Task atomicity", "Skill assignment"]
    assert "## Proposal compliance" in result.report
    assert "## Task atomicity" in result.report
    assert "## Skill assignment" in result.report
    assert result.report_path.read_text(encoding="utf-8").startswith("# Plan Audit Report")
    after = {path: path.read_bytes() for path in [*plan.rglob("*"), *proposal.rglob("*")] if path.is_file()}
    assert before == after


def test_compound_task_fails_only_atomicity_and_keeps_sections(tmp_path: Path) -> None:
    raw, plan, _ = _input(tmp_path)
    _plan(plan, [_task(compound=True)])
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    assert result.overall == "FAIL"
    assert result.checks[0].disposition == "PASS"
    assert result.checks[1].disposition == "FAIL"
    assert result.checks[2].disposition == "PASS"


def test_migration_compatible_omissions_are_conditional(tmp_path: Path) -> None:
    raw, plan, _ = _input(tmp_path)
    task = _task()
    for key in ("taskId", "verificationCoverage", "antiPatternSignals", "purposeOutputAlignment"):
        task.pop(key)
    _plan(plan, [task])
    result = plan_audit.audit(
        raw,
        workspace_root=tmp_path,
        collector_runner=lambda cwd: _collector(cwd),
    )
    assert result.overall == "CONDITIONAL PASS"
    assert result.checks[1].disposition == "CONDITIONAL PASS"


def test_blocked_collector_does_not_hide_other_checks(tmp_path: Path) -> None:
    raw, _, _ = _input(tmp_path)
    failed = plan_audit.CollectorResult(False, [], stderr="collector unavailable", returncode=1)
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda _cwd: failed)
    assert result.overall == "BLOCKED"
    assert result.checks[0].disposition == "PASS"
    assert result.checks[1].disposition == "PASS"
    assert result.checks[2].disposition == "BLOCKED"
    assert "## Task atomicity" in result.report


def test_input_drift_blocks_the_snapshot_after_checks_start(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    raw, plan, _ = _input(tmp_path)
    original = plan_audit._skill_check

    def mutate(*args: Any, **kwargs: Any) -> Any:
        result = original(*args, **kwargs)
        tasks_md = plan / "tasks.md"
        tasks_md.write_text(tasks_md.read_text(encoding="utf-8") + " external drift\n", encoding="utf-8")
        return result

    monkeypatch.setattr(plan_audit, "_skill_check", mutate)
    result = plan_audit.audit(
        raw,
        workspace_root=tmp_path,
        collector_runner=lambda cwd: _collector(cwd),
    )
    assert result.overall == "BLOCKED"
    assert all(check.disposition == "BLOCKED" for check in result.checks)
    assert any(item.criterion == "INPUT-DRIFT" for item in result.checks[0].diagnostics)


def test_passive_documentation_is_allowed_with_an_operation_owner(tmp_path: Path) -> None:
    raw, plan, _ = _input(tmp_path)
    _plan(plan, [_task(skills=["plan-audit", "task-contract"])])
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd, task_contract=True))

    assert result.checks[2].disposition == "PASS"


def test_passive_documentation_without_an_operation_owner_fails(tmp_path: Path) -> None:
    raw, plan, _ = _input(tmp_path)
    _plan(plan, [_task(skills=["task-contract"])])
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd, task_contract=True))

    assert result.checks[2].disposition == "FAIL"
    assert any(item.criterion == "EXECUTABLE-OWNER" for item in result.checks[2].diagnostics)


def test_mismatched_operation_contract_fails(tmp_path: Path) -> None:
    raw, plan, _ = _input(tmp_path)
    _plan(plan, [_task(skills=["plan-writer"])])
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert result.checks[2].disposition == "FAIL"
    assert any(item.criterion == "CONTRACT-FIT" for item in result.checks[2].diagnostics)


def test_persisted_stale_winner_is_comparison_failure_not_a_repair(tmp_path: Path) -> None:
    raw, _, _ = _input(tmp_path)
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        json.dumps(
            [
                {
                    "name": "plan-writer",
                    "class": "operation",
                    "path": str(tmp_path / "old-plan-writer" / "SKILL.md"),
                }
            ]
        ),
        encoding="utf-8",
    )
    raw["assignmentInventory"] = str(inventory)
    raw["auditOutput"] = str(tmp_path / "reports" / "stale.md")
    result = plan_audit.audit(
        raw,
        workspace_root=tmp_path,
        collector_runner=lambda cwd: _collector(cwd),
    )
    assert result.checks[2].disposition == "FAIL"
    assert any(
        item.criterion == "HISTORICAL-WINNER-DRIFT"
        for item in result.checks[2].diagnostics
    )
    assert "no correction" in result.report


def test_authoritative_copy_drift_is_stable_source_finding(tmp_path: Path) -> None:
    raw, _, proposal = _input(tmp_path)
    comparison = tmp_path / "copy"
    _proposal(comparison, drift=True)
    manifest = []
    for path in sorted(comparison.rglob("*")):
        if path.is_file():
            data = path.read_bytes()
            manifest.append(
                {
                    "path": path.relative_to(comparison).as_posix(),
                    "bytes": len(data),
                    "sha256": plan_audit.hashlib.sha256(data).hexdigest(),
                }
            )
    raw["proposalBaseline"]["comparisonSnapshot"] = {
        "root": str(comparison),
        "originIdentity": "comparison-origin",
        "captureTime": "2026-08-24T00:00:00Z",
        "manifest": manifest,
    }
    raw["auditOutput"] = str(tmp_path / "reports" / "drift.md")
    first = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    raw["auditOutput"] = str(tmp_path / "reports" / "drift-again.md")
    second = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    first_ids = [item.id for item in first.checks[0].diagnostics if item.criterion == "SOURCE-DRIFT"]
    second_ids = [item.id for item in second.checks[0].diagnostics if item.criterion == "SOURCE-DRIFT"]
    assert first.overall == "FAIL"
    assert first_ids == second_ids
    assert first_ids[0].startswith("PC-SOURCE-DRIFT-")


def test_copied_snapshot_requires_complete_provenance_and_manifest(tmp_path: Path) -> None:
    raw, _, _ = _input(tmp_path, copied=True)
    raw["proposalBaseline"]["originIdentity"] = ""
    with pytest.raises(plan_audit.AuditInputError):
        plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))


def test_output_boundary_refuses_existing_or_audited_target(tmp_path: Path) -> None:
    raw, plan, _ = _input(tmp_path)
    raw["auditOutput"] = str(plan / "inside.md")
    with pytest.raises(plan_audit.AuditInputError):
        plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))


def test_normal_plan_writer_workspace_does_not_require_a_separate_brief(tmp_path: Path) -> None:
    raw, plan, _ = _input(tmp_path)
    (plan / "PLAN.md").unlink()

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert result.checks[0].disposition == "PASS"
    assert not any(item.criterion == "PLAN-BRIEF" for item in result.checks[0].diagnostics)


def test_label_guidance_is_not_mistaken_for_an_unresolved_statement(tmp_path: Path) -> None:
    raw, _, proposal = _input(tmp_path)
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="").replace(
            "## Technical Rationale\nThe current plan needs independent evidence.",
            "## Technical Rationale\nThe current plan needs independent evidence. Preserve `Assumption:`, `Evidence Gap:`, and `Open Question:` labels when present.",
        ),
    )

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert not any(item.criterion == "LABEL-PRESERVATION" for item in result.checks[0].diagnostics)


def test_actual_unresolved_statement_must_be_preserved(tmp_path: Path) -> None:
    raw, _, proposal = _input(tmp_path)
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="").replace(
            "None.",
            "Open Question: Choose the release owner.",
        ),
    )

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert result.checks[0].disposition == "FAIL"
    assert any(item.criterion == "LABEL-PRESERVATION" for item in result.checks[0].diagnostics)


def test_coupled_multi_action_task_passes_with_complete_coupling_evidence(tmp_path: Path) -> None:
    raw, plan, _ = _input(tmp_path)
    task = _task()
    task["purpose"] = "Create and validate one immutable audit report."
    task["expectedOutput"] = "One created and validated audit report."
    task["couplingRationale"] = {
        "rationale": "Validation is completion evidence for the one report.",
        "sharedResult": "One immutable audit report.",
        "verification": "The report passes its contract checks.",
    }
    _plan(plan, [task])

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert result.checks[1].disposition == "PASS"


def test_separable_actions_fail_without_declared_anti_pattern_signal(tmp_path: Path) -> None:
    raw, plan, _ = _input(tmp_path)
    task = _task()
    task["purpose"] = "Analyze migration risk and implement the parser."
    task["expectedOutput"] = "A risk report and an updated parser module."
    task["filesToWrite"] = ["reports/risk.md", "src/parser.py"]
    task["antiPatternSignals"] = ["none"]
    _plan(plan, [task])

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert result.checks[1].disposition == "FAIL"
    assert any(item.criterion == "SPLIT-TEST" for item in result.checks[1].diagnostics)


def test_dependency_glob_matches_concrete_predecessor_read(tmp_path: Path) -> None:
    raw, plan, _ = _input(tmp_path)
    first = _task()
    first["taskId"] = "create-contract"
    first["filesToWrite"] = ["skills/task-contract/**"]
    second = _task()
    second["taskId"] = "consume-contract"
    second["filesToRead"].append("skills/task-contract/SKILL.md")
    second["dependencies"] = [{"taskId": "create-contract", "reason": "Consume the contract."}]
    _plan(plan, [first, second])

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert not any(item.criterion == "PREDECESSOR-READ" for item in result.checks[1].diagnostics)


def test_standalone_cli_supplies_structural_validator_dependencies(tmp_path: Path) -> None:
    raw, _, _ = _input(tmp_path)
    process = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--plan-workspace",
            raw["planWorkspace"],
            "--proposal-baseline",
            raw["proposalBaseline"]["root"],
            "--audit-output",
            raw["auditOutput"],
        ],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    assert process.returncode == 0, process.stderr
    payload = json.loads(process.stdout)
    assert payload["overall"] in {"PASS", "CONDITIONAL PASS", "FAIL", "BLOCKED"}
    assert "No module named 'jsonschema'" not in Path(payload["report"]).read_text(encoding="utf-8")


def test_blocking_evidence_gap_with_decision_ready_fails(tmp_path: Path) -> None:
    raw, _, proposal = _input(tmp_path)
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="")
        .replace("readiness: review-ready", "readiness: decision-ready")
        .replace(
            "None.",
            "Evidence Gap: Missing performance data blocks the architecture selection.",
        ),
    )

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert any(item.criterion == "BLOCKING-RESEARCH" for item in result.checks[0].diagnostics)
    assert result.checks[0].disposition == "FAIL"


def test_source_drift_declared_not_indexed_blocks_incomplete_baseline(tmp_path: Path) -> None:
    raw, _, proposal = _input(tmp_path)
    _write(proposal / "analysis" / "missing-source.md", "# Missing source\n")
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="").replace(
            "source-documents:\n  - analysis/source.md",
            "source-documents:\n  - analysis/source.md\n  - analysis/missing-source.md",
        ),
    )

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert result.checks[0].disposition == "BLOCKED"
    assert any(item.criterion == "BASELINE-COMPLETE" for item in result.checks[0].diagnostics)


# ---------------------------------------------------------------------------
# One-document monolithic proposal tests (migration completion coverage)
# ---------------------------------------------------------------------------


def test_valid_copied_snapshot_passes(tmp_path: Path) -> None:
    """A copied-snapshot with complete provenance and intact manifest passes."""
    raw, _, _ = _input(tmp_path, copied=True)
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    assert result.overall == "PASS"
    assert result.checks[0].disposition == "PASS"


def test_copied_manifest_missing_file_blocks_without_crashing(tmp_path: Path) -> None:
    raw, _, _ = _input(tmp_path, copied=True)
    raw["proposalBaseline"]["manifest"].append(
        {"path": "analysis/missing.md", "bytes": 1, "sha256": "0" * 64}
    )

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert result.overall == "BLOCKED"
    assert result.checks[0].disposition == "BLOCKED"


def test_missing_recommendation_section_fails(tmp_path: Path) -> None:
    """A one-document proposal without a Recommendation heading fails proposal compliance."""
    raw, _, proposal = _input(tmp_path)
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="").replace("## Recommendation\nAdopt a read-only plan audit.", ""),
    )
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    assert result.checks[0].disposition == "BLOCKED"
    assert any(item.criterion == "BASELINE-COMPLETE" for item in result.checks[0].diagnostics)


def test_missing_implementation_details_section_blocked(tmp_path: Path) -> None:
    """A one-document proposal without Implementation Details heading blocks proposal compliance."""
    raw, _, proposal = _input(tmp_path)
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="").replace(
            "## Implementation Details\nImplement the audit report and collector provenance.",
            "",
        ),
    )
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    assert result.checks[0].disposition == "BLOCKED"


def test_missing_verification_criteria_section_blocked(tmp_path: Path) -> None:
    """A one-document proposal without Verification Criteria heading blocks proposal compliance."""
    raw, _, proposal = _input(tmp_path)
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="").replace(
            "## Verification Criteria\nThe report exposes all three checks and stable findings.",
            "",
        ),
    )
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    assert result.checks[0].disposition == "BLOCKED"


def test_invalid_readiness_blocked(tmp_path: Path) -> None:
    """A one-document proposal with an unrecognized readiness value blocks proposal compliance."""
    raw, _, proposal = _input(tmp_path)
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="").replace("readiness: review-ready", "readiness: invalid-state"),
    )
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    assert result.checks[0].disposition == "BLOCKED"
    assert any(item.criterion == "BASELINE-COMPLETE" for item in result.checks[0].diagnostics)


def test_malformed_frontmatter_blocks_and_writes_a_report(tmp_path: Path) -> None:
    raw, _, proposal = _input(tmp_path)
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="").replace("title: audit fixture", "title: [broken"),
    )

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert result.overall == "BLOCKED"
    assert result.report_path.is_file()
    assert result.checks[0].disposition == "BLOCKED"


def test_complex_example_accepts_ordered_optional_h3_toc_entries() -> None:
    parsed = plan_audit._parse_proposal_md(
        ROOT / "skills" / "proposal" / "examples" / "complex-proposal" / "PROPOSAL.md"
    )

    assert parsed["valid"]


def test_missing_declared_source_file_blocked(tmp_path: Path) -> None:
    """A source-documents entry pointing to a missing file blocks proposal compliance."""
    raw, _, proposal = _input(tmp_path)
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="").replace(
            "source-documents:\n  - analysis/source.md",
            "source-documents:\n  - analysis/source.md\n  - analysis/absent.md",
        ),
    )
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    assert result.checks[0].disposition == "BLOCKED"
    assert any(
        "declared source is missing or not a regular file" in str(item.observed).lower()
        for item in result.checks[0].diagnostics
    )


def test_unsafe_path_in_source_documents_blocked(tmp_path: Path) -> None:
    """A source-documents entry resolving outside the proposal root blocks proposal compliance."""
    raw, _, proposal = _input(tmp_path)
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="").replace(
            "source-documents:\n  - analysis/source.md",
            "source-documents:\n  - analysis/source.md\n  - ../../../unsafe.md",
        ),
    )
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    assert result.checks[0].disposition == "BLOCKED"
    assert any(
        "declared source is unsafe" in str(item.observed).lower()
        for item in result.checks[0].diagnostics
    )


def test_task_atomicity_passes_with_one_document_baseline(tmp_path: Path) -> None:
    """Task atomicity check works against a one-document PROPOSAL.md baseline."""
    raw, plan, proposal = _input(tmp_path)
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    assert result.checks[1].disposition == "PASS"


def test_exact_skill_assignment_passes_with_one_document_baseline(tmp_path: Path) -> None:
    """Skill assignment check works against a one-document PROPOSAL.md baseline."""
    raw, _, _ = _input(tmp_path)
    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))
    assert result.checks[2].disposition == "PASS"


def test_missing_decision_owner_blocks_incomplete_baseline(tmp_path: Path) -> None:
    raw, _, proposal = _input(tmp_path)
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="").replace("decision-owner: test-engineer\n", ""),
    )

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert result.checks[0].disposition == "BLOCKED"
    assert any("decision-owner" in str(item.observed) for item in result.checks[0].diagnostics)


def test_duplicate_sources_identity_blocks_incomplete_baseline(tmp_path: Path) -> None:
    raw, _, proposal = _input(tmp_path)
    _write(
        proposal / "PROPOSAL.md",
        PROPOSAL_BASE.format(drift="").replace(
            "- [Source](./analysis/source.md)",
            "- [Source](./analysis/source.md)\n- [Duplicate](./analysis/source.md)",
        ),
    )

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert result.checks[0].disposition == "BLOCKED"
    assert any("duplicate internal identities" in str(item.observed) for item in result.checks[0].diagnostics)


def test_missing_table_of_contents_blocks_incomplete_baseline(tmp_path: Path) -> None:
    raw, _, proposal = _input(tmp_path)
    text = PROPOSAL_BASE.format(drift="")
    start = text.index("## Table of Contents")
    end = text.index("## Recommendation")
    _write(proposal / "PROPOSAL.md", text[:start] + text[end:])

    result = plan_audit.audit(raw, workspace_root=tmp_path, collector_runner=lambda cwd: _collector(cwd))

    assert result.checks[0].disposition == "BLOCKED"
    assert any("table of contents" in str(item.observed).lower() for item in result.checks[0].diagnostics)
