# Coverage Strategy

## Measurement Tool

Coverage is measured at the **line level** via `pytest-cov`.
The `--cov-report=term-missing` flag prints specific uncovered lines on failure.

## Source Coverage Boundaries

Coverage is measured against these source paths:

- `src/cli/*.py` — CLI entry points tested via `CliRunner.invoke()` in CLI integration test files
- `src/lib/<script_name>/*.py` — Per-script library modules tested via direct function calls in unit test files
- `src/lib/shared/*.py` — Shared library modules tested via `tests/test_shared_<module>.py`
- `src/lib/shared/__init__.py` — Typically empty, excluded from coverage concern

## fail_under = 100 Enforcement

Every generated test suite must achieve `fail_under = 100`.
If coverage drops below 100, the test generation retries once with expanded edge-case tests.
On second failure, return `PARTIAL` with the failing test names and coverage gaps.

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

To achieve 100% coverage, every test suite must include tests for the following edge cases:

- **Input**
  - Empty input (empty file, empty string, empty list)
  - Whitespace-only input
  - Maximum-size input
  - Single-element input
- **File I/O**
  - Nonexistent file path
  - Directory passed where file expected
  - Unreadable file (permission denied)
  - File with unusual encoding
  - Symlink to file
  - File with BOM
- **CLI arguments**
  - Missing required argument
  - Invalid option value (`--format bogus`)
  - Extra positional arguments
  - `--help` flag
- **Error handling**
  - Exception raised in lib module
  - Malformed input data
  - Dependency failure (e.g., YAML parse error)
  - Timeout or resource exhaustion
- **Output**
  - Zero-result output
  - Single-result output
  - Multi-result output
  - Output with special characters
  - Output exceeding typical size
- **Boundary values**
  - Minimum integer (0, empty)
  - Maximum values (large file, many items)
  - Type boundaries (None vs empty string vs blank string)

## Error Path Testing

Every non-zero exit code path must have a corresponding test.
Use `pytest.mark.parametrize` to cover multiple error conditions compactly.

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

Use `# pragma: no cover` sparingly and only for these three categories:

1. **`__main__` guard** — The `if __name__ == "__main__": main()` block is exempted by convention:
   ```python
   if __name__ == "__main__":
       main()  # pragma: no cover
   ```

2. **Unreachable defensive code** — Branches that exist only for type narrowing and cannot be triggered in practice:
   ```python
   if result is None:  # pragma: no cover
       raise RuntimeError("unreachable")
   ```

3. **Version-gated fallbacks** — Code paths for older Python versions when the target is py312.

All other branches, error paths, and edge cases must be covered by tests.
If `# pragma: no cover` appears outside these three categories, the test generation should be re-examined rather than the coverage exempted.