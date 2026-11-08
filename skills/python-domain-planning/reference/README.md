# Workflow Reference Index

These six practices distinguish outcomes and the evidence needed between them.
Their sequences describe the work; the selected operation supplies the executable
procedure and completion judgment.

## Choosing and handing off

Start with the requested outcome, not the filename likely to change. One request may
need multiple owners, but each owns only its outcome: dependency decisions/effects,
production behavior, standalone tests, quality configuration/checks, and distribution
artifacts do not merge merely because they touch `pyproject.toml` or share validation.
Make sequencing explicit when one result is a prerequisite. A handoff should name the
changed paths and authorized effects, exact evidence and its scope, assumptions,
unresolved risks, and the next decision; it is not a completion claim for the next
owner. Proposed defaults are nonbinding: preserve existing compatibility and
configuration first, apply approved local policy where applicable, and use a proposed
choice only for a new or unconfigured project when the request permits choosing. A
declared support range, selected interpreter, resolved lock, installed environment, and
tested target describe different evidence; none substitutes for the others. The linked
project-reference documents explain those distinctions in the relevant workflows.

## Workflow Choices

- [Feature with new dependency](feature-with-new-dependency.md) applies when a requested
  behavior may need a missing package. The dependency decision and authorized effects
  supply the writer's capability, version, and environment assumptions.
- [Brownfield bug fix](brownfield-bug-fix.md) keeps a production correction and its
  directly coupled regression tests with one writer. Reproduction and configured
  validation connect the defect to the claimed fix.
- [Test-only defect exposure](test-only-defect-exposure.md) applies when only test
  changes are authorized. A contract-based failing case and reproduction report support
  a separate production decision without authorizing it.
- [Dependency evaluation](dependency-evaluation.md) supports a decision or bounded
  dependency/environment effect without requiring a feature change. Evidence and
  authorization remain separate even when the recommendation is add or replace.
- [Library distribution](library-distribution.md) connects delivery promises to archive
  contents and clean install results. Checkout tests alone do not establish the
  consumer artifact's usability.
- [Scoped quality check](scoped-quality-check.md) distinguishes check-only reporting
  from requested quality configuration. Effective settings, exact diagnostic scope,
  and write status establish what the report actually assessed.

## Reference Context

Reliance on another skill's guidance requires its explicit load through the skill
tool and an explicit read of the needed document. The destinations below identify
context, not operation assignments, transitive loads, or permission to change state.
An unavailable required reference remains an evidence gap for the consuming operation.

- `python-project-reference -> reference/project-context-and-layout.md` covers
  project shape, import boundaries, and declared versus selected versus tested support.
- `python-project-reference -> reference/source-and-api.md` covers public behavior
  and failure contracts for feature, fix, and defect-test expectations.
- `python-project-reference -> reference/testing-and-coverage.md` covers suite
  behavior and coverage interpretation; it does not require a separate test writer.
- `python-project-reference -> reference/static-quality.md` covers effective
  formatter/linter/type-checker settings and the limits of diagnostic evidence.
- `python-project-reference -> reference/environment-and-dependencies.md` covers
  dependency roles, manager state, lock consistency, and evaluation context.
- `python-project-reference -> reference/distribution-artifacts.md` covers metadata,
  archive contents, and checkout-versus-installed behavior.
- `python-project-reference -> reference/secure-configuration-and-data-handling.md`,
  `python-project-reference -> reference/logging-and-observability.md`, and
  `python-project-reference -> reference/async-and-concurrency.md` cover sensitive
  data, observability, and concurrency constraints when the changed behavior needs them.
- `python-source-style-guide -> reference/python-source-style-guide.md` is the hub
  for names/imports, readable layout/control flow, functions/classes/state,
  comments/docstrings, and annotations. Its conventions do not authorize a public API
  rename, configuration migration, or unsupported syntax upgrade.
