"""Shared fixtures for all tests in scripts/python.

When pytest collects tests, the project root (``scripts/python/``) is not
automatically on ``sys.path`` the way the runtime wrapper inserts it during
normal execution.  This file prepends ``src/`` so that imports resolve
correctly against the ``src/lib/`` and ``src/cli/`` layouts.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from click.testing import CliRunner

_PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(_PROJECT_SRC))


def _classification_errors(items: list[pytest.Item]) -> list[str]:
    """Return collected tests that lack exactly one test classification."""
    errors: list[str] = []
    for item in items:
        is_unit = item.get_closest_marker("unit") is not None
        is_integration = item.get_closest_marker("integration") is not None
        if is_unit == is_integration:
            errors.append(item.nodeid)
    return errors


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> Iterator[None]:
    """Reject missing or conflicting classifications before marker selection."""
    errors = _classification_errors(items)
    yield
    if errors:
        details = ", ".join(errors)
        raise pytest.UsageError(
            "Every collected test must have exactly one of 'unit' or "
            f"'integration'; invalid tests: {details}"
        )


@pytest.fixture
def runner() -> CliRunner:
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
