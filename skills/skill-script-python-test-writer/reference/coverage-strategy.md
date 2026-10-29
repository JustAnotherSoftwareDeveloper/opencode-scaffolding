# Coverage Strategy

## Measurement Policy

Measure line coverage with `pytest-cov`. Require exactly 100% line coverage across the
complete set of tests classified as `unit`. Do not set a numeric branch-coverage
threshold or describe line coverage as proof that every branch, path, input, or assertion
is correct. Exercise relevant branch outcomes when needed to execute in-scope lines.

## Fixed Production-Source Denominator

Include every maintained Python production module beneath both `scripts/python/src/cli/`
and `scripts/python/src/lib/`, including nested packages, shared modules, executable
package initializers, registered and unregistered CLI modules, and the flat
`src/cli/agent_eval_suite.py`. Measure the complete roots, not only files changed by a
task, imported by selected tests, or named in a hand-picked file list.

Test modules, fixtures, dependencies, virtual environments, caches, build outputs, and
non-package data are outside this production-source denominator. Do not use a module
omission or report filter to remove maintained production code.

## Unit-Only Selection And Gate

Classify every test as exactly one of `unit` or `integration`. The effective pytest
collection must reject a missing or double classification. A unit run selects the
complete set classified as `unit`; do not narrow it by path, keyword, changed file,
ignore option, or another marker. `CliRunner`, console-entry-point, subprocess, and
workflow execution are integration tests and never contribute to the unit result.
Direct calls to isolated CLI callbacks or helpers may be unit tests. Tests need not
import `lib.*` directly.

Use a fresh `.coverage.unit` data file, measure both `cli` and `lib`, print missing
lines, and fail below 100%. Do not append or combine other run data. The approved
project-context command shape is:

```sh
COVERAGE_FILE=.coverage.unit uv run pytest -c pyproject.toml -o addopts= tests -m unit \
  --cov=cli --cov=lib --cov-config=pyproject.toml \
  --cov-report=term-missing --cov-fail-under=100
```

This command specifies the approved gate shape; the guidance itself is not evidence that
project configuration or CI already enforces it.

The approved configuration must set the unit line threshold to 100% and reject
unclassified or doubly classified tests; the command must also specify
`--cov-fail-under=100`. Keep `--cov-branch` off for this gate. Do not use
`--cov-append`, `--no-cov`, suppression markers, changed-test selection, reduced source
roots, or a mixed-suite configuration that can satisfy the unit result. Run from the
Python project context with the effective configuration explicitly selected.

If the first complete unit run is below 100%, add targeted tests for supported,
in-scope behavior and rerun the complete unit selection. This second run is the only
retry. If the second run still fails, report `PARTIAL` with failing tests, measured coverage
when available, and remaining gaps. Never lower the target or claim success from a
partial selection.

## Separate Full-Suite Result

Run the complete suite, including both unit and integration tests, as a distinct
full-suite aggregate only when that result is required. Give it fresh `.coverage.full`
data, its own source and test selection, report, threshold, label, and status. Keep the
accepted existing 85% aggregate, if retained, as a separate compatibility gate. Never
label the aggregate unit coverage, append or combine its data with `.coverage.unit`, or
use it to replace or satisfy the 100% unit gate. Integration execution can raise the
aggregate without adding unit execution; the two results must remain independent.

## Effective Exclusion Audit

Audit the complete effective exclusion behavior of the locked coverage.py version,
including built-in defaults, project configuration patterns, and source-level markers.
The accepted policy is based on coverage.py 7.14.3. Neutralize every built-in default
that silently removes maintained production lines from the unit denominator, including
the `TYPE_CHECKING` and ellipsis (`...`) exclusions. Re-audit defaults if the locked
coverage.py version changes.

Do not apply blanket exclusions to `TYPE_CHECKING` blocks, Protocol classes, abstract
methods, `agent_eval_suite.py`, or any other module or production-code category. A
category-wide or wildcard exclusion is not authorized. Reportable lines that remain
after the permitted line-local exceptions below stay in the denominator and must be
executed by unit tests.

Permit only these individually justified line-local `# pragma: no cover` exceptions,
when their conditions hold:

- **`__main__` dispatch:** Exempt only the dispatch line when its underlying CLI
  behavior is covered by unit tests.
- **Unreachable defensive code:** Exempt only a defensive line proven unreachable by
  supported-input and dependency contracts. A type annotation or untested assumption
  is not evidence; test a path that can occur.
- **Out-of-runtime fallback:** Exempt only a fallback for a Python version outside the
  declared supported runtime. Test fallbacks for supported versions.

Each exception must be narrowly located and have a reviewable local rationale. Any
exception to neutralizing a built-in exclusion form also requires the requesting user's
explicit authorization for that specific location. A `# pragma: no cover` does not turn
integration execution into unit coverage. No maintained production module may be
omitted to compensate for exclusions.

## Test-Quality Guardrails

Coverage measures execution, not whether assertions would catch incorrect behavior.
Assert the supported contract with expected values, state or file effects, relevant
exceptions, and other observable outcomes; do not merely call code. Select nominal,
boundary, and reachable error cases from the implementation's supported behavior.
Preserve independent tests and use appropriate temporary files or controlled fakes.
Review assertion relevance and missing-line evidence separately from the percentage.
Do not invent unsupported scenarios or add execution-only tests solely to raise
coverage.

## Case Selection Prompts

Use these cases only when the selected production code accepts, handles, or distinguishes
them. They are prompts, not a universal checklist:

- **Inputs:** Empty, whitespace-only, single-element, or maximum-size input when
  supported limits or handling make the case relevant.
- **File I/O:** Missing paths, directories, unreadable files, encoding, BOM, or symlinks
  when the contract distinguishes those cases.
- **CLI callable logic:** Missing arguments, invalid options, help, or extra arguments
  when direct-call behavior can exercise the relevant production lines. Click parsing
  and command invocation remain integration coverage.
- **Errors:** Malformed input, dependency failures, and other reachable handled errors.
  Exercise only behavior the implementation actually handles.
- **Outputs and boundaries:** Zero, one, or multiple results; special characters; and
  boundary values when they exercise distinct supported behavior.

## Error-Path Testing

Test each reachable, in-scope error-handling path that is part of supported behavior
and contributes lines to the fixed denominator. Do not require irrelevant error cases.
Use `pytest.mark.parametrize` when it expresses multiple applicable conditions clearly.

```python
import pytest


@pytest.mark.unit
@pytest.mark.parametrize(
    "value, expected",
    [
        ("", 0),
        ("hello world", 2),
    ],
)
def test_count_tokens(value, expected):
    assert count_tokens(value) == expected
```
