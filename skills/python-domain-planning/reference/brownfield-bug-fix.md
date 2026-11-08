# Brownfield Bug Fix

> **Authority boundary:** This is a passive workflow document. It describes a scoped
> practice for reference only; it is not an executable procedure or a source of
> execution authority.

`brownfield-bug-fix` - `python-project-writer` - Correct production behavior with
directly coupled regression tests and relevant configured validation.

**Use when:** A request asks to correct observed production behavior in an established
project with existing configuration, compatibility promises, and test conventions.

## Purpose

The production writer owns the fix, its directly coupled regression tests, and the
validation of that bounded change. Existing configuration, compatibility promises,
and test conventions frame the change rather than becoming incidental migration work.

## Descriptive Sequence

1. **Defect Contract** — The observed behavior, reproduction conditions, and documented
   or established expectation identify the mismatch. Supported Python/platform targets,
   public imports, existing tests, and effective quality settings constrain the fix.
   Implementation alone is not an oracle for expected behavior; conflicting expectations
   leave a contract decision unresolved.
2. **Coupled Fix And Regression Evidence** — The writer's bounded change includes the
   smallest production fix and focused tests of that same behavior. Where feasible,
   a failing-before/passing-after case distinguishes the regression from unrelated
   failures. Missing test access or authorization is an evidence gap, not a reason to
   assign another writer implicitly or weaken the expected behavior.
3. **Configured Validation** — The writer's relevant behavior/API tests and applicable
   configured format, lint, and type checks assess the changed paths. Exact invocations,
   versions when known, targets, and outcomes distinguish fixed behavior, pre-existing
   failures, and untested support promises. A separately requested quality report is a
  distinct outcome, not a prerequisite for routine writer validation.

**Example handoff:** Identify the failing input, expected public behavior, supported
runtime, and the test that fails before the fix. The writer changes the smallest
authorized production/test scope, then reports the same test after the fix plus the
actual project-configured checks, paths, versions, and skipped targets. If an unrelated
check was already failing, retain that distinction; do not turn routine validation into
a separate quality assignment or claim an untested support matrix. Compatibility may
include import paths, names, arguments, returns, side effects, exceptions, and subclass
behavior where the project promises them. CPython's own compatibility policy is an
example taxonomy, not a third-party schedule; preserve the project's actual consumer
expectations. For the detailed contract and its publisher references, explicitly load
`python-project-reference -> reference/source-and-api.md`.

## Artifacts

- Reproduction and expected-contract evidence, plus a directly coupled regression case.
- Production source change limited to the authorized behavior.
- Scoped diagnostic report with exact invocations, versions, targets, and results.

## Validation Context

- The regression case exercises the reported mismatch and preserves the intended public
  behavior; a before/after result is identified when available.
- The writer's report identifies changed production/test paths, compatibility
  assumptions, actual test/check results, and skipped or unavailable checks.
- Changed and pre-existing failures remain distinguishable; untested targets remain
  unproven even when local validation passes.

## Prerequisites

- Observed incorrect behavior or a documented contract violation.
- Existing project configuration, test conventions, and supported-range context.
- Authorization covering production and directly coupled test paths, plus the effects
  of validation, including any caches or reports.

## Notes

- A separate `python-project-test-writer` assignment is relevant only to an independent
  test-only outcome, not the fix's directly coupled regression tests.
- `python-quality-workflow` is relevant to a distinct standalone configuration or
  check/report request; routine validation remains with the production writer.
- Unrelated refactoring, style migration, dependency changes, and distribution work
  remain outside the fix.
- A passing static check or test run proves only its actual configured scope, not all
  compatibility or production behavior.
- Coverage evidence includes its source universe, exclusions, branch mode, and any
  configured threshold; it establishes no universal target.

## Operation Handoff

The consuming operation owns the imperative procedure and all execution decisions. It
translates this passive context into its own bounded steps and owns any tools, writes,
delegation, output, and completion validation. This document does not execute, call
tools, modify files, delegate work, load other skills transitively, grant authority, or
establish completion evidence. Any additional reference must be explicitly loaded by the
consuming operation.
