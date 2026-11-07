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

Own one bounded test-only change to an existing Python suite in an application,
service, internal package, or library. This operation may change test cases, fixtures,
test helpers, or test-suite layout. It never changes production source. It owns its
inspection, permitted test edits, validation, and result report; passive references
provide context only.

## Normalize Input

Identify the requested test outcome, target project and suite, authorized paths and
effects, and relevant behavior to verify. Confirm that the request is test-only. If the
behavior, project, scope, or permission is materially ambiguous, ask a focused question
before editing. Do not infer permission from repository access or a nearby file.

Keep ownership aligned with the requested outcome:

- Route a requested production-behavior change, including a directly coupled regression
  test, to `python-project-writer`.
- Route standalone quality configuration or check/report work to
  `python-quality-workflow`.
- Keep dependency, environment, distribution, publishing, and deployment outcomes with
  their respective owners; do not take them on as incidental test work.
- Keep `scripts/python/` automation with its script-specific workflow. Its local
  conventions, coverage markers, and gates are not defaults for other Python projects.

If the request combines separately owned outcomes, identify the split and complete only
the authorized test-only part. Pause and ask for direction if that split changes the
requested result or cannot be performed safely in isolation.

## Procedure

1. **Inspect the existing suite and project constraints.** Read only the project and
   test files needed to understand the target behavior, current cases, fixtures,
   helpers, discovery/layout conventions, test runner, and relevant test configuration.
   Inspect the source behavior and its documented or otherwise established contract;
   do not treat an implementation detail alone as the expected behavior. Identify the
   configured collection and test commands, relevant tool versions when available, and
   any checks normally required for the changed tests.

   Preserve existing project configuration and compatibility promises first, then
   applicable approved local policy, then proposed defaults only for a new or
   unconfigured project when the task permits a choice. Do not switch frameworks,
   migrate test layout, alter test-runner or coverage configuration, add dependencies,
   or introduce a new testing policy as an incidental change. If project requirements
   conflict or require an unresolved policy choice, stop and ask the responsible owner.

   When coverage informs the task or is run, inspect the effective source set and report
   context: which files may be measured, whether tests are included, configured
   exclusions, and line or branch measurement. A percentage without its measured source
   universe is not an interpretable coverage result.

   Load passive reference material selectively and only when it materially helps:

   - `python-project-reference -> reference/testing-and-coverage.md` for test-design
     and coverage-measurement context.
   - `python-project-reference -> reference/project-context-and-layout.md` for project
     shape, test placement, and import/layout context.
   - `python-project-reference -> reference/source-and-api.md` when the behavior under
     test depends on an established public or typed interface contract.
   - `python-source-style-guide -> reference/python-source-style-guide.md` when general
     source conventions materially affect test code or helpers.

   These references are passive and non-transitive. They do not authorize edits, select
   a project's policy, add a workflow, or establish validation or completion evidence.

2. **Choose focused behavior evidence.** Derive cases from the requested behavior,
   project contract, and relevant boundaries or failure outcomes. Make the behavior and
   expected result clear in each test. Reuse fixtures and helpers where they make setup,
   cleanup, or shared intent clearer; keep test state bounded and avoid accidental
   order-dependence or shared mutable state. Use parametrization only when the cases
   genuinely share a useful structure. Do not impose a universal assertion count, test
   taxonomy, unit/integration ratio, test total, coverage target, or required framework.

   A passing test run is evidence only for the collected cases and their actual
   assertions; it does not establish that the test oracle is complete or that all
   requirements are met. Coverage measures execution within a configured source
   universe, not assertion adequacy or defect-detection effectiveness. (TEST2 C01-C08;
   TQ C01-C12.)

3. **Make only authorized test edits.** Change only the approved test cases, fixtures,
   test helpers, or suite-layout paths. Follow the existing suite's conventions and
   preserve unrelated tests and production files. Do not change application code,
   shared runtime configuration, dependencies, locks, coverage settings, or standalone
   quality-tool configuration.

   If inspection or a test exposes a mismatch between expected and actual production
   behavior, do not change production source or weaken the assertion to hide it. Record
   the observed behavior and the contract or expectation it conflicts with; route the
   production change and any directly coupled regression test to
   `python-project-writer`. Stop test-only edits that depend on resolving that defect.

4. **Validate collection and relevant outcomes.** Review the diff to confirm that all
   changes are within authorized test paths and contain no production edits. Use the
   project's documented, configured test tooling and version context; do not invent a
   universal command, add a gate, or run a broader suite without authorization.
   Validate collection for the changed or otherwise relevant targets, then run the
   relevant tests and any existing test-related checks that are authorized and apply to
   those changes. Distinguish failures caused by the edits from pre-existing failures.
   Do not repair unrelated findings or take on a standalone quality-workflow outcome.

   For every coverage result, record the measured source universe or denominator,
   whether test files are included, line or branch mode, known exclusions, any
   configured threshold, the report artifact, and relevant tool versions when known.
   Report coverage as configured execution measurement, not proof of correctness. If
   coverage was not run, say so rather than implying a result.

   For version-sensitive command syntax or tool behavior, rely on the target project's
   documented command and resolved version. If current external documentation is
   needed, obtain separate scoped authorization before fetching or checking it. Do not
   prescribe unverified flags or infer target versions from reference examples. If the
   necessary detail is unavailable, identify the exact command or behavior and
   required tool/version, mark it deferred and non-executable, and request a bounded
   authorized check of the relevant current primary documentation. Record any such
   evidence's exact source, version, access context/date, and limits; a copied-source
   hash does not establish freshness.

5. **Report the outcome.** State the test-only objective and result; changed test paths;
   cases, fixtures, helpers, or layout added or changed; collection targets and result;
   exact commands, targets, versions when known, and results for tests and checks run;
   and any failures, unavailable checks, or evidence gaps. If coverage was reported,
   include its source universe/denominator, test-file inclusion, line or branch mode,
   exclusions, threshold if configured, and report artifact. Identify any production
   defect for the production owner without changing its source. Clearly distinguish
   passed, failed, skipped, unavailable, and deferred work. Do not claim a broader
   compatibility matrix, policy approval, or untested result.

## Evidence Scope

The evidence supports test-runner and coverage-tool mechanics, not comparative test
effectiveness or universal project policy. Research identifiers are retained here:
`TEST2` is the targeted pytest/coverage.py source set inspected on 2026-11-05; `TQ` is
the earlier pytest/coverage.py/pytest-cov source set inspected on 2026-11-04. The
provenance record `python-project-reference -> reference/testing-and-coverage.md`
records a scoped check of official tagged primary documentation on 2026-11-06: pytest
9.2.0 fixture, parametrization, and reference pages, and coverage.py 7.17.2 source,
branch, exclusion, and configuration pages. Those versions and dates describe the
cited evidence only; they do not establish a target project's installed versions or
effective configuration. This workflow intentionally prescribes no version-specific
runner or coverage command.

- Pytest: [test anatomy](https://docs.pytest.org/en/stable/explanation/anatomy.html),
  [fixtures at 9.2.0](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/fixtures.rst),
  [parametrization at 9.2.0](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/how-to/parametrize.rst),
  and [reference at 9.2.0](https://github.com/pytest-dev/pytest/blob/9.2.0/doc/en/reference/reference.rst).
  Relevant claims include test anatomy and assertion limits (TEST2 C01; TQ C01-C02),
  fixture/isolation scope (TEST2 C02; TQ C03-C05), and parametrization (TEST2 C03;
  TQ C05).
- Coverage.py: [source selection at 7.17.2](https://coverage.readthedocs.io/en/7.17.2/source.html),
  [branch measurement at 7.17.2](https://coverage.readthedocs.io/en/7.17.2/branch.html),
  [exclusions at 7.17.2](https://coverage.readthedocs.io/en/7.17.2/excluding.html),
  and [configuration at 7.17.2](https://coverage.readthedocs.io/en/7.17.2/config.html).
  Relevant claims include source scope and denominator (TEST2 C04-C05; TQ C08),
  branch-mode interpretation (TEST2 C06; TQ C07), and threshold limits (TEST2 C07-C08;
  TQ C08, C12).

The pytest test-anatomy stable page was inspected on 2026-11-05, but its individual
page version was not surfaced. The tagged pytest pages and coverage.py 7.17.2 pages
above were accessed on 2026-11-06. Stable/latest documentation is mutable, and none of
these observations implies compatibility with a target project. The source sets do not
establish a Python-specific test-effectiveness estimate, mandatory coverage threshold,
or enterprise policy.

## Self-Validation

- The request is limited to test-only changes in an existing Python suite.
- Only authorized test cases, fixtures, helpers, or suite-layout paths are changed; no
  production behavior, dependencies, or standalone configuration is modified.
- Existing project configuration and compatibility promises take precedence over
  approved local policy and proposed defaults.
- Collection and relevant configured test/check outcomes are validated and reported
  with their actual targets and results.
- Any coverage result includes its source universe/denominator, test-file inclusion,
  measurement mode, exclusions, and configured threshold when applicable.
- A discovered production defect is reported and routed without changing production
  source.
- Passive references are explicitly loaded only when relevant and add no authority or
  transitive workflow.
- Version-sensitive details use target-project evidence or are explicitly deferred
  with a bounded authorized refresh handoff.
- The result report distinguishes passed, failed, skipped, unavailable, and deferred
  work without claiming untested outcomes or universal policy.
- Filled content uses semantic prose forms and contains no Markdown table.

## Expected Output

One bounded test-only change to an existing Python suite and a report containing the
changed test paths, collection/test/check results, and coverage context when applicable.
If a production defect is found, do not change production source; report it to
`python-project-writer`. If scope, authorization, or evidence blocks the test-only work, make no unauthorized edit and report the specific blocker and bounded next step.
