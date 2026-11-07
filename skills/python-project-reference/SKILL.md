---
name: python-project-reference
description: "Use when Python project context is needed for compatibility, layout, tooling, testing, dependencies, distribution, security, logging, or concurrency decisions."
selection:
  role: reference
  tags:
    actions: [reference, explain]
    inputs: [Python project context]
    outputs: [project guidance]
    topics: [project compatibility, project structure, project tooling]
    environments: [Python application, Python service, Python package]
    constraints: [passive, no side effects]
  use_when:
    - a request needs one or more project-level Python reference topics
  not_for:
    - a request asks to change Python source, tests, configuration, or distribution artifacts
    - a request is specifically about general naming, imports, docstring form, or annotation style
class: documentation
---

# Python Project Context Reference

Use this reference to reason about Python project constraints, tool behavior, and
common failure modes. Examples are explanatory; no target project has been inspected
or executed here.

This reference is passive: it does not make a project's decision, authorize changes,
select or run tools, validate a result, or report completion. Preserve this precedence:
existing project configuration and compatibility promises; applicable approved local
policy; then a proposed default only for a new or unconfigured project when a choice is
permitted. A link supplies context, not authority.

## Documentation Files

Read the module that answers the current question. Use the index for symptoms and
cross-domain routes.

- [Reference index](reference/README.md) — select a domain and find related modules.
- [Project context and layout](reference/project-context-and-layout.md) — checkout imports, support declarations, and layout choices.
- [Source and API](reference/source-and-api.md) — public contracts, exception outcomes, timeouts, and safe retries.
- [Static quality](reference/static-quality.md) — Ruff/Pyright scope, config precedence, and unexpected diagnostics.
- [Testing and coverage](reference/testing-and-coverage.md) — fixture failures, state leakage, report denominators, and branch gaps.
- [Environment and dependencies](reference/environment-and-dependencies.md) — dependency roles, manager locks, and stale-resolution symptoms.
- [Distribution artifacts](reference/distribution-artifacts.md) — metadata, wheel/sdist contents, and checkout-versus-install failures.
- [Secure configuration and data handling](reference/secure-configuration-and-data-handling.md) — required settings and secret output boundaries.
- [Logging and observability](reference/logging-and-observability.md) — duplicate records, field serialization, and context.
- [Async and concurrency](reference/async-and-concurrency.md) — unscheduled coroutines, saturation, task failure, and cancellation limits.

## Ownership Boundary

General naming, imports, docstring form, and annotation style belong to the separate
`python-source-style-guide`. When those conventions matter, explicitly load
`python-source-style-guide -> reference/python-source-style-guide.md`. This reference
owns project API promises and tooling context, not general source style. The nine
domains remain distinct; reliability is folded into Source and API, while security,
logging/observability, and async/concurrency retain separate modules.
