"""Unit tests for lib.init_state_file.core."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from lib.init_state_file.core import init_state


def test_creates_state_file(tmp_path: Path) -> None:
    """Successfully creates a state file with correct stub payload."""
    out_dir = tmp_path / ".tasks"
    state_path = init_state(str(out_dir))

    assert os.path.exists(state_path)
    assert "decomposition.json" in state_path

    with open(state_path) as f:
        data = json.load(f)
    assert data == {"summary": "", "tasks": []}


def test_creates_output_directory(tmp_path: Path) -> None:
    """Creates the output directory if it does not exist."""
    out_dir = tmp_path / "nested" / ".tasks"
    state_path = init_state(str(out_dir))
    assert os.path.exists(state_path)
    assert out_dir.is_dir()


def test_filename_contains_epoch() -> None:
    """State file filename includes the current epoch timestamp."""
    out_dir = Path("/tmp") / "test-tasks-epoch"
    out_dir.mkdir(parents=True, exist_ok=True)
    before = int(time.time())
    state_path = init_state(str(out_dir))
    after = int(time.time())

    filename = Path(state_path).name
    # Extract epoch from filename: <epoch>-decomposition.json
    epoch_str = filename.split("-")[0]
    epoch = int(epoch_str)

    assert before <= epoch <= after

    # Cleanup
    os.unlink(state_path)
    out_dir.rmdir()


def test_returns_absolute_path(tmp_path: Path) -> None:
    """Returns an absolute path."""
    state_path = init_state(str(tmp_path))
    assert Path(state_path).is_absolute()


def test_writes_valid_json(tmp_path: Path) -> None:
    """The written state file contains valid JSON."""
    state_path = init_state(str(tmp_path))
    content = Path(state_path).read_text()
    data = json.loads(content)
    assert isinstance(data, dict)
    assert "summary" in data
    assert "tasks" in data


def test_collision_retry(tmp_path: Path) -> None:
    """When a file collision occurs, increment epoch and retry."""
    epoch = int(time.time())
    # Pre-create a file that would collide
    collision = tmp_path / f"{epoch}-decomposition.json"
    collision.write_text("{}")

    # This should succeed by using epoch+1
    state_path = init_state(str(tmp_path))
    assert state_path != str(collision)
    assert "decomposition.json" in state_path


def test_exhausted_retries_raises(tmp_path: Path, monkeypatch) -> None:
    """If all retry attempts collide, raises OSError."""
    import builtins

    real_open = builtins.open

    def _mock_open(*args, **kwargs):
        if args and len(args) >= 2 and args[1] & os.O_CREAT:
            raise FileExistsError("collision")
        return real_open(*args, **kwargs)

    monkeypatch.setattr(os, "open", _mock_open)
    monkeypatch.setattr(os, "fdopen", real_open)

    with pytest.raises(OSError, match="Could not create state file"):
        init_state(str(tmp_path))
