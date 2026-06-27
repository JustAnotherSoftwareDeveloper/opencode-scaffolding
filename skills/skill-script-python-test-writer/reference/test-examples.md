# Test Examples

## File-Based Tests with `isolated_filesystem()`

CliRunner's `isolated_filesystem()` creates a temporary directory as the CWD, ensuring tests do not pollute the real filesystem.

```python
"""CLI integration tests for count-tokens."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.count_tokens import main


class TestCountTokensCLI:
    """Integration tests for the count-tokens CLI."""

    runner = CliRunner()

    def test_nominal_file(self):
        """Count tokens in a file with typical content."""
        with self.runner.isolated_filesystem():
            Path("input.txt").write_text("hello world")
            result = self.runner.invoke(main, ["input.txt"])
            assert result.exit_code == 0
            assert '"tokens": 2' in result.output

    def test_empty_file(self):
        """Empty file produces zero tokens."""
        with self.runner.isolated_filesystem():
            Path("empty.txt").write_text("")
            result = self.runner.invoke(main, ["empty.txt"])
            assert result.exit_code == 0
            assert '"tokens": 0' in result.output

    def test_file_with_special_characters(self):
        """File with special characters and Unicode is handled."""
        with self.runner.isolated_filesystem():
            Path("unicode.txt").write_text("café résumé 中文 Español")
            result = self.runner.invoke(main, ["unicode.txt"])
            assert result.exit_code == 0
            assert '"tokens": 4' in result.output

    def test_nonexistent_file_fails(self):
        """Missing input path exits non-zero."""
        result = self.runner.invoke(main, ["nonexistent.txt"])
        assert result.exit_code != 0
```

## File-Based Tests with `tmp_path`

For unit tests that need a temp directory without CliRunner, use the built-in `tmp_path` fixture.

```python
"""Unit tests for count-tokens lib module."""

from pathlib import Path

from lib.count_tokens.core import count_tokens, process_file


def test_count_tokens_empty_string():
    assert count_tokens("") == 0


def test_count_tokens_whitespace_only():
    assert count_tokens("   \n\t  ") == 0


def test_count_tokens_multiple_words():
    assert count_tokens("hello world foo bar") == 4


def test_process_file_nominal(tmp_path: Path):
    """process_file reads a file and returns a dict with token count."""
    input_file = tmp_path / "test.txt"
    input_file.write_text("hello world")
    result = process_file(input_file)
    assert result["tokens"] == 2
    assert result["path"] == str(input_file.resolve())
```

## Mock-Based Tests with `unittest.mock.patch`

Use `unittest.mock.patch` when a script depends on external resources (network, filesystem outside the workspace, system commands).

```python
"""Tests for validate-skill script with mocking."""

from unittest.mock import patch, mock_open

import pytest
from click.testing import CliRunner

from cli.validate_skill import main


def test_validate_skill_network_failure():
    """When a dependency check fails (network error), the script exits non-zero."""
    with patch("lib.skill_validator.checks.fetch_schema", side_effect=ConnectionError("timeout")):
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path("skill.yaml").write_text("name: test-skill\ndescription: test")
            result = runner.invoke(main, ["skill.yaml"])
            assert result.exit_code == 1
            assert "Error" in result.output
```

## Mock-Based Tests with `monkeypatch`

Prefer monkeypatch (pytest built-in) over `unittest.mock.patch` for simpler attribute/sys.path overrides.

```python
"""Tests for collect-skills script using monkeypatch."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from cli.collect_skills import main


def test_collect_skills_empty_directory(monkeypatch, tmp_path):
    """When no skills exist, the script returns an empty collection."""
    monkeypatch.setattr("cli.collect_skills.DEFAULT_SKILLS_DIR", str(tmp_path))
    runner = CliRunner()
    result = runner.invoke(main, [])
    assert result.exit_code == 0
    assert "[]" in result.output or "count" in result.output
```

## Fixture-Based Shared Setup (conftest.py)

Shared fixtures in `conftest.py` eliminate duplication across test files.

### conftest.py

```python
"""Shared fixtures for all tests in scripts/python."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add src/ to sys.path so that tests can import from cli.* and lib.*
_PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
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
```

### Usage Examples

```python
"""Tests for count-tokens using shared fixtures."""

import json

from cli.count_tokens import main


def test_with_sample_file(runner, sample_text):
    """Uses conftest fixtures for file setup and CliRunner."""
    result = runner.invoke(main, [str(sample_text)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["tokens"] == 5


def test_with_empty_file(runner, empty_file):
    """Uses the empty-file fixture."""
    result = runner.invoke(main, [str(empty_file)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["tokens"] == 0
```

## Parameterized Tests

Use `@pytest.mark.parametrize` to test multiple inputs with a single test function, reducing boilerplate and ensuring consistent assertion logic.

```python
"""Parameterized unit tests for count-tokens lib."""

import pytest
from lib.count_tokens.core import count_tokens


@pytest.mark.parametrize(
    "text, expected",
    [
        ("", 0),
        ("   ", 0),
        ("hello", 1),
        ("hello world", 2),
        ("hello   world", 2),
        ("a b c d e", 5),
        ("line1\nline2\nline3", 3),
        ("\n\n\n", 0),
        ("  leading spaces", 2),
        ("trailing spaces  ", 2),
    ],
)
def test_count_tokens_various_inputs(text, expected):
    """Verify token counting for various input patterns."""
    assert count_tokens(text) == expected
```

## Unit Test vs Integration Test Pattern

Generated test suites maintain a clear separation between unit and integration tests.

- **Unit test**: `tests/test_<script_name>.py` — `lib.*` functions in isolation. Key tool: Direct function calls, `tmp_path` for file I/O
- **CLI integration test**: `tests/test_<script_name>_cli.py` — Full CLI pipeline from argument parsing to output. Key tool: `CliRunner.invoke()`, `isolated_filesystem()`

The integration test verifies that CLI arguments parse correctly, the lib function is invoked, and output formatting produces the expected structure.
Unit tests verify lib function logic in detail, including error handling and edge cases that the CLI test covers indirectly.
