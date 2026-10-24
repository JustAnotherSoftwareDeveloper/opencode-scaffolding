"""Release gates for the plan to plan-writer identity cutover."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ROOT / "skills"
TARGET = SKILLS / "plan-writer"
SOURCE = SKILLS / "plan"


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _assert_three_stage_collection_contract(workflow: str) -> None:
    """Check distinct ordered class calls and task-specific assignment rules."""
    execution_match = re.search(
        r"(?ms)^## Execution\s*\n(?P<section>.*?)(?=^## [^\n]+|\Z)",
        workflow,
    )
    assert execution_match is not None
    execution = execution_match.group("section")

    calls: list[tuple[tuple[str, ...], int]] = []
    for block in re.finditer(
        r"```(?:bash|sh)\s*\n(.*?)```", execution, re.DOTALL
    ):
        command_block = re.sub(r"\\\s*\n\s*", " ", block.group(1))
        for invocation in re.finditer(
            r"\bcollect-skills\b([^\n]*)", command_block
        ):
            classes = tuple(
                re.findall(
                    r"--class(?:=|\s+)([a-z][\w-]*)", invocation.group(1)
                )
            )
            calls.append((classes, block.start(1) + invocation.start()))

    assert [classes for classes, _ in calls] == [
        ("planning",),
        ("operation",),
        ("documentation",),
    ]

    execution_lowered = " ".join(execution.lower().split())
    for stage in ("planning", "operation", "documentation"):
        assert f"collect {stage} skills once per request" in execution_lowered

    task_contract_load = re.search(
        r"\*\*Load the shared task contract before authoring\.", execution
    )
    author_tasks = re.search(r"\*\*Author tasks\.", execution)
    assignment = re.search(
        r"\*\*Assign skills after boundary acceptance\.", execution
    )
    assert task_contract_load is not None
    assert author_tasks is not None
    assert assignment is not None
    assert calls[-1][1] < task_contract_load.start() < author_tasks.start()
    assert author_tasks.start() < assignment.start()

    assert (
        "keep this operation result distinct for later executable assignment"
        in execution_lowered
    )
    assert (
        "keep this documentation result distinct and available for the "
        "pre-authoring "
        "load and later task assignment" in execution_lowered
    )
    assert (
        "the distinct operation and documentation results to the llm only "
        "after "
        "task boundaries are accepted" in execution_lowered
    )
    assert (
        "actively consider whether a documentation profile adds distinct"
        in execution_lowered
    )
    assert "material execution value for that task beyond its context" in (
        execution_lowered
    )
    assert "listed materials" in execution_lowered
    assert "zero documentation assignments is valid" in execution_lowered
    assert "assign no more than two" in execution_lowered
    assert "this is not a blanket ban on `task-contract`" in execution_lowered
    assert "do not recollect for each task" in execution_lowered
    workflow_lowered = " ".join(workflow.lower().split())
    assert "without per-task recollection or task-semantic filtering" in (
        workflow_lowered
    )


def test_workspace_move_preserves_the_complete_relative_reference_subtree() -> (
    None
):
    """Verify the plan-writer move preserves its complete reference subtree."""
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
    """Verify collection exposes plan-writer, not the retired identity."""
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
    matches = [
        record for record in records if record.get("name") == "plan-writer"
    ]

    assert len(matches) == 1
    assert matches[0]["class"] == "operation"
    assert Path(matches[0]["path"]).resolve() == (TARGET / "SKILL.md").resolve()
    assert all(record.get("name") != "plan" for record in records)


def test_frontmatter_and_shared_contract_are_cut_over_before_authoring() -> (
    None
):
    """Verify plan-writer metadata and shared contract completed the cutover."""
    workflow = _text("skills/plan-writer/SKILL.md")
    frontmatter = workflow.split("---", 2)[1]

    assert "name: plan-writer" in frontmatter
    assert "class: operation" in frontmatter
    assert (
        "correcting bounded audit findings in an existing plan" in frontmatter
    )
    assert "correct plan-owned audit findings" in frontmatter
    assert "same-workspace correction" in frontmatter
    assert "name: plan\n" not in frontmatter
    assert "# Plan Writer" in workflow
    assert "Load the shared task contract before authoring" in workflow
    assert workflow.index(
        "Load the shared task contract before authoring"
    ) < workflow.index("**Author tasks.**")
    assert "passive, documentation-only, and non-transitive" in workflow
    assert "already-loaded `task-contract` documentation skill" in workflow
    assert "../task-contract/reference/README.md" not in workflow
    assert "proposal-derived" in workflow
    assert "Never modify source documents" in workflow
    assert "init-task-packet" in workflow
    assert "validate-task-structure" in workflow
    assert "--state-file tasks.json" in workflow
    assert "Require the author to select one packet slug" in workflow
    assert "Never derive," in workflow
    assert "normalize, or locally validate it" in workflow


def test_plan_writer_collection_and_assignment_contract() -> None:
    """Verify the updated producer and task-authoring handoff contract."""
    workflow = _text("skills/plan-writer/SKILL.md")
    authoring = _text("skills/plan-writer/reference/task-authoring.md")

    _assert_three_stage_collection_contract(workflow)

    normalized_authoring = " ".join(authoring.split()).lower()
    assert (
        "after task boundaries are accepted, assign skills inline from the "
        "distinct "
        "operation and documentation results" in normalized_authoring
    )
    assert "the passive `task-contract` record is context only" in (
        normalized_authoring
    )


def test_script_reference_matches_publication_and_validation_contract() -> None:
    """Verify plan-writer script commands match publication and validation."""
    scripts = _text("skills/plan-writer/reference/scripts.md")
    workflow = _text("skills/plan-writer/SKILL.md")

    assert '--output-dir "$PLAN_DIR"' in scripts
    assert 'mv "$PUBLISHED_PATH" "$PLAN_DIR/tasks.json"' in scripts
    assert '--state-file "$PLAN_DIR/tasks.json"' in scripts
    assert '--input "$PLAN_DIR/tasks.json"' in scripts
    assert "$PLAN_DIR/.tasks" not in scripts
    assert "render-task-markdown" in workflow


def test_bounded_correction_stays_in_place_and_requires_fresh_reaudit() -> None:
    """Keep initial creation distinct from correction of an audited plan."""
    workflow = _text("skills/plan-writer/SKILL.md")
    scripts = _text("skills/plan-writer/reference/scripts.md")
    initial, correction = workflow.split(
        "### Bounded Audit-Finding Correction", maxsplit=1
    )
    correction_scripts = scripts.split(
        "For a bounded plan-owned correction", maxsplit=1
    )[1]

    assert "always create a new plan workspace" in initial
    assert "Create `.plans/<epoch-ms>-<workspace-slug>/`" in initial
    assert "init-task-packet" in initial
    assert "Do not use `--overwrite` for initial publication" in initial

    assert (
        "Require the existing plan-directory path, exact audit report (or a "
        "finding extract retaining its run identity and complete input "
        "manifest), finding IDs, and proposal baseline."
    ) in correction
    assert (
        "manifest identifies this target's pre-correction `tasks.json` and "
        "`tasks.md` and all supplied baseline files by path and recorded "
        "SHA-256"
    ) in correction
    assert "block missing, ambiguous, or mismatched identity" in correction
    assert "Correct only the reported, plan-writer-owned findings" in correction
    assert "preserving unrelated task content and packet identity" in correction
    assert (
        "The only writable files are that `tasks.json` and its `tasks.md`; "
        "never modify copied sources or the proposal baseline"
    ) in correction
    assert (
        "Validate the revised `tasks.json` with step 14's state-file command "
        "but omit `--auto-fix`"
    ) in correction
    assert (
        "inspect each diff and fix only finding-authorized violations, "
        "including `skills` entries only when that finding authorizes them"
        in correction
    )
    assert (
        "Do not create `draft.json`, invoke `init-task-packet`, or create, "
        "rename, or replace a plan workspace."
    ) in correction
    assert (
        "rerender from the existing `tasks.json` with `--overwrite`"
        in correction
    )
    assert "output path must be exactly `$PLAN_DIR/tasks.md`" in correction
    assert (
        "copied sources and the proposal baseline remain unchanged"
        in correction
    )
    assert (
        "Require a fresh independent `plan-audit` of the corrected plan "
        "and the "
        "same baseline"
    ) in correction

    assert '--state-file "$PLAN_DIR/tasks.json"' in correction_scripts
    assert "--auto-fix" not in correction_scripts
    assert "--schema" in correction_scripts
    assert '--input "$PLAN_DIR/tasks.json"' in correction_scripts
    assert '--output "$PLAN_DIR/tasks.md"' in correction_scripts
    assert "--overwrite" in correction_scripts
    assert (
        "Correction does not invoke `init-task-packet` or create a new plan "
        "workspace."
    ) in correction_scripts


def test_documented_state_file_validator_form_executes(tmp_path: Path) -> None:
    """Verify the documented state-file validator command succeeds."""
    packet = {
        "summary": "validator command fixture",
        "slug": "validator-command-fixture",
        "tasks": [
            {
                "taskId": "validator-command",
                "purpose": "Validate one task packet.",
                "context": (
                    "This fixture provides enough concrete context to satisfy "
                    "the shared task schema while exercising the documented "
                    "plan-writer "
                    "validator command without mutating repository files. "
                )
                * 2,
                "filesToRead": [],
                "filesToWrite": [],
                "skills": ["generic-analysis"],
                "executionInstructions": [
                    {"step": 1, "action": "Validate the packet."}
                ],
                "verification": ["The documented validator command succeeds."],
                "expectedOutput": "One validated task packet.",
                "verificationCoverage": {
                    "observable": ["The validator exits successfully."]
                },
                "dependencies": [],
                "antiPatternSignals": ["none"],
                "purposeOutputAlignment": {
                    "status": "aligned",
                    "evidence": "The validated packet is the requested result.",
                },
            }
        ],
        "boundaryReview": {
            "requestResultInventory": {
                "validated-packet": {
                    "result": "One validated task packet.",
                    "kind": "immediate",
                    "disposition": "represented-by-task",
                }
            },
            "taskReviews": {
                "validator-command": {
                    "immediateResult": "One validated task packet.",
                    "predecessorOutputs": [],
                    "preAssignmentDisposition": "single-result",
                    "acceptanceDisposition": "accepted",
                }
            },
            "warningDispositions": {},
        },
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


def test_active_callers_lifecycle_mappings_and_fixtures_use_new_identity() -> (
    None
):
    """Verify callers, lifecycle references, and fixtures use plan-writer."""
    plan_command = _text("commands/plan.md")
    assert "Load the `plan-writer` skill." in plan_command
    assert "Load the `plan` skill." not in plan_command
    assert (
        "Authorize planning only when either the proposal records an "
        "accepted lifecycle state"
    ) in plan_command
    assert "decision-ready" in plan_command
    assert "recorded decision authority" in plan_command
    assert "Do not infer acceptance" in plan_command
    assert "For findings with plan-writer-owned remediation" in plan_command
    assert "the existing plan workspace" in plan_command
    assert (
        "After each correction, perform a mandatory fresh read-only "
        "`plan-audit`"
        in plan_command
    )

    automation_command = _text("commands/leeroy-jenkins.md")
    assert "Load the `plan-writer` skill and create a new plan workspace" in (
        automation_command
    )
    assert "Stop after proposal creation unless" in automation_command
    assert "Initial automation consent is not proposal acceptance" in (
        automation_command
    )
    assert "recorded decision authority" in automation_command
    assert "For findings with plan-writer-owned remediation" in (
        automation_command
    )
    assert (
        "After each correction, perform a mandatory fresh read-only "
        "`plan-audit`"
        in automation_command
    )
    planner = " ".join(_text("agents/planner.md").split())
    assert (
        "`plan-writer` - Create copied-source task-plan workspaces and make "
        "bounded corrections to an existing plan workspace."
    ) in planner
    assert (
        "to make only bounded corrections in the same existing plan workspace"
        in planner
    )
    assert "Require a fresh independent `plan-audit`" in planner
    index = _text("skills/README.md")
    assert (
        "[`plan-writer`][plan-writing] — create executable plan workspaces."
        in index
    )
    assert "[plan-writing]: ./plan-writer/SKILL.md" in index
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


def test_migrated_reference_map_resolves_current_contracts() -> None:
    """Verify the migrated reference map resolves every current contract."""
    reference = TARGET / "reference"
    index = (reference / "README.md").read_text(encoding="utf-8")
    for relative in (
        "workspace-contract.md",
        "task-authoring.md",
        "scripts.md",
    ):
        assert f"](./{relative})" in index
        assert (reference / relative).resolve().is_file()
    assert "Load the `task-contract` documentation skill" in index
