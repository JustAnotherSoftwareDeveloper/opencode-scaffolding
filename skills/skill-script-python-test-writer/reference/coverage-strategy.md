# Coverage Strategy

## Measurement Tool

Coverage is measured at the **line level** via `pytest-cov`.
The `--cov-report=term-missing` flag prints specific uncovered lines on failure.
The required percentage is line coverage; the strategy does not configure a separate
branch-coverage threshold.

## Source Coverage Boundaries

Coverage is measured against these source paths:

- `src/cli/*.py` — CLI entry points tested via `CliRunner.invoke()` in CLI integration test files
- `src/lib/<script_name>/*.py` — Per-script library modules tested via direct function calls in unit test files
- `src/lib/shared/*.py` — Shared library modules tested via `tests/test_shared_<module>.py`
- `src/lib/shared/__init__.py` — Included in this source scope; it is typically empty
  and therefore has no executable lines to cover. Any executable lines remain subject
  to the target.

## Required Coverage Target

The required target is **100% line coverage for the selected source scope above**. Keep
`fail_under = 100` in the coverage configuration; do not defer to a lower configured
target or reduce the selected source scope to make the threshold pass.

If the first run is below 100%, retry once with targeted tests for the uncovered,
in-scope behavior. On a second failure, return `PARTIAL` and report the failing test
names, measured coverage when available, and the remaining coverage gaps. Do not report
the result as complete, weaken the threshold, or add tests for behavior that does not
apply just to force the percentage.

## pyproject.toml Coverage Configuration

```toml
[tool.coverage.run]
source = ["cli", "lib"]
omit = ["*/tests/*", "*/test_*", "*/.tox/*", "*/venv/*", "*/env/*"]

[tool.coverage.report]
fail_under = 100

[tool.pytest.ini_options]
addopts = "--cov=cli --cov=lib --cov-report=term-missing --cov-fail-under=100"
```

## Edge Case Identification Checklist

The cases below are prompts for identifying relevant behavior, not a universal set of
tests required in every suite. Select cases based on the chosen source scope, the
implementation's supported inputs and interface, and its reachable behavior. Test
applicable cases and branch outcomes as needed to execute all in-scope lines; omit
categories the script does not support or that do not apply. Do not invent behavior or
add meaningless tests to satisfy this list. The 100% line-coverage target still applies
to the selected source scope.

- **Input, when accepted or handled by the selected code**
  - Empty input (empty file, empty string, empty list)
  - Whitespace-only input
  - Single-element input
  - Maximum-size input, when size limits or large-input handling are relevant
- **File I/O, for code that reads or writes paths**
  - Nonexistent file path, directory passed where a file is expected, or unreadable
    file when the implementation handles those conditions
  - Unusual encoding or BOM when supported input formats make these relevant
  - Symlink behavior when the code or its contract distinguishes symlinks
- **CLI arguments, for scripts that expose a CLI**
  - Missing required argument, invalid option value (for example, `--format bogus`),
    or extra positional arguments when the interface handles those cases
  - `--help` when the CLI provides it
- **Error handling, for reachable handled failures**
  - Exception raised in a library module, malformed input, or dependency failure (for
    example, a YAML parse error) when the selected code handles that failure
  - Timeout or resource exhaustion only when the implementation has relevant handling
    that is practical and meaningful to exercise
- **Output, when these result shapes exercise distinct behavior**
  - Zero-result, single-result, and multi-result output
  - Special characters or output exceeding typical size when formatting or size
    handling makes them relevant
- **Boundary values, where accepted values or constraints create boundary behavior**
  - Minimum integer (for example, 0), maximum values (for example, large file or many
    items), and type distinctions (for example, `None` versus empty or blank string)

## Error Path Testing

Test every reachable, in-scope error-handling path that is part of the supported
behavior and contributes lines to the selected source scope. Do not require irrelevant
error cases for code with no such path. Use `pytest.mark.parametrize` to cover multiple
applicable error conditions compactly.

Example:

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

## Coverage Exemptions

Use `# pragma: no cover` sparingly and only for these three categories, and only when
the stated conditions actually hold. Keep each exclusion narrow; do not hide reachable
behavior or compensate for missing tests:

1. **`__main__` guard** — The `if __name__ == "__main__": main()` dispatch may be
   exempted by convention when the `main` behavior is covered through the tested CLI
   entry point. Limit the exclusion to the dispatch line:

   ```python
   if __name__ == "__main__":
       main()  # pragma: no cover
   ```

2. **Unreachable defensive code** — A defensive branch may be excluded only when the
   supported input and dependency contracts establish that it cannot be reached. A
   type annotation or an untested assumption alone is not evidence of unreachability; if
   the path can occur, test it:

   ```python
   # The selected API contract guarantees that result is not None.
   if result is None:  # pragma: no cover
       raise RuntimeError("unreachable")
   ```

3. **Version-gated fallbacks** — A fallback for an older Python version may be excluded
   when that version is outside the project's declared supported runtime (for example,
   an older-version fallback when the target is Python 3.12). If that version is
   supported, the fallback is applicable and must be tested in the supported runtime
   matrix.

All other executable lines and applicable reachable error paths must be covered by
tests. If `# pragma: no cover` appears outside these three categories, re-examine the
test generation rather than exempting the code.
