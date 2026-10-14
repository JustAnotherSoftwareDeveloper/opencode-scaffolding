# Pytest Conventions

In the patterns throughout this reference, `<script_name>` is the selected library
package name from its existing `src/lib/` directory, `<module>` is the referenced
module's name from its source filename, and `<name>` is the selected script identifier
from its existing CLI filename or library directory. Substitute these source-derived
names when applying import, path, or test-name patterns or reporting blocked outcomes.
The examples are minimal behavior patterns; classify every test created from them as
described below, even when a short snippet omits its marker for brevity.

## Naming Conventions

- Test files start with `test_` prefix (e.g., `test_count_tokens.py`, `test_count_tokens_cli.py`).
- Test functions start with `test_` prefix (e.g., `test_count_tokens_with_file`).
- Test classes start with `Test` prefix (e.g., `TestCountTokensCLI`).

## Unit And Integration Classification

Every collected test must have exactly one effective classification: `unit` or
`integration`. Pytest collection must reject tests with neither classification or both.
Apply the classification to each test, or use an enclosing marker only when every
affected test still resolves to exactly one class.

- **Unit:** Call production behavior directly and assert its observable contract. A
  direct call to a CLI module's callback or helper is a unit test when it bypasses
  Click's command invocation layer and isolates external effects. A test may reach
  library behavior through a CLI callable path; importing `lib.*` directly is not
  mandatory.
- **Integration:** Classify `CliRunner`, console-entry-point, subprocess, and workflow
  execution as integration. A workflow that combines modules or systems is integration
  even if it also exercises unit-level behavior.

The unit-only gate selects the complete `unit` classification. Do not use test paths,
keywords, changed-file selection, or additional markers to narrow that set. Integration
tests may contribute to a separately reported full-suite result, never to the unit-only
coverage result. See [Coverage Strategy](coverage-strategy.md) for the fixed source
denominator, exclusions, and independent run rules.

```python
import pytest


@pytest.mark.unit
def test_count_tokens_empty():
    assert count_tokens("") == 0


@pytest.mark.integration
def test_cli_nominal():
    result = CliRunner().invoke(main, ["input.txt"])
    assert result.exit_code == 0
```

## CliRunner Usage Pattern

CLI integration tests use `click.testing.CliRunner` to invoke CLI commands without subprocess overhead.

```python
import pytest
from click.testing import CliRunner
from cli.count_tokens import main

@pytest.mark.integration
def test_cli_nominal():
    runner = CliRunner()
    result = runner.invoke(main, ["input.txt"])
    assert result.exit_code == 0
    assert "expected" in result.output
```

Use `runner.isolated_filesystem()` as a context manager when tests need to create or read files.

```python
import pytest

@pytest.mark.integration
def test_with_file():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("input.txt").write_text("hello world")
        result = runner.invoke(main, ["input.txt"])
        assert result.exit_code == 0
```

## Unit Test Direct Import Pattern

Direct `lib.<script_name>.<module>` imports are one unit-testing option, not a
requirement. A unit test can instead call isolated production behavior through a CLI
callback or helper, as long as it does not use Click invocation or another integration
boundary.

```python
import pytest
from lib.count_tokens.core import count_tokens, process_file

@pytest.mark.unit
def test_count_tokens_empty():
    assert count_tokens("") == 0

@pytest.mark.unit
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
import pytest

@pytest.mark.integration
def test_with_sample_file(runner, sample_text):
    result = runner.invoke(main, [str(sample_text)])
    assert result.exit_code == 0
    assert "5" in result.output

@pytest.mark.integration
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

@pytest.mark.unit
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
import pytest

@pytest.mark.integration
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

- `src/cli/<name>.py` → `tests/test_<name>_cli.py` for `CliRunner` integration coverage;
  directly callable CLI logic may also be covered by unit tests without Click invocation.
- `src/lib/<name>/core.py` → `tests/test_<name>.py` (tests lib/)
- `src/lib/<name>/formats.py` → Coverage included in unit tests
- `src/lib/<name>/validators.py` → Coverage included in unit tests
- `src/lib/shared/<module>.py` → `tests/test_shared_<module>.py`

The test writer reads generated source files to determine module structure and automatically generates corresponding tests.

## Handling `BLOCKED` Outcomes

- If the source CLI or lib files do not exist: `BLOCKED: Source script <name> not found — run skill-script-python-writer first.`
- If a shared module referenced by the script does not exist: `BLOCKED: Shared module <name> not found — create it under src/lib/shared/ first.`
- If generated tests fail coverage on first run, retry once with expanded edge-case tests.
- On second coverage failure, return `PARTIAL` with failing test names and specific coverage gaps.

## Test Isolation Convention

Each test is independent and shares no state with other tests.
Use `isolated_filesystem()` or `tmp_path` for file-based tests.
Use fixtures for reusable setup rather than module-level variables.
Coverage classification is per test, not per file; any test module can contain both
classes only when each collected test resolves to exactly one class.
