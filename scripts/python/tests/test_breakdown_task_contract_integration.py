"""Focused integration checks for breakdown-tasks/task-contract ownership."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BREAKDOWN = ROOT / "skills" / "breakdown-tasks"
WORKFLOW = BREAKDOWN / "SKILL.md"
TASK_CONTRACT = ROOT / "skills" / "task-contract" / "SKILL.md"


def _collector_records() -> list[dict[str, object]]:
    result = subprocess.run(
        [
            "uv",
            "run",
            "--project",
            str(ROOT / "scripts" / "python"),
            "collect-skills",
            "--class",
            "operation",
            "--class",
            "documentation",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    records = json.loads(result.stdout)
    assert isinstance(records, list)
    return records


def test_task_contract_is_collector_winning_passive_context_before_drafting() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    records = _collector_records()
    matches = [record for record in records if record.get("name") == "task-contract"]

    assert len(matches) == 1
    record = matches[0]
    assert record["class"] == "documentation"
    assert Path(str(record["path"])).resolve() == TASK_CONTRACT.resolve()
    assert record["path"].endswith("skills/task-contract/SKILL.md")

    load = text.index("Load the shared task contract before authoring boundaries")
    draft = text.index("Draft atomic tasks")
    assert load < draft
    assert "exact winning record" in text
    assert "passive, documentation-only, and non-transitive" in text
    assert "add no authority" in text


def test_operation_owned_pipeline_remains_and_cli_paths_are_stable() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    for phrase in (
        "normalize",
        "Inventory every question",
        "Draft atomic tasks",
        "Assign skills to each task",
        "Inspect contracts",
        "Publish for dispatch",
        "Validate and fix",
    ):
        assert phrase.lower() in text.lower()

    for command in (
        "collect-skills --class planning",
        "--class operation",
        "--class documentation",
        "init-task-packet",
        "validate-task-structure",
    ):
        assert command in text

    assert (BREAKDOWN / "schema" / "task-input.schema.json").is_file()
    assert (BREAKDOWN / "schema" / "task-packet.schema.json").is_file()
    assert "--output-dir .tasks" in text
    assert 'schema=~/.config/opencode/skills/breakdown-tasks/schema' in text


def test_local_authoring_docs_point_to_shared_invariant_owners() -> None:
    core = (BREAKDOWN / "reference" / "authoring" / "core-rules.md").read_text(
        encoding="utf-8"
    )
    granularity = (
        BREAKDOWN / "reference" / "authoring" / "task-granularity.md"
    ).read_text(encoding="utf-8")
    fields = (
        BREAKDOWN / "reference" / "authoring" / "field-reference-table.md"
    ).read_text(encoding="utf-8")
    context = (
        BREAKDOWN / "reference" / "authoring" / "context-preservation.md"
    ).read_text(encoding="utf-8")
    validation = (
        BREAKDOWN / "reference" / "orchestration" / "task-validation.md"
    ).read_text(encoding="utf-8")

    assert "task-contract" in core
    assert "atomicity-and-alignment.md" in core
    assert "dependencies-and-coupling.md" in core
    assert "traceability-and-metadata.md" in core
    assert "atomicity-and-alignment.md" in granularity
    assert "dependencies-and-coupling.md" in granularity
    assert "task-contract" in fields
    assert "traceability-and-metadata.md" in context
    assert "task-contract" in validation

    assert "Create separate tasks when either concern can be" not in core
    assert "They produce one shared result." not in core
    assert "A dependency explains order; it does not" not in core
    assert "Metadata records the author's boundary decision." not in fields


def test_passive_documentation_is_not_an_executable_assignment() -> None:
    assignment = (
        BREAKDOWN / "reference" / "skill-assignment.md"
    ).read_text(encoding="utf-8")
    contract = TASK_CONTRACT.read_text(encoding="utf-8")

    assert "context only, not an executable assignment" in assignment
    assert "passive, documentation-only, non-transitive" in assignment
    assert "class: documentation" in contract
    assert "non-transitive" in contract
    assert "does not own decomposition" in contract
    assert "does not auto-read" in contract
