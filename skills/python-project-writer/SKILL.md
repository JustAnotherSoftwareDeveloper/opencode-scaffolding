---
name: python-project-writer
description: "Use when changing production behavior in an existing Python application, service, internal package, or library."
selection:
  role: owner
  tags:
    actions: [change production behavior]
    inputs: [Python project, behavior change request]
    outputs: [implemented behavior, validated change report]
    topics: [production Python source, directly coupled regression tests]
    environments: [Python application, Python service, Python package, Python library]
    constraints: [bounded authorized changes, preserve compatibility]
  use_when:
    - a request asks to implement or modify production behavior in a Python project
  not_for:
    - a request asks only to add, change, or repair tests without changing production behavior
    - a request asks for standalone quality configuration or check/report work
    - a request asks to choose or change dependencies, environments, or locks
    - a request asks to build or change distribution artifacts, publish, or deploy
class: operation
---

# Production Behavior Change Workflow

Change production behavior in a Python application, service, internal package, or
library, including directly coupled regression tests. Standalone test, quality,
dependency/environment, distribution, publishing, and deployment outcomes remain separate.

## Normalize Input

Identify the target project, intended observable behavior, compatibility constraints,
and authorized paths and effects. Ask before editing if these are materially ambiguous;
repository access alone grants no permission. Stop any effect that needs additional
authorization or an unresolved project-policy decision.

## Procedure

1. **Inspect the affected behavior.** Trace implementation, callers, public imports,
   documented and typed interfaces, supported Python/platform versions, environment
   assumptions, and relevant runtime, security, and reliability constraints. Read the
   necessary project guidance; use topic references under Docs when needed. Keep
   repository `scripts/python/` conventions local to that tree.
2. **Choose and bound the change.** Preserve existing configuration and compatibility
   promises first, approved local policy next, and proposed defaults only for new or
   unconfigured projects when choice is permitted. Surface conflicts rather than
   silently migrating. Before writing, state the smallest production/test edits,
   compatibility impact, and permitted checks. Do not add unrelated refactoring,
   infrastructure, configuration, dependency, lock, or delivery changes.
3. **Verify version-sensitive details.** Ground syntax, APIs, and commands in permitted
   target-project/version evidence. Obtain separate scoped authorization before
   checking current external primary documentation. Record exact source, applicable
   version, access context/date, and limits; snapshot hashes do not prove freshness.
   If evidence, access, or authorization is missing, name the affected detail and
   needed source/version, defer it as non-executable, and give a bounded authorized
   refresh handoff.
4. **Implement the behavior and coupled regressions.** Preserve unaffected names,
   imports, interfaces, supported versions, and local conventions. Keep sensitive
   values out of source, test output, logs, and reports. If a necessary change or
   command effect exceeds scope, stop that effect and identify the needed owner or
   authorization.
5. **Validate the changed outcome.** Run relevant configured behavior/API tests and
   applicable formatting, lint, and type checks when authorized and available. Use
   project commands and targets, not a universal gate; prefer non-writing checks
   unless writes are authorized. Record exact commands, versions when known, targets,
   and results. Separate new failures from pre-existing ones without repairing
   unrelated findings; identify skipped, unavailable, deferred, or inconclusive checks.

## Self-Validation

- The diff contains only authorized production changes and directly coupled tests.
- Every claimed result is supported by checks of that actual scope; untested
  compatibility, security, policy approval, and deployment are not implied.

## Expected Output

Return the change and a concise report of observable behavior, production/test paths,
compatibility assumptions, exact validation evidence, and remaining gaps. If blocked
or unchanged, state why and the bounded next step.

## Docs

- [Change design and validation](reference/change-design-and-validation.md) — compatibility,
  failure boundaries, regression cases, and scoped validation.

For domain context, explicitly load the named documentation skill before reading a
relevant module. These references are passive: they grant no effects, project policy,
or validation evidence.

- `python-project-reference -> reference/project-context-and-layout.md` — layout and
  compatibility promises.
- `python-project-reference -> reference/source-and-api.md` — public/typed interfaces
  and failure contracts.
- `python-project-reference -> reference/testing-and-coverage.md` — regression evidence.
- `python-project-reference -> reference/static-quality.md` — configured static checks.
- `python-project-reference -> reference/environment-and-dependencies.md` — interpreter
  and resolved-environment context.
- `python-project-reference -> reference/secure-configuration-and-data-handling.md` —
  secrets and sensitive data.
- `python-project-reference -> reference/logging-and-observability.md` — log/context records.
- `python-project-reference -> reference/async-and-concurrency.md` — task, thread,
  process, synchronization, and shutdown behavior.
- `python-project-reference -> reference/distribution-artifacts.md` — existing consumer
  installation contracts, not artifact production.
- `python-source-style-guide -> reference/python-source-style-guide.md` — source conventions.
