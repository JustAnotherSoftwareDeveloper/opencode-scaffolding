---
name: skill-script-python-test-writer
description: "Use when generating pytest test files for Python scripts under scripts/python/, covering CLI integration tests via CliRunner and unit tests for lib modules."
class: operation
---

# Skill Script Python Test Writer

## Normalize Input

Map invocation context to one internal input object with these required fields:

- **Script name** — Kebab-case entry point name that must already exist under `scripts/python/`.
- **Module structure** — The `lib/` package modules and functions to test.
- **CLI interface** — Click command decorators, arguments, and options for integration tests.
- **Known edge cases** — Empty input, malformed input, boundary conditions relevant to this script.
- **Coverage target** — Defaults to `fail_under = 100` from pyproject.toml.

`BLOCKED: Source script <name> not found — run skill-script-python-writer first.`
`BLOCKED: Shared module <name> not found — create it under src/lib/shared/ first.`
`BLOCKED: Scripts directory not found at scripts/python/.`

## Procedure

Each step is one imperative action.
Do not delegate sub-tasks.

1. **Parse input** — Read the source script files under `src/cli/<name>.py` and `src/lib/<name>/`.
   Extract module structure, public functions, CLI decorators, and known edge cases.
   Identify shared lib dependencies (`from lib.shared.*`) for separate test generation.

2. **Generate unit test file** — Write `tests/test_<script_name>.py` with:
   Direct imports from `lib.<script_name>.<module>`.
   One test function per public function covering nominal and edge-case inputs.
   `tmp_path` fixture for file I/O tests.
   `@pytest.mark.parametrize` for multi-input functions.
   Coverage for error paths and exception handling.

3. **Generate CLI integration test file** — Write `tests/test_<script_name>_cli.py` with:
   `CliRunner`-based tests covering all CLI arguments and options.
   `runner.invoke(main, [args])` pattern.
   Assertions on `exit_code` and `result.output`.
   `isolated_filesystem()` for file-based tests.
   Parameterized error-path tests for non-zero exit conditions.
   Update `tests/conftest.py` if new shared fixtures are needed.

4. **Validate and report** — Run tests, coverage, and lint.
   `uv run pytest --cov --cov-fail-under=100 --tb=short`
   `uv run ruff check tests/test_<script_name>.py tests/test_<script_name>_cli.py`
   On coverage failure, retry once with expanded edge-case tests.
   On second failure, return `PARTIAL` with failing test names and coverage gaps.

## Self-Validation

Each check is a yes/no assertion.

- All generated tests pass (`uv run pytest --tb=short`).
- Coverage meets `fail_under = 100` (`uv run pytest --cov --cov-fail-under=100`).
- No `@pytest.mark.skip` markers exist in generated files.
- Lint passes (`uv run ruff check` on all generated test files).

## Expected Output

Test files under `scripts/python/tests/`:

- `tests/test_<script_name>.py` — Unit tests for `src/lib/<script_name>/` modules
- `tests/test_<script_name>_cli.py` — CLI integration tests for `src/cli/<script_name>.py`
- `tests/conftest.py` — Updated with new shared fixtures if needed

All tests pass, coverage is 100%, no skipped tests, and lint is clean.
