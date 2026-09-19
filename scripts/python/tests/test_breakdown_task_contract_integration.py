"""Focused integration checks for breakdown-tasks/task-contract ownership."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from lib.boundary_review_acceptance.core import accept_boundary_review
from lib.schema import load_schema
from lib.validate_task_structure.core import validate_root

ROOT = Path(__file__).resolve().parents[3]
BREAKDOWN = ROOT / "skills" / "breakdown-tasks"
WORKFLOW = BREAKDOWN / "SKILL.md"
TASK_CONTRACT = ROOT / "skills" / "task-contract" / "SKILL.md"
SCHEMA = BREAKDOWN / "schema" / "task-packet.schema.json"


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
    draft = text.index("Draft tasks without `skills`")
    assert load < draft
    assert "exact collector winner" in text
    assert "passive, non-transitive" in text
    assert "adds no authority" in text


def test_operation_owned_pipeline_remains_and_cli_paths_are_stable() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    normalized_text = " ".join(text.split()).lower()

    for phrase in (
        "normalize",
        "inventory every discovery",
        "then split it again if it still",
        "Draft tasks without `skills`",
        "Assign skills only after boundary acceptance",
        "Inspect contracts",
        "Publish the candidate packet",
        "Validate structure and close final request-aware acceptance",
    ):
        assert phrase.lower() in normalized_text

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
    assert 'mktemp "${TMPDIR:-/tmp}/opencode-breakdown.XXXXXX.json"' in text
    assert '< "$DRAFT_PATH"' in text
    assert 'rm -f -- "$DRAFT_PATH"' in text
    assert text.index("init-task-packet") < text.index('rm -f -- "$DRAFT_PATH"')
    assert "|| status=$?" in text
    assert 'exit "${status:-0}"' in text
    assert "/tmp/breakdown-draft.json" not in text


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


def test_decomposition_method_aggressively_splits_then_connects_results() -> None:
    method = (
        BREAKDOWN / "reference" / "authoring" / "decomposition-method.md"
    ).read_text(encoding="utf-8")
    examples = (
        BREAKDOWN / "reference" / "authoring" / "decomposition-examples.md"
    ).read_text(encoding="utf-8")
    normalized_method = " ".join(method.split())
    normalized_examples = " ".join(examples.split())

    for phrase in (
        "Name the requested outcome",
        "Create the request-result inventory",
        "Make and record the fixed-predecessor split decision",
        "Connect the results",
        "Draft and close the pre-assignment boundary review",
        "Stop splitting only",
    ):
        assert phrase in method

    assert "predecessor outputs held fixed" in method
    assert "Do not add `skills` yet" in method
    assert (
        "When there is a reasonable argument for another boundary, create it"
        in normalized_method
    )
    assert "Research That Determines Later Work" in examples
    assert "Known-Source Lookup Inside One Task" in examples
    assert "session evidence" in examples
    assert "Create a separate verification task" in normalized_examples


def test_atomicity_contract_prefers_splitting_over_compound_work() -> None:
    atomicity = (
        ROOT / "skills" / "task-contract" / "reference" / "atomicity-and-alignment.md"
    ).read_text(encoding="utf-8")
    normalized_atomicity = " ".join(atomicity.split()).lower()

    for phrase in (
        "when a boundary is uncertain, split it",
        "A false split is preferable to hidden compound work",
        "Distinct lifecycle stages are separate tasks by default",
        "default to separate tasks for",
        "Verification is a separate task by default",
        "Do not stop merely because further splitting feels fine-grained",
    ):
        assert phrase.lower() in normalized_atomicity

    assert "Research may remain internal" not in atomicity


def _task(task_id: str, result: str) -> dict[str, object]:
    return {
        "taskId": task_id,
        "purpose": result,
        "context": "Request-plus-packet regression fixture.",
        "filesToRead": [],
        "filesToWrite": [],
        "skills": ["generic-analysis"],
        "executionInstructions": [{"step": 1, "action": result}],
        "expectedOutput": result,
        "verificationCoverage": {
            "observable": ["Fixture assertion."],
            "coverage": "complete",
        },
        "dependencies": [],
        "antiPatternSignals": ["none"],
        "purposeOutputAlignment": {"status": "aligned", "evidence": result},
    }


def _reviewed_packet(
    request: str,
    task_results: list[tuple[str, str]],
    *,
    warning_dispositions: dict[str, dict[str, str]] | None = None,
    indivisible_task_id: str | None = None,
) -> dict[str, object]:
    task_reviews: dict[str, dict[str, object]] = {}
    for task_id, result in task_results:
        task_reviews[task_id] = {
            "immediateResult": result,
            "predecessorOutputs": [],
            "preAssignmentDisposition": "single-result",
            "acceptanceDisposition": "accepted",
        }
    if indivisible_task_id:
        task_reviews[indivisible_task_id] = {
            "immediateResult": task_reviews[indivisible_task_id]["immediateResult"],
            "predecessorOutputs": [],
            "preAssignmentDisposition": "retained-indivisible",
            "acceptanceDisposition": "accepted-indivisible",
            "indivisibilityEvidence": {
                "sharedResult": "One valid source-schema/generated-client state.",
                "verificationBoundary": "Generated client matches the source schema.",
                "separationHarm": "Separating them leaves the repository inconsistent.",
            },
        }
    return {
        "summary": request,
        "slug": "boundary-review-regression",
        "tasks": [_task(task_id, result) for task_id, result in task_results],
        "boundaryReview": {
            "requestResultInventory": {
                task_id: {
                    "result": result,
                    "kind": "immediate",
                    "disposition": "represented-by-task",
                }
                for task_id, result in task_results
            },
            "taskReviews": task_reviews,
            "warningDispositions": warning_dispositions or {},
        },
    }


@pytest.mark.parametrize(
    "user_request,task_results,warnings,indivisible_task_id",
    [
        (
            "Analyze the lifecycle and implement the resulting change.",
            [
                ("analyze", "Lifecycle analysis."),
                ("implement", "Implementation change."),
            ],
            {
                "lifecycle": {
                    "signal": "lifecycle-stage-bundle",
                    "disposition": "split",
                }
            },
            None,
        ),
        (
            "Analyze the risk and write a proposal from that analysis.",
            [("analysis", "Risk analysis."), ("proposal", "Proposal.")],
            {
                "analysis-proposal": {
                    "signal": "analysis-plus-planning",
                    "disposition": "split",
                }
            },
            None,
        ),
        (
            (
                "Implement checkout and publish an independently executable "
                "verification report."
            ),
            [
                ("implementation", "Checkout implementation."),
                ("verification", "Verification report."),
            ],
            {
                "verification": {
                    "signal": "implementation-plus-independent-verification",
                    "disposition": "split",
                }
            },
            None,
        ),
        (
            "Implement checkout and run its ordinary regression tests.",
            [("implementation", "Verified checkout implementation.")],
            {
                "ordinary-verification": {
                    "signal": "implementation-plus-tests",
                    "disposition": "not-applicable",
                }
            },
            None,
        ),
        (
            (
                "Change the source schema and regenerate its client as one "
                "required repository state."
            ),
            [("schema-client", "Source schema and generated client state.")],
            {
                "schema-client": {
                    "signal": "coupling-rationale",
                    "taskId": "schema-client",
                    "disposition": "accepted-indivisible",
                }
            },
            "schema-client",
        ),
    ],
)
def test_request_packet_regressions_keep_structural_and_semantic_evidence_separate(
    user_request: str,
    task_results: list[tuple[str, str]],
    warnings: dict[str, dict[str, str]],
    indivisible_task_id: str | None,
) -> None:
    """Schema conformance records evidence; delegator review decides semantics."""
    packet = _reviewed_packet(
        user_request,
        task_results,
        warning_dispositions=warnings,
        indivisible_task_id=indivisible_task_id,
    )

    valid, diagnostics = validate_root(packet, load_schema(SCHEMA))

    assert valid is True
    assert diagnostics == []
    assert packet["summary"] == user_request


def _review_evidence(
    request: str, packet: dict[str, object], *, deficiencies: list[str] | None = None
) -> dict[str, object]:
    tasks = packet["tasks"]
    assert isinstance(tasks, list)
    return {
        "reviewedRequest": request,
        "packetSlug": packet["slug"],
        "reviewedTaskIds": [task["taskId"] for task in tasks],
        "disposition": "accepted",
        "rationale": "The supervisory review substantiates the recorded boundary.",
        "deficiencies": deficiencies or [],
    }


@pytest.mark.parametrize(
    "original_request,packet,evidence,expected_diagnostic",
    [
        pytest.param(
            "Implement checkout.",
            _reviewed_packet(
                "Implement checkout.", [("implementation", "Checkout.")]
            ),
            None,
            "explicit review evidence must be an object",
            id="absent-review-evidence",
        ),
        pytest.param(
            "Implement checkout.",
            _reviewed_packet(
                "Implement checkout.", [("implementation", "Checkout.")]
            ),
            {"reviewedRequest": "Implement checkout."},
            "review evidence must cover each final packet taskId exactly once",
            id="incomplete-review-evidence",
        ),
        pytest.param(
            "Implement checkout.",
            _reviewed_packet(
                "Implement checkout.", [("implementation", "Checkout.")]
            ),
            _review_evidence(
                "Implement checkout.",
                _reviewed_packet(
                    "Implement checkout.", [("implementation", "Checkout.")]
                ),
                deficiencies=["The warning disposition remains unresolved."],
            ),
            "review evidence identifies unresolved deficiencies",
            id="unresolved-review-evidence",
        ),
        pytest.param(
            "Implement checkout.",
            _reviewed_packet(
                "Implement checkout.", [("implementation", "Checkout.")]
            ),
            {
                **_review_evidence(
                    "Implement checkout.",
                    _reviewed_packet(
                        "Implement checkout.", [("implementation", "Checkout.")]
                    ),
                ),
                "rationale": "",
            },
            "review evidence must include a non-empty rationale",
            id="unsubstantiated-review-evidence",
        ),
        pytest.param(
            "Analyze the lifecycle and implement the resulting change.",
            _reviewed_packet(
                "Analyze the lifecycle and implement the resulting change.",
                [("implementation", "Implementation change.")],
            ),
            _review_evidence(
                "Analyze the lifecycle and implement the resulting change.",
                _reviewed_packet(
                    "Analyze the lifecycle and implement the resulting change.",
                    [("implementation", "Implementation change.")],
                ),
                deficiencies=["The lifecycle analysis is missing from the inventory."],
            ),
            "review evidence identifies unresolved deficiencies",
            id="missing-inventory-coverage",
        ),
        pytest.param(
            "Change the source schema and regenerate its client.",
            _reviewed_packet(
                "Change the source schema and regenerate its client.",
                [("schema-client", "Source schema and generated client.")],
                indivisible_task_id="schema-client",
            ),
            _review_evidence(
                "Change the source schema and regenerate its client.",
                _reviewed_packet(
                    "Change the source schema and regenerate its client.",
                    [("schema-client", "Source schema and generated client.")],
                    indivisible_task_id="schema-client",
                ),
                deficiencies=["The claimed coupling has no request-aware support."],
            ),
            "review evidence identifies unresolved deficiencies",
            id="unsupported-coupling",
        ),
        pytest.param(
            "Analyze the lifecycle and implement the resulting change.",
            _reviewed_packet(
                "Analyze the lifecycle and implement the resulting change.",
                [("lifecycle", "Lifecycle analysis and implementation.")],
            ),
            _review_evidence(
                "Analyze the lifecycle and implement the resulting change.",
                _reviewed_packet(
                    "Analyze the lifecycle and implement the resulting change.",
                    [("lifecycle", "Lifecycle analysis and implementation.")],
                ),
                deficiencies=[
                    "Analysis and implementation are independently acceptable results."
                ],
            ),
            "review evidence identifies unresolved deficiencies",
            id="independently-acceptable-lifecycle-work",
        ),
    ],
)
def test_downstream_eligibility_rejects_unaccepted_request_packet_reviews(
    original_request: str,
    packet: dict[str, object],
    evidence: object,
    expected_diagnostic: str,
) -> None:
    """Structural validity is necessary, never a request-aware acceptance oracle."""
    schema = load_schema(SCHEMA)
    structural_valid, structural_diagnostics = validate_root(packet, schema)

    assert structural_valid is True
    assert structural_diagnostics == []
    accepted, diagnostics = accept_boundary_review(
        original_request, packet, evidence, schema
    )

    assert accepted is False
    assert expected_diagnostic in diagnostics


def test_downstream_eligibility_accepts_only_documented_indivisible_fixture() -> None:
    """A concrete shared repository state remains the narrow retained exception."""
    request = (
        "Change the source schema and regenerate its client as one required "
        "repository state."
    )
    packet = _reviewed_packet(
        request,
        [("schema-client", "Source schema and generated client state.")],
        warning_dispositions={
            "schema-client": {
                "signal": "coupling-rationale",
                "taskId": "schema-client",
                "disposition": "accepted-indivisible",
            }
        },
        indivisible_task_id="schema-client",
    )
    schema = load_schema(SCHEMA)
    evidence = _review_evidence(request, packet)

    structural_valid, structural_diagnostics = validate_root(packet, schema)
    accepted, diagnostics = accept_boundary_review(request, packet, evidence, schema)

    assert structural_valid is True
    assert structural_diagnostics == []
    assert accepted is True
    assert diagnostics == []


def test_downstream_eligibility_rejects_invalid_request_binding_and_structure() -> None:
    """Eligibility binds the original request and requires the canonical root."""
    request = "Implement checkout."
    packet = _reviewed_packet(request, [("implementation", "Checkout.")])
    schema = load_schema(SCHEMA)
    evidence = _review_evidence(request, packet)

    accepted, diagnostics = accept_boundary_review("", packet, evidence, schema)

    assert accepted is False
    assert "original request must be a non-empty string" in diagnostics
    assert "review evidence must bind the unchanged original request" in diagnostics

    packet.pop("boundaryReview")
    accepted, diagnostics = accept_boundary_review(request, packet, evidence, schema)

    assert accepted is False
    assert diagnostics[0] == "canonical packet failed structural validation"
