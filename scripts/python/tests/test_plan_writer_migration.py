"""Release gates for the plan to plan-writer identity cutover."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ROOT / "skills"
TARGET = SKILLS / "plan-writer"
SOURCE = SKILLS / "plan"


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_workspace_move_preserves_the_complete_relative_reference_subtree() -> None:
    expected = {
        "SKILL.md",
        "reference/README.md",
        "reference/scripts.md",
        "reference/task-authoring.md",
        "reference/workspace-contract.md",
    }
    actual = {
        path.relative_to(TARGET).as_posix()
        for path in TARGET.rglob("*")
        if path.is_file()
    }

    assert actual == expected
    assert TARGET.is_dir() and not TARGET.is_symlink()
    assert not SOURCE.exists()
    assert not SOURCE.is_symlink()


def test_collector_has_one_plan_writer_operation_and_no_plan_identity() -> None:
    result = subprocess.run(
        [
            "uv",
            "run",
            "--project",
            str(ROOT / "scripts/python"),
            "collect-skills",
            "--class",
            "operation",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    records = json.loads(result.stdout)
    matches = [record for record in records if record.get("name") == "plan-writer"]

    assert len(matches) == 1
    assert matches[0]["class"] == "operation"
    assert Path(matches[0]["path"]).resolve() == (TARGET / "SKILL.md").resolve()
    assert all(record.get("name") != "plan" for record in records)


def test_frontmatter_and_shared_contract_are_cut_over_before_authoring() -> None:
    workflow = _text("skills/plan-writer/SKILL.md")
    frontmatter = workflow.split("---", 2)[1]

    assert "name: plan-writer" in frontmatter
    assert "class: operation" in frontmatter
    assert "name: plan\n" not in frontmatter
    assert "# Plan Writer" in workflow
    assert "Load the shared task contract before authoring" in workflow
    assert workflow.index(
        "Load the shared task contract before authoring"
    ) < workflow.index("**Author tasks.**")
    assert "passive, documentation-only, and non-transitive" in workflow
    assert "../task-contract/reference/README.md" in workflow
    assert "proposal-derived" in workflow
    assert "Never modify source documents" in workflow
    assert "init-task-packet" in workflow
    assert "validate-task-structure" in workflow
    assert "--state-file tasks.json" in workflow


def test_script_reference_matches_publication_and_validation_contract() -> None:
    scripts = _text("skills/plan-writer/reference/scripts.md")
    workflow = _text("skills/plan-writer/SKILL.md")

    assert '--output-dir "$PLAN_DIR"' in scripts
    assert 'mv "$PUBLISHED_PATH" "$PLAN_DIR/tasks.json"' in scripts
    assert '--state-file "$PLAN_DIR/tasks.json"' in scripts
    assert '--input "$PLAN_DIR/tasks.json"' in scripts
    assert '$PLAN_DIR/.tasks' not in scripts
    assert "render-task-markdown" in workflow


def test_documented_state_file_validator_form_executes(tmp_path: Path) -> None:
    packet = {
        "summary": "validator command fixture",
        "tasks": [
            {
                "purpose": "Validate one task packet.",
                "context": (
                    "This fixture provides enough concrete context to satisfy the "
                    "shared task schema while exercising the documented plan-writer "
                    "validator command without mutating repository files. "
                )
                * 2,
                "filesToRead": [],
                "filesToWrite": [],
                "skills": ["generic-analysis"],
                "executionInstructions": [
                    {"step": 1, "action": "Validate the packet."}
                ],
                "expectedOutput": "One validated task packet.",
            }
        ],
    }
    state_file = tmp_path / "tasks.json"
    state_file.write_text(json.dumps(packet), encoding="utf-8")

    result = subprocess.run(
        [
            "uv",
            "run",
            "--project",
            str(ROOT / "scripts/python"),
            "validate-task-structure",
            "--state-file",
            str(state_file),
            "--schema",
            str(ROOT / "skills/breakdown-tasks/schema/task-packet.schema.json"),
            "--auto-fix",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_active_callers_lifecycle_mappings_and_fixtures_use_new_identity() -> None:
    assert "Load the `plan-writer` skill." in _text("commands/plan.md")
    assert "Load the `plan` skill." not in _text("commands/plan.md")
    assert "Load the `plan-writer` skill." in _text("commands/leeroy-jenkins.md")
    assert "`plan-writer` - Create copied-source task-plan workspaces." in _text(
        "agents/planner.md"
    )
    assert "`plan-writer` — create executable plan workspaces." in _text(
        "skills/README.md"
    )
    assert "supports: [breakdown-tasks, plan-writer]" in _text(
        "skills/task-contract/SKILL.md"
    )

    lifecycle_files = (
        "skills/planning-pipeline-architecture/SKILL.md",
        "skills/planning-pipeline-architecture/reference/plan-only.md",
        "skills/planning-pipeline-architecture/reference/analysis-to-plan.md",
        "skills/planning-pipeline-architecture/reference/proposal-to-plan.md",
        "skills/planning-pipeline-architecture/reference/analysis-to-proposal-to-plan.md",
    )
    for relative in lifecycle_files:
        text = _text(relative)
        assert "plan-writer" in text
        assert "`plan`" not in text

    for relative in (
        "scripts/python/test-data/semantic-selection-cases.json",
        "scripts/python/test-data/task-contract-selection-cases.json",
    ):
        data = json.loads(_text(relative))
        inventory = data["inventory"]
        assert any(
            item["name"] == "plan-writer"
            and item["path"] == "skills/plan-writer/SKILL.md"
            for item in inventory
        )
        assert all(item["name"] != "plan" for item in inventory)


def test_rollback_ledger_has_hash_backed_post_cutover_evidence() -> None:
    ledger = _text("reports/plan-writer-migration-ledger.md")
    post_cutover = ledger.split("Post-cutover SHA-256 values", 1)[1]
    recorded = {
        path: digest
        for digest, path in re.findall(
            r"^([0-9a-f]{64})\s+(skills/plan-writer/\S+)$",
            post_cutover,
            re.MULTILINE,
        )
    }

    expected_paths = {
        "skills/plan-writer/SKILL.md",
        "skills/plan-writer/reference/README.md",
        "skills/plan-writer/reference/scripts.md",
        "skills/plan-writer/reference/task-authoring.md",
        "skills/plan-writer/reference/workspace-contract.md",
    }
    assert set(recorded) == expected_paths
    for relative, digest in recorded.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest

    assert "Pre-cutover SHA-256 values" in ledger
    assert "Historical exclusions" in ledger
    assert "Rollback is bounded" in ledger
    assert "does not claim retroactive byte-level proof" in ledger
