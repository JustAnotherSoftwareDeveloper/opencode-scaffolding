---
name: python-domain-planning
description: "Use as planning reference for Python project change work: which operation owns each outcome and how they combine."
selection:
  role: reference
  tags:
    actions: [explain, plan]
    inputs: [Python project request]
    outputs: [planning context]
    topics: [Python change workflow, outcome ownership]
    environments: [Python application, Python service, Python package, Python library]
    constraints: [no side effects]
  use_when:
    - a request needs Python project change planning, outcome ownership, or multi-outcome sequencing
  not_for:
    - executing or editing a Python project, skill, or plan
class: planning
---

# Python Domain Planning Reference

This reference describes how Python project outcomes fit together, which operations
own them, and what evidence connects their work. It provides planning context, not
an execution procedure, permission to act, or evidence that a change is complete.

## Domain Context

Existing project configuration and compatibility promises take precedence over
applicable approved local policy. Proposed defaults apply only to new or unconfigured
projects when the request permits a choice. An application run from a checkout does
not automatically need a library's distribution artifacts or public API promises.
Treat each tool result as scoped evidence: record the effective version, configuration,
paths, target environment, invocation, and outcome when they affect the conclusion.
Declared support is not tested support, and a passing local check is not proof for
untested targets. Any proposed baseline is nonbinding, not approved project policy.

`python-project-reference` supplies nine project topics: layout, API, quality,
testing, dependencies, distribution, security, logging, and concurrency.
`python-source-style-guide` supplies five source-convention topics. Neither reference
chooses a project policy or transfers execution authority.

## Key Considerations

- Production fixes and directly coupled regression tests form one writer outcome;
  routine validation does not require separate test-writing or quality operations.
- Independently requested test-only or standalone quality outcomes have distinct owners.
  A test-only defect report does not authorize a production fix.
- Quality configuration may change only when explicitly requested and authorized;
  check-only work preserves configuration. Neither case includes source/test remediation.
- A dependency decision, its authorized effects, a distribution build, and publication
  are different outcomes; success in one does not establish the others.
- Compatibility is project-specific: preserve existing behavior/configuration and
  supported targets; apply approved local policy where relevant; use proposed defaults
  only where a new or unconfigured project permits a choice. A version declaration,
  lock, clean check, or artifact tag each establishes only its own stated scope.

## Common Workflows

- [Feature with new dependency](reference/feature-with-new-dependency.md) — dependency
  decision and authorized environment effects precede dependent production work.
- [Brownfield bug fix](reference/brownfield-bug-fix.md) — one writer owns the fix,
  directly coupled regression tests, and relevant configured validation.
- [Test-only defect exposure](reference/test-only-defect-exposure.md) — test evidence
  documents a defect without extending authorization to production changes.
- [Dependency evaluation](reference/dependency-evaluation.md) — evidence supports a
  decision independently of permission to change declarations, locks, or environments.
- [Library distribution](reference/library-distribution.md) — metadata and build
  choices lead to artifact inspection and target-specific install evidence.
- [Scoped quality check](reference/scoped-quality-check.md) — check-only reporting or
  explicitly requested quality configuration, without source/test remediation.

## Related Skills

- `python-project-writer` owns production behavior and directly coupled regression tests.
- `python-project-test-writer` owns independently requested tests, fixtures, helpers,
  and test layout without production changes.
- `python-quality-workflow` owns standalone quality configuration or scoped check/report
  outcomes, not remediation.
- `python-project-dependencies` owns dependency decisions and authorized declaration,
  lock, resolution, and environment effects.
- `python-package-distribution` owns distribution metadata, build configuration,
  wheel/sdist contents, and installability checks, not publishing or deployment.

Reference use requires an explicit skill-tool load followed by the needed document
read. The [reference index](reference/README.md#reference-context) identifies focused
cross-skill destinations; neither a link nor a skill name loads anything transitively.

## Docs

The [workflow index](reference/README.md) distinguishes the six practices and their
handoff evidence. Each workflow is descriptive; the consuming operation retains its
procedure, tools, writes, output, and completion validation.
