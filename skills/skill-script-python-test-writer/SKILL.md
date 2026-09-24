---
name: skill-script-python-test-writer
description: "Use when creating or editing pytest coverage for existing Python scripts under scripts/python/, including CLI tests, library tests, fixtures, and coverage maintenance."
selection:
  role: owner
  tags:
    actions: [create Python tests, edit Python tests]
    inputs: [existing Python script, existing pytest suite]
    outputs: [pytest test suite]
    topics: [script testing, test maintenance]
    environments: [pytest]
  use_when: [an existing Python script needs new, changed, repaired, or expanded pytest coverage]
  not_for: [changing the Python implementation itself]
class: operation
---

# Skill Script Python Test Writer

Create or edit pytest coverage for one existing Python script under `scripts/python/`.
Own test-only work: adding coverage, repairing stale tests, refactoring test structure,
updating fixtures, and changing expectations to match already-approved implementation
behavior. Do not modify the Python implementation to make the tests pass; implementation
changes belong to `skill-script-python-writer`.

## Normalize Input

Map invocation context to one internal input object. Infer whether tests need to be
created, edited, or both from the repository state.

Capture these fields:

- **Script identity** — Kebab-case entry point name or existing Python script path/name.
- **Requested test result** — Coverage to add, failing/stale tests to repair, or test behavior to change.
- **Module structure** — Existing `lib/` package modules and public functions relevant to the request.
- **CLI interface** — Existing Click command decorators, arguments, options, exit behavior, and output contract when applicable.
- **Existing tests** — Current unit, CLI, fixture, and conftest coverage for the selected script.
- **Known edge cases** — Empty input, malformed input, boundary conditions, regression cases, or failures relevant to the requested result.
- **Coverage target** — Existing project coverage requirement, defaulting to configured `fail_under` behavior.

Read the source implementation and existing tests before editing tests. Treat the
implementation as the behavioral baseline unless the request explicitly identifies an
implementation defect, in which case stop rather than silently changing source code.

`BLOCKED: Source script <name> not found — create or identify the implementation first.`
`BLOCKED: Scripts directory not found at scripts/python/.`

## Procedure

Each step is one imperative action. Do not delegate sub-tasks.

1. **Inspect implementation and existing coverage.** Read the selected CLI and library
   files plus all materially relevant existing tests and fixtures. Identify the exact
   behavior, uncovered paths, stale expectations, duplication, or failing coverage
   that the request requires changing. Follow `./reference/pytest-conventions.md` and
   `./reference/coverage-strategy.md`.

2. **Create or edit unit tests.** Add missing unit-test files or modify existing ones
   under `tests/` as required. Cover nominal behavior, edge cases, error paths, and
   regressions relevant to the requested result. Use direct imports, `tmp_path`,
   `pytest.mark.parametrize`, mocks, and fixtures where appropriate. Preserve useful
   existing coverage and avoid rewriting unrelated tests.

3. **Create or edit CLI integration tests.** Add or modify `CliRunner` coverage when
   the script exposes a CLI. Cover the applicable arguments/options, successful output,
   exit codes, error conditions, and filesystem behavior. Do not require a CLI test
   file for scripts that do not expose a CLI.

4. **Maintain shared test fixtures.** Update `tests/conftest.py` or shared test helpers
   only when the requested test result genuinely needs reusable setup. Preserve
   unrelated fixtures and avoid moving local setup into shared scope without a clear
   reuse benefit.

5. **Validate and remediate.** Run the affected pytest targets, configured coverage
   enforcement, and Ruff checks on changed test files. Remediate test defects within
   the requested test scope. If failures reveal that the implementation itself must
   change, return `BLOCKED` or `PARTIAL` with the implementation mismatch instead of
   editing source code under this operation.

## Validation

Use the strongest applicable checks for the changed test surface:

- `uv run pytest <affected test targets> --tb=short`
- `uv run pytest --cov --cov-fail-under=<configured target> --tb=short` when the project coverage gate applies
- `uv run ruff check <changed test files>`
- Run broader regression tests when the changed fixtures or helpers affect multiple script test suites.

A failed coverage gate should trigger targeted additional coverage when missing tests
are genuinely within scope. Do not add meaningless assertions or weaken configured
coverage to satisfy the number.

## Expected Output

A created or updated pytest suite under `scripts/python/tests/`, limited to files
required by the requested test result. Typical affected files include:

- `tests/test_<script_name>.py`
- `tests/test_<script_name>_cli.py`
- `tests/conftest.py`
- existing shared test helpers when directly relevant

Report which tests were created versus edited, what behavior or regression they cover,
and the validation actually run.

## Self-Validation

- [ ] Source implementation and existing relevant tests were read before editing.
- [ ] Test changes correspond to existing or explicitly requested implementation behavior.
- [ ] Existing useful coverage was preserved unless the request required changing it.
- [ ] Unit, CLI, fixture, and edge-case coverage were added or edited only where applicable.
- [ ] No Python implementation file was modified under this test-only operation.
- [ ] Relevant pytest, coverage, and Ruff checks were run or truthfully reported as blocked.
- [ ] No skipped tests or meaningless assertions were introduced to hide failures.

## Docs

See `./reference/README.md` for the reference file index.
