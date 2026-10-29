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

# Write Focused Pytest Coverage

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
- **Coverage target** — The complete maintained production-source denominator and 100% unit-only line target in `./reference/coverage-strategy.md`; do not reduce the denominator or defer to a lower target.

Read the source implementation and existing tests before editing tests. Treat the
implementation as the behavioral baseline unless the request explicitly identifies an
implementation defect, in which case stop rather than silently changing source code.

`BLOCKED: Source script <name> not found — create or identify the implementation first.`
`BLOCKED: Scripts directory not found at scripts/python/.`

Replace `<name>` in the first blocked message with the script name recorded under
**Script identity** before returning that message.

## Procedure

Each step is one imperative action. Do not delegate sub-tasks.

1. **Inspect implementation and existing coverage.** Read the selected CLI and library
   files plus all materially relevant existing tests and fixtures. Identify the exact
   behavior, uncovered paths, stale expectations, duplication, or failing coverage
   that the request requires changing. Follow `./reference/pytest-conventions.md` and
   `./reference/coverage-strategy.md`.

2. **Create or edit unit tests.** Add missing unit-test files or modify existing ones
   under `tests/` as required. Call production behavior directly, including CLI
   callbacks or helpers when they bypass Click invocation and isolate external effects.
   A unit test may reach library behavior through a CLI callable path; a direct
   `lib.*` import is not mandatory. Assert the observable contract, including relevant
   values, state or file effects, and expected exceptions. Preserve useful existing
   coverage and avoid rewriting unrelated tests.

3. **Classify every test exactly once.** Give each collected test exactly one effective
   `unit` or `integration` classification. Collection must reject a test with neither
   classification or both. Keep direct-call tests that isolate production behavior in
   the unit class; classify `CliRunner`, console-entry-point, subprocess, and workflow
   execution as integration. A workflow that combines modules or systems is
   integration even when it also exercises unit-level behavior.

4. **Create or edit CLI integration tests.** Add or modify `CliRunner` coverage when
   the script exposes a CLI. Cover applicable argument parsing, successful output, exit
   codes, error conditions, and filesystem behavior. Do not require a CLI test file for
   scripts that do not expose a CLI. Integration execution never contributes to the
   unit-only coverage result.

5. **Maintain shared test fixtures.** Update `tests/conftest.py` or shared test helpers
   only when the requested test result genuinely needs reusable setup. Preserve
   unrelated fixtures and avoid moving local setup into shared scope without a clear
   reuse benefit.

6. **Validate and remediate.** Run the complete unit classification against every
   maintained production module under `src/cli/` and `src/lib/` with the required 100%
   line-only gate. Run the full suite separately with its own coverage data and result;
   do not combine its execution with, append it to, or substitute it for unit coverage.
   Run Ruff checks on changed test files. Remediate test defects within the requested
   test scope. If failures reveal that the implementation itself must change, return
   `BLOCKED` or `PARTIAL` with the implementation mismatch instead of editing source
   code under this operation.

## Validation

Use the strongest applicable checks for the changed test surface:

Replace `<affected test targets>` with the relevant paths and `<changed test files>`
with the concrete modified test files. The affected-test command is a focused diagnostic,
not a substitute for the complete unit-only gate. Use the approved project configuration
for the gate; its command shape is shown below and must run from `scripts/python/`.

- `uv run pytest <affected test targets> --tb=short`
- `COVERAGE_FILE=.coverage.unit uv run pytest -c pyproject.toml -o addopts= tests -m unit --cov=cli --cov=lib --cov-config=pyproject.toml --cov-report=term-missing --cov-fail-under=100`
- `uv run ruff check <changed test files>`
- Run broader regression tests when the changed fixtures or helpers affect multiple script test suites.

The unit gate selects every test classified as `unit`, measures all maintained `cli`
and `lib` production modules, and uses fresh `.coverage.unit` data. Do not filter the
unit set by path, keyword, changed file, ignore option, or marker beyond the complete
`unit` class. Run any retained full-suite aggregate separately with fresh `.coverage.full`
data, its own report and status, and a separately defined threshold (the accepted policy
keeps the existing 85% aggregate as a distinct compatibility gate). Never call that
aggregate unit coverage. When the unit gate reports gaps, add targeted tests only for
supported behavior within the fixed denominator, then rerun the complete unit gate. Do
not add meaningless assertions, omit modules, or weaken the 100% line threshold.

## Expected Output

A created or updated pytest suite under `scripts/python/tests/`, limited to files
required by the requested test result. Typical affected files include:

Replace `<script_name>` in these illustrative filenames with the selected script name
from **Script identity** before creating or reporting a test file. The listed paths are
relative to `scripts/python/`. Keep `_cli` for the CLI test filename.

- `tests/test_<script_name>.py`
- `tests/test_<script_name>_cli.py`
- `tests/conftest.py`
- existing shared test helpers when directly relevant

List the tests created versus edited, the behaviors or regressions they cover, and the
validation actually run in your report.

## Self-Validation

- [ ] Source implementation and existing relevant tests were read before editing.
- [ ] Test changes correspond to existing or explicitly requested implementation behavior.
- [ ] Existing useful coverage was preserved unless the request required changing it.
- [ ] Every test has exactly one effective `unit` or `integration` classification; missing or double classifications are rejected.
- [ ] Unit tests use direct calls, including callable CLI logic where appropriate; `lib.*` imports are not mandatory.
- [ ] All maintained `src/cli` and `src/lib` production modules remain in the 100% unit line denominator; no branch threshold is substituted.
- [ ] CLI entry-point and workflow integration coverage is separate from the complete unit-only run and its data.
- [ ] Assertions check supported behavior rather than merely executing code.
- [ ] No Python implementation file was modified under this test-only operation.
- [ ] Relevant pytest, coverage, and Ruff checks were run or truthfully reported as blocked.
- [ ] No skipped tests, module omissions, coverage exclusions, or meaningless assertions were introduced to hide failures.

## Docs

See `./reference/README.md` for the reference file index.
