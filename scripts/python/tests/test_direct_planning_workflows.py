"""Contract checks for the shared procedural workflow semantics."""

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

ROOT = Path(__file__).parents[3]
BREAKDOWN = ROOT / "skills/breakdown-tasks/SKILL.md"
PLAN = ROOT / "skills/plan-writer/SKILL.md"


def _execution_section(workflow: str) -> str:
    """Return the producer's execution section without unrelated references."""
    match = re.search(
        r"(?ms)^## Execution\s*\n(?P<section>.*?)(?=^## [^\n]+|\Z)",
        workflow,
    )
    assert match is not None
    return match.group("section")


def _collector_calls(execution: str) -> list[tuple[tuple[str, ...], int]]:
    """Return class filters and positions from workflow code blocks."""
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
    return calls


def _assert_three_stage_workflow(workflow: str) -> None:
    """Check one ordered, distinct collection sequence before assignment."""
    execution = _execution_section(workflow)
    calls = _collector_calls(execution)
    assert [classes for classes, _ in calls] == [
        ("planning",),
        ("operation",),
        ("documentation",),
    ]

    lowered = workflow.lower()
    execution_lowered = execution.lower()
    execution_compact = " ".join(execution_lowered.split())
    assert "once per request" in lowered
    assert re.search(
        r"do not recollect for each task|no per-task recollection", lowered
    )
    assert re.search(
        r"\b(?:keep|use)\b.{0,120}\bresults? distinct\b",
        execution_compact,
    )

    task_contract_load = re.search(
        r"load the shared task contract before authoring", execution_lowered
    )
    assignment = re.search(
        r"\bassign skills(?: only)? after boundary acceptance\b",
        execution_lowered,
    )
    assert task_contract_load is not None
    assert assignment is not None
    assert calls[-1][1] < task_contract_load.start() < assignment.start()


def _assert_affirmative_documentation_policy(text: str) -> None:
    """Check material-value criteria, contrasting examples, and safeguards."""
    lowered = " ".join(text.lower().split())
    assert "actively consider whether a documentation profile" in lowered
    assert "distinct, material execution value" in lowered
    assert "beyond" in lowered and "context" in lowered
    assert "listed materials" in lowered
    assert re.search(r"clarif(?:y|ies) a relevant contract", lowered)
    assert re.search(r"resolv(?:e|es) a task-specific semantic", lowered)
    assert re.search(r"help(?:s)? prevent a likely execution error", lowered)

    assert "customize-opencode" in lowered
    assert "packet" in lowered and "envelope" in lowered
    assert re.search(r"\bwhen\b.{0,180}\baffect\b", lowered)
    assert re.search(
        r"\bomit\b.{0,100}"
        r"\b(?:unrelated|already (?:covered|supplied|provided))\b",
        lowered,
    )
    assert re.search(r"\bzero documentation assignments? is valid\b", lowered)
    assert re.search(r"\b(?:no more than two|maximum remains two)\b", lowered)

    assert re.search(r"\bdo not impose\b[^.]{0,120}\bquota\b", lowered)
    assert re.search(r"\bdo not impose\b[^.]{0,120}\btarget\b", lowered)
    assert re.search(r"\bdo not\b[^.]{0,180}\bscore\b", lowered)
    assert re.search(r"\bdo not\b[^.]{0,180}\brejection log\b", lowered)


def test_both_workflows_share_three_stage_and_assignment_contract() -> None:
    """Verify collection and task-specific assignment for both producers."""
    breakdown = BREAKDOWN.read_text(encoding="utf-8")
    plan = PLAN.read_text(encoding="utf-8")
    assignment_reference = (
        ROOT / "skills/breakdown-tasks/reference/skill-assignment.md"
    ).read_text(encoding="utf-8")
    assert "(reference/skill-assignment.md)" in breakdown

    for text in (breakdown, plan):
        lowered = " ".join(text.lower().split())
        _assert_three_stage_workflow(text)
        assert "collect-skills --class planning" in text
        assert "--class operation" in text
        assert "--class documentation" in text
        assert "exactly one `class: operation` execution owner" in lowered
        assert re.search(
            r"zero to two (?:materially relevant )?"
            r"(?:`class: documentation` )?skills|"
            r"zero to two documentation skills",
            lowered,
        )
        assert "never score" in lowered or "do not score" in lowered
        assert "init-task-packet" in text
        assert "packet slug" in lowered
        assert "never derive" in lowered

    _assert_affirmative_documentation_policy(assignment_reference)
    _assert_affirmative_documentation_policy(plan)


def test_breakdown_prohibits_obsolete_selection_patterns() -> None:
    """Verify breakdown-tasks prohibits obsolete selection patterns."""
    text = BREAKDOWN.read_text(encoding="utf-8").lower()
    assert "do not score" in text
    assert "do not recollect" in text
    assert "do not manually populate" in text


def test_plan_preserves_sources_and_fail_closed_publication() -> None:
    """Verify plan-writer preserves sources and fails closed on publication."""
    text = PLAN.read_text(encoding="utf-8").lower()
    assert "never modify source documents" in text
    assert "fail closed" in text
    assert "tasks.md" in text
    assert "validate-task-structure" in text


def test_dispatch_and_display_require_a_canonical_slug_without_derivation() -> (
    None
):
    """Verify dispatch and display preserve the selected slug unchanged."""
    dispatch = (ROOT / "skills/dispatch-decompose/SKILL.md").read_text(
        encoding="utf-8"
    )
    display = (ROOT / "skills/display-tasks/SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "select a packet slug" in dispatch
    assert "preserve it unchanged" in dispatch
    assert "including its author-selected packet slug" in display
    assert "Do not restate or\nlocally validate slug grammar" in display


def test_display_tasks_preserves_required_table_exception_contract() -> None:
    """Verify display-tasks retains the required Markdown table contract."""
    display = (ROOT / "skills/display-tasks/SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "A single Markdown table with no surrounding commentary." in display
    assert (
        "```markdown\n"
        "| Purpose | Starting files | Suggested outputs | Skills |\n"
        "| ------- | -------------- | ----------------- | ------ |\n"
        "```"
    ) in display
