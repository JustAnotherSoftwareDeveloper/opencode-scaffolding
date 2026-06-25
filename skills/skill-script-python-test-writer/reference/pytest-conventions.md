# Pytest Conventions

## Naming Conventions

- Test files start with `test_` prefix (e.g., `test_count_tokens.py`, `test_count_tokens_cli.py`).
- Test functions start with `test_` prefix (e.g., `test_count_tokens_with_file`).
- Test classes start with `Test` prefix (e.g., `TestCountTokensCLI`).

## CliRunner Usage Pattern

CLI integration tests use `click.testing.CliRunner` to invoke CLI commands without subprocess overhead.

```python
from click.testing import CliRunner
from cli.count_tokens import main

def test_cli_nominal():
    runner = CliRunner()
    result = runner.invoke(main, ["input.txt"])
    assert result.exit_code == 0
    assert "expected" in result.output
```

Use `runner.isolated_filesystem()` as a context manager when tests need to create or read files.

```python
def test_with_file():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("input.txt").write_text("hello world")
        result = runner.invoke(main, ["input.txt"])
        assert result.exit_code == 0
```

## Unit Test Direct Import Pattern

Unit tests import directly from `lib.<script_name>.<module>` and call functions directly.

```python
from lib.count_tokens.core import count_tokens, process_file

def test_count_tokens_empty():
    assert count_tokens("") == 0

def test_process_file_nominal(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("hello world")
    result = process_file(file)
    assert result["tokens"] == 2
```

Use `tmp_path` (pytest built-in) for file I/O in unit tests.
Use `tmp_path` over `isolated_filesystem()` when not testing CLI invocation.

## Fixture-Based Shared Setup

Define shared fixtures in `tests/conftest.py` to avoid duplication across test files.

### Conftest Fixture Example

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

### Fixture Usage Example

```python
def test_with_sample_file(runner, sample_text):
    result = runner.invoke(main, [str(sample_text)])
    assert result.exit_code == 0
    assert "5" in result.output

def test_with_empty_file(runner, empty_file):
    result = runner.invoke(main, [str(empty_file)])
    assert result.exit_code == 0
    assert "0" in result.output
```

## Parameterized Tests

Use `@pytest.mark.parametrize` to test multiple inputs with a single test function.
This reduces boilerplate and ensures consistent assertion logic across variants.

```python
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
    assert count_tokens(text) == expected
```

Use parametrize for CLI error paths to cover multiple exit conditions compactly.

```python
@pytest.mark.parametrize(
    "args, expected_exit_code, expected_substring",
    [
        ([], 2, "Missing argument"),
        (["/nonexistent"], 2, "does not exist"),
        (["--format", "bogus", "file.txt"], 2, "invalid choice"),
    ],
)
def test_cli_error_paths(args, expected_exit_code, expected_substring):
    runner = CliRunner()
    with runner.isolated_filesystem():
        if args and args[-1] != "file.txt":
            pass
        else:
            Path("file.txt").write_text("some content")
        result = runner.invoke(main, args)
        assert result.exit_code == expected_exit_code
        assert expected_substring in result.output
```

## Paired Script / Test Mapping

- `src/cli/<name>.py` → `tests/test_<name>_cli.py`
- `src/lib/<name>/core.py` → `tests/test_<name>.py` (tests lib/)
- `src/lib/<name>/formats.py` → Coverage included in unit tests
- `src/lib/<name>/validators.py` → Coverage included in unit tests
- `src/lib/shared/<module>.py` → `tests/test_shared_<module>.py`

The test writer reads generated source files to determine module structure and automatically generates corresponding tests.

## BLOCKED Edge Case Handling

- If the source CLI or lib files do not exist: `BLOCKED: Source script <name> not found — run skill-script-python-writer first.`
- If a shared module referenced by the script does not exist: `BLOCKED: Shared module <name> not found — create it under src/lib/shared/ first.`
- If generated tests fail coverage on first run, retry once with expanded edge-case tests.
- On second coverage failure, return `PARTIAL` with failing test names and specific coverage gaps.

## Test Isolation Convention

Each test is independent and shares no state with other tests.
Use `isolated_filesystem()` or `tmp_path` for file-based tests.
Use fixtures for reusable setup rather than module-level variables.