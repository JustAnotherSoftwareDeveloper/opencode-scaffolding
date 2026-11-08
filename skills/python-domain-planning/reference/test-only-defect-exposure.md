# Test-Only Defect Exposure

> **Authority boundary:** This is a passive workflow document. It describes a scoped
> practice for reference only; it is not an executable procedure or a source of
> execution authority.

`test-only-defect-exposure` - `python-project-test-writer` - Add tests that expose a
production defect without changing production source.

**Use when:** A request asks for test-only changes and the source inspection reveals
production behavior that conflicts with the expected contract.

## Purpose

The test writer documents a contract mismatch within an independently requested
test-only outcome. A failing or diagnostic case provides evidence for a later production
decision without authorizing the fix or weakening the assertion to hide the defect.

## Descriptive Sequence

1. **Test Scope And Expected Contract** — The requested test outcome, existing cases
   and fixtures, and authorized paths define the test-only boundary. Documented or
   established behavior supplies the expectation; implementation alone does not settle
   whether the observed behavior is a defect. An ambiguous expectation remains a
   contract question rather than an invented assertion.
2. **Defect-Demonstrating Case** — A focused case captures inputs, expected behavior,
   and the observed mismatch using existing suite conventions. Collection and relevant
   test results distinguish an assertion failure in the behavior from a fixture,
   environment, or test-setup failure. The evidence remains useful even when a production
   defect prevents a passing result.
3. **Production Handoff** — The test-only report identifies the failing case, exact
   invocation/environment, expected-contract basis, observed behavior, and authorized
   paths changed. A later production request belongs to `python-project-writer`, which
   can use the existing case and owns any directly coupled regression adjustments.
    Without that authorization, the production source remains unchanged.

**Example handoff:** Report the test node, command, environment/runtime, expected-contract
source, observed output, and whether collection succeeded. A behavioral assertion failure
is useful evidence; an import error, fixture failure, or unavailable service is not by
itself proof of the production defect. The writer can later use the case as a regression
test, but only under a production-change request. Pytest fixture and mutable-parameter
behavior can affect reproduction: function-scoped fixtures are the default, broader
scopes reuse state, yield cleanup is not reached if setup fails before yielding, and
parametrized values are not copied. `monkeypatch` restores only the changes it made; it
does not clean arbitrary external state. For these runner-specific details and direct
pytest citations, explicitly load
`python-project-reference -> reference/testing-and-coverage.md`.

## Artifacts

- Test case, fixture, or helper that demonstrates the defect.
- Handoff report of observed versus expected behavior, reproduction conditions, and
  evidence distinguishing a production defect from test/environment failure.
- Optional coverage context if the project already reports it for the changed tests.

## Validation Context

- Collection result for the changed tests.
- Test outcome showing the defect or documenting the expected behavior.
- Clear separation between the test-only evidence and any production change.

## Prerequisites

- An existing Python suite with discoverable conventions and a test runner.
- Authorization for test-only changes only; production edits are out of scope.
- The source behavior and its contract or documented expectation.

## Notes

- Production source, configuration, dependencies, and quality settings remain outside
  the test-only change; an unavailable environment is a blocker, not install permission.
- A request that already asks for a production fix normally fits the
  [brownfield bug fix](brownfield-bug-fix.md), with the fix and directly coupled tests
  owned together. Separate test writing is useful only for an independent test outcome.
- Coverage measures execution within its configured source universe; it does not prove
  the defect is the only failure or that assertions are adequate.

## Operation Handoff

The consuming operation owns the imperative procedure and all execution decisions. It
translates this passive context into its own bounded steps and owns any tools, writes,
delegation, output, and completion validation. This document does not execute, call
tools, modify files, delegate work, load other skills transitively, grant authority, or
establish completion evidence. Any additional reference must be explicitly loaded by the
consuming operation.
