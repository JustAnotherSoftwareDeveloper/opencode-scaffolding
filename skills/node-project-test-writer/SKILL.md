---
name: node-project-test-writer
description: "Use when adding or maintaining tests in an existing TypeScript Node.js or Bun project without changing production behavior."
selection:
  role: owner
  tags:
    actions: [change tests]
    inputs: [existing project test suite, behavior contract]
    outputs: [test-only changes, test result report]
    topics: [TypeScript tests, test collection, coverage context]
    environments: [Node.js project, Bun project]
    constraints: [test-only changes, TypeScript-only scope, preserve project conventions]
  use_when:
    - a request asks for test cases, fixtures, helpers, or suite layout changes in an existing TypeScript Node.js or Bun project
  not_for:
    - changing production behavior or repairing a defect revealed by a test
    - a JavaScript-only request, including JavaScript or mixed-language test eligibility
    - changing the repository's scripts/node/ automation or its test suite
    - selecting or changing the test runner, runtime, dependencies, or standalone quality configuration
    - building or validating package artifacts, deployment, or publication
class: operation
---

# Test-Only Change Workflow

Own standalone test changes in existing TypeScript Node.js and Bun projects. The subject is
TypeScript test files, fixtures, helpers, and suite layout in those projects. Standalone
JavaScript test guidance, JavaScript or mixed-language eligibility, JavaScript checking,
and JSDoc typing of `.js` files are excluded. A JavaScript-only request is reported as out
of scope rather than answered with TypeScript guidance. Do not infer a runtime from
TypeScript syntax, a framework name, package manager, or repository path.

Authority covers TypeScript test surfaces plus only the manifests and configuration named
in the authorization. JavaScript source edits are out of scope and are reported as such. A
test-only request does not authorize production source changes.

## Routing Boundaries

- A request to add, change, or repair tests for existing behavior belongs here when no
  production outcome is requested.
- Production behavior and directly coupled regression tests belong to `node-project-writer`.
- Tests for this repository's `scripts/node/` utilities belong to
  `skill-script-node-test-writer`; its Bun conventions are not general project defaults.
- A request whose evidence is a packed artifact or an installed-archive consumer belongs to
  `node-package-distribution`, not to this owner.
- Runner or runtime selection, dependency changes, and standalone quality configuration
  belong to `node-project-dependencies` or `node-quality-workflow`.

## Normalize Input

Identify the target project and suite, behavior contract to verify, requested test outcome,
allowed paths/effects, project runtime(s), and applicable test command. Confirm that the
requested targets are TypeScript test surfaces and that any accompanying manifest or
configuration edit is named in the authorization. Repository access alone does not authorize
edits. Ask before editing when ambiguity could change target, coverage, or scope. If a
request combines test-only and production changes, separate the authorized test-only
portion or ask the requester; do not assume authority to edit production source.

## Procedure

1. **Inspect the existing contract and suite.** Read the relevant source and public behavior contract, tests, fixtures, helpers, suite layout, discovery and filter configuration, runner/runtime versions, setup and isolation rules, and documented commands. Determine the effective project/workspace root and relevant package boundary. Treat current implementation behavior as evidence, not as the test oracle when it conflicts with the stated contract.
2. **Design focused cases.** Cover the requested behavior and relevant boundaries or rejection cases with observable assertions. Assert promised values, state changes, errors, or externally visible effects; do not merely call the subject. Keep setup, cleanup, and mutable state understandable. Use parametrization or shared fixtures only when they preserve independent cases and match project conventions. Do not impose a universal test ratio, assertion count, runner, coverage target, or test layer.
3. **Preserve tool and project boundaries.** Use the existing runner, runtime, configuration, and package scripts. Test transformation or runtime execution is not automatically type checking. Identify which files are discovered, which runtime executes them, and whether a configured check covers tests, imports, or the wider project. Do not change dependencies, lockfiles, runtime selection, runner, coverage settings, quality configuration, or infrastructure as incidental test work.
4. **Edit authorized test files only.** Preserve production files and unrelated tests. If an assertion exposing a production defect is consistent with the contract, retain the mismatch, report it, and stop dependent edits; hand off the behavior change and coupled regression to `node-project-writer`. Do not weaken assertions or alter production source to obtain a pass.
5. **Validate and report.** Review the diff for test-only scope. Check collection for the intended targets when available, then run the authorized project command and applicable existing test-related checks. Record exact commands, target scope, known versions, collected cases, pass/fail/skip outcomes, and whether failures are new or pre-existing. If coverage is relevant, record its measured source set, exclusions, test-file inclusion, metric, configured threshold, report and tool version when known. Do not alter a denominator or invent a gate to improve a percentage.

For runner distinctions, test design, isolation, process-level cases, and a worked coverage-drift diagnosis, see [Test Design And Measurement](reference/test-design-and-measurement.md) and [Collection, Isolation, And Coverage](reference/collection-isolation-and-coverage.md). For the cross-runtime runner and coverage view, see `node-project-reference -> reference/test-execution-and-measurement.md`.

## Self-Validation

- Changes are limited to authorized TypeScript tests, fixtures, helpers, or test layout.
- The intended tests were collected, or collection evidence and its limitation are reported.
- Results identify the actual runner/runtime and test scope without implying untested compatibility.
- Coverage context is reported when applicable; no universal threshold or policy is implied.
- Any production defect remains unmodified and has a bounded handoff to `node-project-writer`.

## Expected Output

Return the authorized test-only change and a concise report of changed paths and cases, collection evidence, exact test/check commands and results, coverage context when applicable, and production defects requiring handoff. Distinguish passed, failed, skipped, unavailable, deferred, and inconclusive work; state any blocker and bounded next step.

## Docs

- [Reference index](reference/README.md) — navigation for this workspace's design and collection pages.
- [Test Design And Measurement](reference/test-design-and-measurement.md) — behavior oracles, mock fidelity, assertion strength, runner and TypeScript boundaries, and evidence handoff.
- [Collection, Isolation, And Coverage](reference/collection-isolation-and-coverage.md) — omitted-test diagnosis, isolation boundaries, CLI and process cases, coverage interpretation, and the coverage-drop diagnosis.
