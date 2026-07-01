"""test_sequential_pipeline.py — Integration tests for the 2-script sequential pipeline.

Tests the reduced pipeline end-to-end:
  1. validate-task-structure --state-file --schema  — validate task structure
  2. validate-and-format-output --state-file --schema  — validate full output

Also covers individual step behaviour, failure propagation, and edge cases.

Run from ``scripts/python/``:
    uv run pytest tests/test_sequential_pipeline.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.validate_and_format_output import main as validate_format_main
from cli.validate_task_structure import main as validate_structure_main

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "skills"
    / "breakdown-tasks"
    / "schema"
    / "task-packet.schema.json"
)

assert SCHEMA_PATH.is_file(), f"Task-packet schema not found at {SCHEMA_PATH}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_task(purpose: str = "Default purpose", context: str = "Default context.") -> dict:
    """Return a minimal valid task dict."""
    return {
        "purpose": purpose,
        "context": context,
        "filesToRead": [],
        "filesToWrite": [],
        "skills": ["generic-analysis"],
        "executionInstructions": [{"step": 1, "action": "Do the thing."}],
        "verification": [],
        "expectedOutput": f"Output for: {purpose}",
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def runner() -> CliRunner:
    """Provide a CliRunner for all CLI invocations."""
    return CliRunner()


@pytest.fixture
def state_file(tmp_path: Path) -> Path:
    """Return a path to a .tasks state file inside a tmp_path directory."""
    return tmp_path / "state.tasks"


@pytest.fixture
def two_valid_tasks() -> list[dict]:
    """Two minimal tasks with static UUID v4 ids (for step 1 injection)."""
    return [
        _make_task(purpose="Task one purpose", context="Context for task one."),
        _make_task(purpose="Task two purpose", context="Context for task two."),
    ]


# ===========================================================================
# TestPipelineSteps — each script in isolation
# ===========================================================================


class TestPipelineSteps:
    """Each of the two pipeline scripts works correctly in isolation."""

    # --- Step 1: validate-task-structure ---

    def test_step2_valid_tasks_pass(
        self,
        runner: CliRunner,
        state_file: Path,
        two_valid_tasks: list[dict],
    ) -> None:
        """validate-task-structure --state-file exits 0 for valid tasks."""
        state = {"tasks": two_valid_tasks}
        state_file.write_text(json.dumps(state))

        result = runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 0, f"STDERR: {result.stderr}"
        data = json.loads(result.output)
        assert data["valid"] is True

    def test_step2_invalid_tasks_fail(
        self,
        runner: CliRunner,
        state_file: Path,
    ) -> None:
        """validate-task-structure --state-file exits 1 for invalid tasks."""
        task = _make_task(purpose="x" * 201)  # purpose over maxLength 200
        state = {"tasks": [task]}
        state_file.write_text(json.dumps(state))

        result = runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["valid"] is False
        assert len(data["errors"]) > 0

    def test_step2_missing_tasks_key(
        self, runner: CliRunner, state_file: Path
    ) -> None:
        """--state-file without 'tasks' key exits code 2."""
        state_file.write_text(json.dumps({"not_tasks": []}))
        result = runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 2
        assert "must contain a JSON object with a 'tasks' array" in result.output

    # --- Step 3: validate-and-format-output ---

    def test_step3_valid_output_passes(
        self,
        runner: CliRunner,
        state_file: Path,
        two_valid_tasks: list[dict],
    ) -> None:
        """validate-and-format-output --state-file exits 0 for valid output."""
        data = {"summary": "Integration test summary.", "tasks": two_valid_tasks}
        state_file.write_text(json.dumps(data))

        result = runner.invoke(
            validate_format_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 0, f"STDERR: {result.stderr}"
        # stdout is raw JSON
        parsed = json.loads(result.output.strip())
        assert parsed["summary"] == "Integration test summary."
        assert len(parsed["tasks"]) == 2

    def test_step3_missing_summary(
        self,
        runner: CliRunner,
        state_file: Path,
        two_valid_tasks: list[dict],
    ) -> None:
        """Missing summary in output triggers exit code 1."""
        data = {"tasks": two_valid_tasks}
        state_file.write_text(json.dumps(data))

        result = runner.invoke(
            validate_format_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 1

    def test_step3_empty_tasks(
        self, runner: CliRunner, state_file: Path
    ) -> None:
        """Empty tasks array triggers exit code 1 (minItems: 1)."""
        data = {"summary": "Empty tasks test.", "tasks": []}
        state_file.write_text(json.dumps(data))

        result = runner.invoke(
            validate_format_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 1


# ===========================================================================
# TestEndToEndPipeline — full sequential pipeline
# ===========================================================================


class TestEndToEndPipeline:
    """Full 2-script pipeline executed end-to-end."""

    def test_full_pipeline_success(
        self,
        runner: CliRunner,
        state_file: Path,
        tmp_path: Path,
    ) -> None:
        """End-to-end: create tasks → validate structure → validate output."""
        # --- Seed: write initial state with minimal tasks ---
        initial_tasks = [
            _make_task(purpose="Pipeline task one", context="Context for pipeline task one."),
            _make_task(purpose="Pipeline task two", context="Context for pipeline task two."),
            _make_task(purpose="Pipeline task three", context="Context for pipeline task three."),
        ]
        state = {"tasks": initial_tasks}
        state_file.write_text(json.dumps(state))

        # --- Step 1: validate-task-structure ---
        result1 = runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result1.exit_code == 0, f"Step 1 failed: {result1.stderr}"
        data1 = json.loads(result1.output)
        assert data1["valid"] is True

        # --- Assemble full output from state file data ---
        after_step1: dict = json.loads(state_file.read_text())
        output_data = {
            "summary": "End-to-end pipeline test: three tasks.",
            "tasks": after_step1["tasks"],
        }
        output_file = tmp_path / "output.json"
        output_file.write_text(json.dumps(output_data))

        # --- Step 2: validate-and-format-output ---
        result2 = runner.invoke(
            validate_format_main,
            [str(output_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result2.exit_code == 0, f"Step 2 failed: {result2.stderr}"
        parsed = json.loads(result2.output.strip())
        assert isinstance(parsed, dict)
        assert "summary" in parsed
        assert len(parsed["tasks"]) == 3

    def test_pipeline_preserves_task_order(
        self,
        runner: CliRunner,
        state_file: Path,
    ) -> None:
        """Task order is preserved through both pipeline steps."""
        purposes = ["First task", "Second task", "Third task"]
        tasks = [_make_task(purpose=p, context=f"Context {p}.") for p in purposes]
        state = {"tasks": tasks}
        state_file.write_text(json.dumps(state))

        # Step 1: validate-task-structure
        runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        after_step1: dict = json.loads(state_file.read_text())
        assert [t["purpose"] for t in after_step1["tasks"]] == purposes

    def test_pipeline_step2_stdin_alternative(
        self,
        runner: CliRunner,
        state_file: Path,
        two_valid_tasks: list[dict],
    ) -> None:
        """Step 2 via --stdin (instead of --state-file) also works."""
        state = {"tasks": two_valid_tasks}
        state_file.write_text(json.dumps(state))

        # Step 2 via --stdin: read tasks from stdout-like piping
        result2 = runner.invoke(
            validate_structure_main,
            ["--stdin", "--schema", str(SCHEMA_PATH)],
            input=json.dumps(two_valid_tasks),
        )
        assert result2.exit_code == 0, f"Step 2 (stdin) failed: {result2.stderr}"
        data2 = json.loads(result2.output)
        assert data2["valid"] is True

    def test_pipeline_output_raw_json_no_fences(
        self,
        runner: CliRunner,
        state_file: Path,
        tmp_path: Path,
    ) -> None:
        """Step 2 output is raw JSON without markdown fences."""
        tasks = [_make_task(purpose="Raw JSON test", context="Context.")]
        state = {"tasks": tasks}
        state_file.write_text(json.dumps(state))

        # Run step 2 (validate-and-format-output) directly
        output_data = {"summary": "Raw JSON test.", "tasks": tasks}
        output_file = tmp_path / "output.json"
        output_file.write_text(json.dumps(output_data))

        result = runner.invoke(
            validate_format_main,
            [str(output_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 0
        output = result.output
        assert "```" not in output
        assert "```json" not in output
        assert not output.startswith("Here")
        assert not output.startswith("The")
        json.loads(output.strip())  # ensure valid standalone JSON


# ===========================================================================
# TestFailurePropagation — invalid input fails at the correct step
# ===========================================================================


class TestFailurePropagation:
    """Invalid or malformed data is caught at the expected pipeline step."""

    def test_step2_rejects_missing_purpose(
        self, runner: CliRunner, state_file: Path
    ) -> None:
        """Tasks missing 'purpose' fail at step 2 (validate-task-structure)."""
        task = _make_task(purpose="Will be removed")
        del task["purpose"]
        state = {"tasks": [task]}
        state_file.write_text(json.dumps(state))

        result = runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["valid"] is False
        error_text = " ".join(data["errors"])
        assert "purpose" in error_text

    def test_step2_rejects_purpose_too_long(
        self, runner: CliRunner, state_file: Path
    ) -> None:
        """Purpose exceeding 200 characters fails at step 2."""
        task = _make_task(purpose="x" * 201)
        state = {"tasks": [task]}
        state_file.write_text(json.dumps(state))

        result = runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert data["valid"] is False

    def test_step2_accepts_empty_tasks_array(
        self, runner: CliRunner, state_file: Path
    ) -> None:
        """Empty tasks array passes validation at step 2 (no tasks to validate).
        The responses is ``{"valid": true}`` — the ``validate()`` function
        returns success for an empty list because there are no task objects
        to check against the schema.
        """
        state = {"tasks": []}
        state_file.write_text(json.dumps(state))

        result = runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["valid"] is True

    def test_step3_rejects_empty_tasks(
        self, runner: CliRunner, state_file: Path
    ) -> None:
        """Empty tasks array in the output fails at step 3 (minItems: 1)."""
        data = {"summary": "Empty tasks test.", "tasks": []}
        state_file.write_text(json.dumps(data))

        result = runner.invoke(
            validate_format_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 1

    def test_step3_rejects_missing_summary(
        self, runner: CliRunner, state_file: Path
    ) -> None:
        """Missing summary at the output level fails at step 3."""
        task = _make_task(purpose="Task with no summary")
        data = {"tasks": [task]}
        state_file.write_text(json.dumps(data))

        result = runner.invoke(
            validate_format_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 1

    def test_step3_rejects_extra_root_keys(
        self, runner: CliRunner, state_file: Path
    ) -> None:
        """Extra keys at the output root (beyond summary + tasks) fail at step 3."""
        task = _make_task(purpose="Extra keys task")
        data = {"summary": "Extra keys test.", "tasks": [task], "extraKey": "invalid"}
        state_file.write_text(json.dumps(data))

        result = runner.invoke(
            validate_format_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 1

    def test_step3_rejects_empty_skills(
        self, runner: CliRunner, state_file: Path
    ) -> None:
        """A task with empty skills array (minItems: 1) fails at step 3."""
        task = _make_task(purpose="Empty skills task")
        task["skills"] = []
        data = {"summary": "Empty skills test.", "tasks": [task]}
        state_file.write_text(json.dumps(data))

        result = runner.invoke(
            validate_format_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result.exit_code == 1


# ===========================================================================
# TestEdgeCases — unusual or boundary conditions
# ===========================================================================


class TestEdgeCases:
    """Edge cases: empty input, single task, all-empty fields, max tasks."""

    def test_single_task_pipeline(
        self, runner: CliRunner, state_file: Path, tmp_path: Path
    ) -> None:
        """Pipeline works with a single task (boundary: minItems = 1)."""
        tasks = [_make_task(purpose="Single task", context="Context.")]
        state = {"tasks": tasks}
        state_file.write_text(json.dumps(state))

        # Step 1: validate-task-structure
        result1 = runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result1.exit_code == 0

        # Step 2: validate-and-format-output
        after_step1: dict = json.loads(state_file.read_text())
        output_data = {"summary": "Single task pipeline.", "tasks": after_step1["tasks"]}
        output_file = tmp_path / "output.json"
        output_file.write_text(json.dumps(output_data))
        result3 = runner.invoke(
            validate_format_main,
            [str(output_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result3.exit_code == 0
        parsed = json.loads(result3.output.strip())
        assert len(parsed["tasks"]) == 1

    def test_tasks_with_empty_arrays(
        self, runner: CliRunner, state_file: Path, tmp_path: Path
    ) -> None:
        """Tasks with empty filesToRead, filesToWrite, verification work (skills uses generic-analysis)."""
        task = _make_task(
            purpose="Empty arrays task",
            context="All optional arrays are empty.",
        )
        task["filesToRead"] = []
        task["filesToWrite"] = []
        task["skills"] = ["generic-analysis"]
        task["verification"] = []

        state = {"tasks": [task]}
        state_file.write_text(json.dumps(state))

        # Step 1: validate-task-structure
        result1 = runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result1.exit_code == 0, f"Step 1 failed: {result1.stderr}"

        # Step 2: validate-and-format-output
        output_data = {"summary": "Empty arrays test.", "tasks": [task]}
        output_file = tmp_path / "output.json"
        output_file.write_text(json.dumps(output_data))
        result3 = runner.invoke(
            validate_format_main,
            [str(output_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result3.exit_code == 0

    def test_pipeline_with_max_tasks(
        self, runner: CliRunner, state_file: Path, tmp_path: Path
    ) -> None:
        """Pipeline handles the maximum of 100 tasks (boundary: max)."""
        tasks = [_make_task(purpose=f"Task {i}", context=f"Context {i}.") for i in range(100)]
        state = {"tasks": tasks}
        state_file.write_text(json.dumps(state))

        # Step 1: validate-task-structure
        result1 = runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result1.exit_code == 0, f"Step 1 failed for 100 tasks: {result1.stderr}"

        # Step 2: validate-and-format-output
        after_step1: dict = json.loads(state_file.read_text())
        output_data = {"summary": "Max tasks (100) pipeline test.", "tasks": after_step1["tasks"]}
        output_file = tmp_path / "output.json"
        output_file.write_text(json.dumps(output_data))
        result3 = runner.invoke(
            validate_format_main,
            [str(output_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result3.exit_code == 0
        parsed = json.loads(result3.output.strip())
        assert len(parsed["tasks"]) == 100

    def test_all_tasks_have_identical_structure(
        self, runner: CliRunner, state_file: Path, tmp_path: Path
    ) -> None:
        """Multiple identically-structured tasks all pass through the pipeline."""
        template = _make_task(purpose="Same purpose", context="Same context.")
        tasks = [dict(template) for _ in range(3)]
        state = {"tasks": tasks}
        state_file.write_text(json.dumps(state))

        # Step 1: validate-task-structure
        result1 = runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result1.exit_code == 0

        # Step 2: validate-and-format-output
        after_step1: dict = json.loads(state_file.read_text())
        output_data = {"summary": "Identical tasks test.", "tasks": after_step1["tasks"]}
        output_file = tmp_path / "output.json"
        output_file.write_text(json.dumps(output_data))
        result3 = runner.invoke(
            validate_format_main,
            [str(output_file), "--schema", str(SCHEMA_PATH)],
        )
        assert result3.exit_code == 0

    def test_state_file_persists_after_step2(
        self, runner: CliRunner, state_file: Path, two_valid_tasks: list[dict]
    ) -> None:
        """State file content (including custom fields) survives step 1."""
        state = {"tasks": two_valid_tasks, "custom_metadata": "survives validation"}
        state_file.write_text(json.dumps(state))

        # Step 1: validate-task-structure
        runner.invoke(
            validate_structure_main,
            ["--state-file", str(state_file), "--schema", str(SCHEMA_PATH)],
        )

        after_step2: dict = json.loads(state_file.read_text())
        assert after_step2.get("custom_metadata") == "survives validation"
        assert len(after_step2["tasks"]) == 2