"""Integration coverage for the registered ``example`` console command."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

PYTHON_PROJECT = Path(__file__).resolve().parents[1]


def test_example_console_entry_point_prints_success_message() -> None:
    """Invoke the installed project script and verify its output contract."""
    result = subprocess.run(
        ["uv", "run", "--project", str(PYTHON_PROJECT), "example"],
        cwd=PYTHON_PROJECT,
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "example runtime=python status=ok\n"
    assert result.stderr == ""
