"""CLI integration tests for init-state-file."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from cli.init_state_file import main


def test_help() -> None:
    """--help produces usage info and exits 0."""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Create a stub decomposition state file" in result.output


def test_missing_required_option() -> None:
    """Missing --output-dir exits 2."""
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 2  # click exits 2 for missing required option


def test_creates_state_file(tmp_path: Path) -> None:
    """Normal invocation creates a state file and prints its path."""
    out_dir = tmp_path / ".tasks"
    runner = CliRunner()
    result = runner.invoke(main, ["--output-dir", str(out_dir)])
    assert result.exit_code == 0
    assert "decomposition.json" in result.output

    state_path = Path(result.output.strip())
    assert state_path.exists()


def test_output_is_valid_json_stub(tmp_path: Path) -> None:
    """The created file contains a valid empty stub."""
    out_dir = tmp_path / ".tasks"
    runner = CliRunner()
    result = runner.invoke(main, ["--output-dir", str(out_dir)])
    assert result.exit_code == 0

    state_path = Path(result.output.strip())
    with open(state_path) as f:
        data = json.load(f)
    assert data == {"summary": "", "tasks": []}


def test_collision_retry_produces_different_filename(tmp_path: Path) -> None:
    """Pre-existing file with same epoch causes retry with incremented epoch."""
    import time

    out_dir = tmp_path / ".tasks"
    out_dir.mkdir(parents=True)

    epoch = int(time.time())
    # Pre-create a collision file
    (out_dir / f"{epoch}-decomposition.json").write_text("{}")

    runner = CliRunner()
    result = runner.invoke(main, ["--output-dir", str(out_dir)])
    assert result.exit_code == 0

    state_path = Path(result.output.strip())
    assert os.path.exists(state_path)
    assert state_path != out_dir / f"{epoch}-decomposition.json"


def test_unwritable_directory_exits_1(tmp_path: Path) -> None:  # noqa: ARG001
    """OS-level failure to create or write exits 1."""
    # Use a path where we cannot write
    out_dir = "/root/.tasks"
    runner = CliRunner()
    result = runner.invoke(main, ["--output-dir", out_dir])
    assert result.exit_code == 1
    assert "Error:" in result.output


def test_file_exists_error_exits_1(tmp_path: Path) -> None:
    """CLI catches FileExistsError from init_state and exits 1."""
    out_dir = tmp_path / ".tasks"
    with patch(
        "cli.init_state_file.init_state",
        side_effect=FileExistsError("collision"),
    ):
        runner = CliRunner()
        result = runner.invoke(main, ["--output-dir", str(out_dir)])
        assert result.exit_code == 1
        assert "Error:" in result.output
