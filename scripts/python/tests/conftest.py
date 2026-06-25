"""Shared fixtures for all tests in scripts/python.

When pytest collects tests, the project root (``scripts/python/``) is not
automatically on ``sys.path`` the way the runtime wrapper inserts it during
normal execution.  This file prepends ``src/`` so that imports resolve
correctly against the ``src/lib/`` and ``src/cli/`` layouts.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(_PROJECT_SRC))


@pytest.fixture
def runner() -> "CliRunner":
    """Provide a CliRunner instance for CLI integration tests."""
    from click.testing import CliRunner

    return CliRunner()


@pytest.fixture
def sample_text(tmp_path: Path) -> Path:
    """Create a sample text file and return its path."""
    data_path = tmp_path / "sample.txt"
    data_path.write_text("hello world foo bar baz")
    return data_path


@pytest.fixture
def empty_file(tmp_path: Path) -> Path:
    """Create an empty file and return its path."""
    data_path = tmp_path / "empty.txt"
    data_path.write_text("")
    return data_path
