"""CLI integration tests for agent_eval_suite."""

from __future__ import annotations

import subprocess
from pathlib import Path


def test_agent_eval_suite_list_cases() -> None:
    """Verify --list-cases outputs JSON with cases."""
    result = subprocess.run(
        ["python", "src/cli/agent_eval_suite.py", "--list-cases"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0
    assert "cases" in result.stdout


def test_agent_eval_suite_write_inspect_task(tmp_path: Path) -> None:
    """Verify --write-inspect-task creates a file."""
    output_path = tmp_path / "inspect_task.py"
    result = subprocess.run(
        [
            "python",
            "src/cli/agent_eval_suite.py",
            "--write-inspect-task",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0
    assert output_path.exists()


def test_agent_eval_suite_requires_model_for_inspect(tmp_path: Path) -> None:
    """Verify --run-inspect requires --inspect-model."""
    output_path = tmp_path / "inspect_task.py"
    result = subprocess.run(
        [
            "python",
            "src/cli/agent_eval_suite.py",
            "--write-inspect-task",
            str(output_path),
            "--run-inspect",
        ],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode != 0
    assert "requires" in result.stderr.lower() or "Error" in result.stderr


def test_agent_eval_suite_requires_model_for_terminal_bench(tmp_path: Path) -> None:
    """Verify --run-terminal-bench requires --tb-model."""
    output_path = tmp_path / "inspect_task.py"
    result = subprocess.run(
        [
            "python",
            "src/cli/agent_eval_suite.py",
            "--write-inspect-task",
            str(output_path),
            "--run-terminal-bench",
        ],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode != 0
    assert "requires" in result.stderr.lower() or "Error" in result.stderr
