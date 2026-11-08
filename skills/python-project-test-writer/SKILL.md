---
name: python-project-test-writer
description: "Use when adding or maintaining tests, fixtures, helpers, or test layout in an existing Python project without changing production behavior."
selection:
  role: owner
  tags:
    actions: [change tests]
    inputs: [existing Python suite, source-observed behavior, coverage configuration]
    outputs: [validated test-only changes, test result report]
    topics: [Python tests, test collection, coverage context]
    environments: [Python application, Python service, Python package, Python library]
    constraints: [test-only changes, preserve project conventions]
  use_when:
    - "a request asks for test-only changes to an existing Python suite: cases, fixtures, helpers, or layout"
  not_for:
    - a request asks to change production behavior, even when regression tests are also needed
    - a request asks only for standalone quality configuration, checks, or reports
    - a request concerns the repository's scripts/python/ automation workflow
class: operation
---

# Test-Only Change Workflow

Change cases, fixtures, helpers, or layout in an existing Python test suite without
changing production source. Production-behavior changes and their directly coupled
regressions belong to `python-project-writer`; this operation owns standalone test-only work.

## Normalize Input

Identify the project/suite, behavior to verify, requested test outcome, and authorized
paths/effects. Ask before editing if these are materially ambiguous; repository access
alone grants no permission. For mixed requests, isolate the authorized test-only part
or ask if separation would change the result. Standalone quality, dependency/environment,
distribution, publishing, and deployment outcomes remain separate. Keep `scripts/python/`
automation and its conventions with the script-specific workflow.

## Procedure

1. **Inspect the suite and behavior contract.** Read relevant source, cases, fixtures,
   helpers, discovery/layout rules, runner configuration, collection/test commands,
   and applicable checks and versions. An implementation detail alone is not the test
   oracle. If coverage informs the task, inspect its effective measurement context
   before choosing cases or interpreting a percentage.
2. **Design focused cases.** Cover the requested contract, boundaries, and relevant
   failures with observable expected outcomes: assert returned values or state changes,
   and assert documented rejection behavior rather than merely calling the code. Reuse
   fixtures/helpers for understandable setup and cleanup; avoid order dependence and
   shared mutable state. Parametrize cases only when their structure genuinely fits.
   Preserve project configuration and
   compatibility first, approved local policy next, and proposed defaults only where
   choice is permitted for new or unconfigured projects. Surface conflicts; impose no
   universal framework, taxonomy, assertion count, test ratio/total, or coverage target.
3. **Verify version-sensitive tooling.** Use the project's documented commands and
   resolved versions, not flags inferred from reference examples. Obtain separate
   scoped authorization before checking current external primary documentation;
   record exact source, applicable version, access context/date, and limits. Hashes
   do not establish freshness. If evidence, access, or authorization is missing, name
   the affected detail and needed source/version, defer it as non-executable, and
   give a bounded authorized refresh handoff.
4. **Edit only authorized tests.** Preserve production files and unrelated tests.
   Do not incidentally migrate frameworks/layout, add infrastructure or dependencies,
   or change locks, runtime, runner, coverage, or standalone quality configuration. If tests
   expose a production defect, record observed behavior and the conflicting contract;
   neither repair production source nor weaken assertions to hide it. Stop dependent
   edits and hand the production change and coupled regression to `python-project-writer`.
5. **Validate collection and outcomes.** Review the diff, validate collection for the
   relevant targets, then run authorized configured tests and applicable test-related
   checks. Do not invent a gate, broaden the suite without authorization, or repair
   unrelated failures. Record exact commands, targets, versions when known, and
   results; distinguish new failures from pre-existing ones.

   For practical case patterns, fixture cleanup, isolation limits, and coverage
   interpretation, see [Test design and isolation](reference/test-design-and-isolation.md).

   For coverage, record the measured source universe/denominator, test-file inclusion,
   line/branch mode, exclusions, configured threshold, report artifact, and tool
   version when known. Say when coverage was not run. Passing tests cover only collected
   cases and assertions; coverage measures execution, not oracle completeness or defect detection.

## Self-Validation

- The diff is test-only and respects the authorized paths and existing suite contract.
- Reported results identify actual collection/assertion scope and measurement context,
  without implying untested compatibility or policy approval.

## Expected Output

Return the test-only change and a concise report of changed paths/cases, collection,
exact test/check evidence, coverage context when applicable, and production defects
for handoff. Distinguish passed, failed, skipped, unavailable, deferred, and inconclusive
work; state any blocker and bounded next step.

## Docs

- [Test design and isolation](reference/test-design-and-isolation.md) — behavior cases,
  fixtures, state isolation, and interpretable coverage.

Explicitly load the named documentation skill before reading a relevant module below.
References supply passive context, not permissions, project policy, or completion evidence.

- `python-project-reference -> reference/testing-and-coverage.md` — test design and
  measurement context.
- `python-project-reference -> reference/project-context-and-layout.md` — placement
  and imports.
- `python-project-reference -> reference/source-and-api.md` — public/typed contracts.
- `python-source-style-guide -> reference/python-source-style-guide.md` — test/helper
  source conventions.
