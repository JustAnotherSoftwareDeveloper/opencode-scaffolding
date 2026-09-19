"""Structural regressions for the canonical task-packet validator boundary."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.validate_task_structure import main
from lib.schema import load_schema
from lib.validate_task_structure import (
    _validate_execution_steps,
    _validate_file_array,
    auto_fix,
    auto_fix_task_structure,
    validate,
)
from lib.validate_task_structure.core import validate_root

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "skills"
    / "breakdown-tasks"
    / "schema"
    / "task-packet.schema.json"
)


@pytest.fixture(scope="module")
def schema() -> dict:
    return load_schema(SCHEMA_PATH)


@pytest.fixture
def canonical_packet() -> dict:
    """One schema-valid root; its prose is not an atomicity assertion."""
    return {
        "summary": "Validate the task-packet structural interface.",
        "slug": "validator-boundary-regression",
        "tasks": [
            {
                "taskId": "validator-tests",
                "purpose": "Add validator regression coverage.",
                "context": "Exercise only the canonical structural interface.",
                "filesToRead": [
                    "scripts/python/src/lib/validate_task_structure/core.py"
                ],
                "filesToWrite": [
                    "scripts/python/tests/test_validate_task_structure.py"
                ],
                "skills": ["skill-script-python-test-writer"],
                "executionInstructions": [{"step": 1, "action": "Run focused tests."}],
                "verification": ["Focused validator tests pass."],
                "expectedOutput": "Focused validator regression tests.",
                "verificationCoverage": {"observable": ["pytest result"]},
                "dependencies": [],
                "antiPatternSignals": ["none"],
                "purposeOutputAlignment": {
                    "status": "aligned",
                    "evidence": "The output is the requested regression coverage.",
                },
            }
        ],
        "boundaryReview": {
            "requestResultInventory": {
                "validator-coverage": {
                    "result": "Focused structural validator coverage.",
                    "kind": "immediate",
                    "disposition": "represented-by-task",
                }
            },
            "taskReviews": {
                "validator-tests": {
                    "immediateResult": "Focused structural validator coverage.",
                    "predecessorOutputs": [],
                    "preAssignmentDisposition": "single-result",
                    "acceptanceDisposition": "accepted",
                }
            },
            "warningDispositions": {},
        },
    }


def _result(runner_result) -> dict:
    assert runner_result.output, runner_result.exception
    return json.loads(runner_result.output)


def _invalid_roots(packet: dict) -> dict[str, dict]:
    absent = deepcopy(packet)
    absent.pop("boundaryReview")

    malformed = deepcopy(packet)
    malformed["boundaryReview"] = {}

    unresolved = deepcopy(packet)
    unresolved["boundaryReview"]["warningDispositions"] = {
        "unclosed-warning": {"signal": "review-signal", "disposition": "unresolved"}
    }

    contradictory = deepcopy(packet)
    contradictory["boundaryReview"]["warningDispositions"] = {
        "indivisible-warning": {
            "signal": "review-signal",
            "taskId": "validator-tests",
            "disposition": "accepted-indivisible",
        }
    }

    legacy = deepcopy(packet)
    legacy["tasks"][0].pop("taskId")

    return {
        "rootless": deepcopy(packet["tasks"]),
        "absent-review": absent,
        "malformed-review": malformed,
        "unresolved-warning": unresolved,
        "contradictory-review": contradictory,
        "legacy-shaped": legacy,
    }


class TestCanonicalValidatorApi:
    """Every exported validator consumer requires a canonical root."""

    def test_validate_accepts_a_canonical_root(self, canonical_packet, schema) -> None:
        valid, diagnostics = validate(canonical_packet, schema)
        assert valid is True
        assert diagnostics == []

    @pytest.mark.parametrize(
        "case",
        [
            "rootless",
            "absent-review",
            "malformed-review",
            "unresolved-warning",
            "contradictory-review",
            "legacy-shaped",
        ],
    )
    def test_exported_validate_rejects_closed_review_invalid_inputs(
        self, canonical_packet, schema, case
    ) -> None:
        valid, diagnostics = validate(_invalid_roots(canonical_packet)[case], schema)
        assert valid is False
        assert diagnostics

    @pytest.mark.parametrize(
        "case",
        [
            "rootless",
            "absent-review",
            "malformed-review",
            "unresolved-warning",
            "contradictory-review",
            "legacy-shaped",
        ],
    )
    def test_validate_root_rejects_closed_review_invalid_inputs(
        self, canonical_packet, schema, case
    ) -> None:
        valid, diagnostics = validate_root(
            _invalid_roots(canonical_packet)[case], schema
        )
        assert valid is False
        assert diagnostics

    @pytest.mark.parametrize("disposition", ["split", "not-applicable"])
    def test_closed_non_indivisible_warning_dispositions_are_structurally_valid(
        self, canonical_packet, schema, disposition
    ) -> None:
        packet = deepcopy(canonical_packet)
        packet["boundaryReview"]["warningDispositions"] = {
            "structural-signal": {
                "signal": "potential-boundary-signal",
                "disposition": disposition,
            }
        }
        valid, diagnostics = validate(packet, schema)
        assert valid is True
        assert diagnostics == []

    def test_accepted_indivisible_warning_requires_matching_review(
        self, canonical_packet, schema
    ) -> None:
        packet = deepcopy(canonical_packet)
        review = packet["boundaryReview"]["taskReviews"]["validator-tests"]
        review.update(
            {
                "preAssignmentDisposition": "retained-indivisible",
                "acceptanceDisposition": "accepted-indivisible",
                "indivisibilityEvidence": {
                    "sharedResult": "One structural interface fixture.",
                    "verificationBoundary": "One focused test module.",
                    "separationHarm": "Separating it would duplicate the fixture.",
                },
            }
        )
        packet["boundaryReview"]["warningDispositions"] = {
            "indivisible-signal": {
                "signal": "potential-boundary-signal",
                "taskId": "validator-tests",
                "disposition": "accepted-indivisible",
            }
        }
        valid, diagnostics = validate(packet, schema)
        assert valid is True
        assert diagnostics == []


class TestCanonicalValidatorCli:
    """File, stdin, and state-file entry modes all retain the root gate."""

    @pytest.mark.parametrize("mode", ["file", "stdin", "state-file"])
    def test_cli_accepts_canonical_roots(
        self, canonical_packet, tmp_path: Path, mode
    ) -> None:
        runner = CliRunner()
        input_file = tmp_path / "packet.json"
        input_file.write_text(json.dumps(canonical_packet), encoding="utf-8")
        arguments = ["--schema", str(SCHEMA_PATH)]
        if mode == "file":
            result = runner.invoke(main, [str(input_file), *arguments])
        elif mode == "stdin":
            result = runner.invoke(
                main, ["--stdin", *arguments], input=input_file.read_text()
            )
        else:
            result = runner.invoke(main, ["--state-file", str(input_file), *arguments])
        assert result.exit_code == 0, result.output
        assert _result(result) == {"valid": True}

    @pytest.mark.parametrize("mode", ["file", "stdin", "state-file"])
    @pytest.mark.parametrize(
        "case",
        [
            "rootless",
            "absent-review",
            "malformed-review",
            "unresolved-warning",
            "contradictory-review",
            "legacy-shaped",
        ],
    )
    def test_cli_modes_reject_rootless_and_closed_review_invalid_inputs(
        self, canonical_packet, tmp_path: Path, mode, case
    ) -> None:
        runner = CliRunner()
        input_file = tmp_path / "invalid.json"
        input_file.write_text(
            json.dumps(_invalid_roots(canonical_packet)[case]), encoding="utf-8"
        )
        arguments = ["--schema", str(SCHEMA_PATH)]
        if mode == "file":
            result = runner.invoke(main, [str(input_file), *arguments])
        elif mode == "stdin":
            result = runner.invoke(
                main, ["--stdin", *arguments], input=input_file.read_text()
            )
        else:
            result = runner.invoke(main, ["--state-file", str(input_file), *arguments])
        assert result.exit_code == 1, result.output
        payload = _result(result)
        assert payload["valid"] is False
        assert payload["errors"]

    def test_state_file_auto_fix_does_not_write_an_absent_review(
        self, canonical_packet, tmp_path: Path
    ) -> None:
        packet = deepcopy(canonical_packet)
        packet.pop("boundaryReview")
        state_file = tmp_path / "missing-review.json"
        original = json.dumps(packet)
        state_file.write_text(original, encoding="utf-8")

        result = CliRunner().invoke(
            main,
            [
                "--state-file",
                str(state_file),
                "--auto-fix",
                "--schema",
                str(SCHEMA_PATH),
            ],
        )

        assert result.exit_code == 1, result.output
        assert _result(result)["valid"] is False
        assert state_file.read_text(encoding="utf-8") == original


def test_auto_fix_api_rejects_rootless_input_before_writing(
    schema, tmp_path: Path
) -> None:
    state_file = tmp_path / "rootless.json"
    original = json.dumps([])
    state_file.write_text(original, encoding="utf-8")

    result = auto_fix_task_structure(state_file, schema)

    assert result["valid"] is False
    assert state_file.read_text(encoding="utf-8") == original


def test_structural_helpers_and_auto_fix_cover_normalization(canonical_packet) -> None:
    assert _validate_execution_steps([{"step": 2, "action": "wrong"}], "tasks[0]")
    errors = _validate_file_array(
        [42, "", "same.py", "same.py", "${placeholder}"], "tasks[0]", "filesToRead"
    )
    assert len(errors) == 4
    skills = canonical_packet["tasks"][0]["skills"]
    skills[:] = ["python", "", "python", "testing", "linting", "extra"]
    assert auto_fix(canonical_packet["tasks"]) is True
    assert skills != canonical_packet["tasks"][0]["skills"]


def test_auto_fix_api_persists_only_a_repaired_canonical_root(
    canonical_packet, schema, tmp_path: Path
) -> None:
    canonical_packet["tasks"][0]["skills"] = ["python", "python", "testing", "linting"]
    state_file = tmp_path / "repairable.json"
    state_file.write_text(json.dumps(canonical_packet), encoding="utf-8")

    result = auto_fix_task_structure(state_file, schema)

    assert result == {"valid": True, "fixed": True}
    assert json.loads(state_file.read_text())["tasks"][0]["skills"] == [
        "python",
        "testing",
        "linting",
    ]


def test_metadata_reference_and_write_errors_are_structural(
    canonical_packet, schema
) -> None:
    packet = deepcopy(canonical_packet)
    task = packet["tasks"][0]
    task["dependencies"] = [{"taskId": "unknown"}]
    valid, diagnostics = validate(packet, schema)
    assert valid is False
    assert any("dependency-reference" in item for item in diagnostics)


def test_metadata_cycle_and_shared_write_rules_are_structural(
    canonical_packet, schema
) -> None:
    packet = deepcopy(canonical_packet)
    second = deepcopy(packet["tasks"][0])
    second["taskId"] = "second-task"
    second["dependencies"] = []
    packet["tasks"][0]["dependencies"] = []
    packet["tasks"].append(second)
    packet["boundaryReview"]["taskReviews"]["second-task"] = {
        "immediateResult": "A second structural fixture.",
        "predecessorOutputs": [],
        "preAssignmentDisposition": "single-result",
        "acceptanceDisposition": "accepted",
    }
    valid, diagnostics = validate(packet, schema)
    assert valid is False
    assert any("write-target-conflict" in item for item in diagnostics)

    packet["tasks"][0]["dependencies"] = [{"taskId": "second-task"}]
    second["dependencies"] = [{"taskId": "validator-tests"}]
    valid, diagnostics = validate(packet, schema)
    assert valid is False
    assert any("dependency-cycle" in item for item in diagnostics)


@pytest.mark.parametrize(
    "arguments, expected",
    [
        (["--schema", str(SCHEMA_PATH)], "provide a file path"),
        (
            ["--stdin", "--auto-fix", "--schema", str(SCHEMA_PATH)],
            "requires --state-file",
        ),
    ],
)
def test_cli_usage_errors_are_reported(arguments, expected) -> None:
    result = CliRunner().invoke(main, arguments)
    assert result.exit_code == 2
    assert expected in result.output


def test_cli_parse_and_schema_load_errors_are_reported(tmp_path: Path) -> None:
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("not json", encoding="utf-8")
    result = CliRunner().invoke(main, [str(invalid_json), "--schema", str(SCHEMA_PATH)])
    assert result.exit_code == 2
    assert "invalid JSON" in result.output

    invalid_schema = tmp_path / "schema.json"
    invalid_schema.write_text("not json", encoding="utf-8")
    result = CliRunner().invoke(
        main, [str(invalid_json), "--schema", str(invalid_schema)]
    )
    assert result.exit_code == 2
    assert "failed to load schema" in result.output
