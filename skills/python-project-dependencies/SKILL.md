---
name: python-project-dependencies
description: "Use when evaluating Python dependencies or changing a project's dependency declarations, lock, or environment."
selection:
  role: owner
  tags:
    actions: [evaluate dependencies, change dependencies, manage project environment]
    inputs: [Python project, dependency or environment request]
    outputs: [evidence-based decision, authorized dependency outcome report]
    topics: [Python dependencies, Python environments, dependency evaluation]
    environments: [Python application, Python service, Python package, Python library]
    constraints: [preserve manager and compatibility, authorized dependency and environment effects]
  use_when:
    - a request asks whether to add, remove, replace, or defer a Python dependency
    - a request asks to change Python dependency declarations, resolution, lock, or sync state
  not_for:
    - a request asks to change production behavior or write tests without a dependency outcome
    - a request asks only for standalone quality configuration, checks, or reports
    - a request asks to build, publish, or deploy a Python distribution
class: operation
---

# Python Dependency Decision and Change Workflow

Evaluate dependencies or make a requested dependency/environment change in a Python
project. Production behavior, standalone tests/quality, distribution artifacts,
publishing, and deployment remain separate outcomes.

## Normalize Input

Identify the project/root, capability or environment outcome, candidate if supplied,
compatibility/target constraints, policy/evidence, requested checks, and authorized
paths/effects. Default to read-only evaluation: repository access permits neither edits,
resolution, installs, lock updates, nor sync. Ask if a required candidate, scope, or
effect is materially ambiguous. Do not invent a candidate or support matrix; unspecified
validation targets remain untested.

## Procedure

1. **Inspect the project without changing it.** Identify project kind, Python/platform
   promises, manager/version, requirements, groups/extras, source/index settings,
   lock/resolution files, interpreter selection, and CI lock/sync behavior. Distinguish
   declared support, selected interpreter, resolved graph, and installed environment;
   one local environment does not prove all runtime targets.
2. **Establish evidence and precedence.** Preserve existing configuration and
   compatibility first, approved local policy next, and proposed defaults only for new
   or unconfigured projects when choice is permitted. Surface conflicts. Preserve the
   manager and its conventions unless change is authorized; uv is an optional proposal,
   not a universal requirement or superiority finding.

   Ground version-sensitive APIs, commands, and behavior in permitted target-version
   evidence. Obtain separate scoped authorization before checking current external
   primary documentation. Record exact source, applicable version, access context/date,
   and limits; hashes do not prove freshness. If evidence, access, or authorization is
   missing, name the affected detail and needed source/version, defer it as
   non-executable, and give a bounded authorized refresh handoff.
3. **Evaluate the need and candidate.** First consider the standard library, existing
   code, and approved dependencies. For a candidate or material version change, inspect:

   - API/functional fit, Python/platform compatibility, and stability;
   - maintenance/support, security response, authentic source, and known vulnerabilities;
   - direct/transitive graph, install/build needs, and target artifact availability;
   - license metadata and shipped license evidence for the graph and intended use;
     escalate legal/policy decisions to the responsible owner.

   Retain evidence links, dates, gaps, and qualifications. Popularity, activity, badges,
   and scores prompt investigation, not verdicts. Invent no release-age or vulnerability
   thresholds, license allowlists, or universal approval process. The source basis is
   not a candidate audit, legal conclusion, or comparative tool ranking.
4. **Record the decision.** Choose **no-add** when need is absent or already met;
   **add** when concrete need and evidence support the candidate within constraints and
   approvals; **replace** when a concrete issue and understood migration impacts warrant
   it; or **defer** when material evidence or an owner decision is missing. Explain why
   and, for deferral, name the next check or decision owner. A recommendation does not
   authorize removal, migration, or installation.
5. **Apply only authorized effects.** Confirm exact files/environment before editing,
   resolving, installing, updating locks, or syncing. Stop effects needing additional
   authorization or policy decisions. Preserve runtime requirements, consumer-facing
   extras, and development groups as distinct roles; groups are not automatically
   distribution metadata. Use the manager's target-version workflow to keep declarations
   and resolution consistent. Do not hand-edit/regenerate locks, broaden constraints,
   alter indexes, or install optional groups unless in scope. Review the diff and lock
   impact; do not make incidental source, test, quality, build, or publishing changes.
6. **Validate the requested outcome.** When applicable and authorized, use the manager's
   documented non-rewriting lock-currentness check; trusting an existing lock is not
   checking it against metadata. For authorized sync, record interpreter/platform,
   groups/extras, manager version, and package installation/removal effects. Run
   requested project-configured checks in the resolved environment on stated targets,
   not an invented matrix or gate. Record exact commands, versions, context, and
   results; distinguish stale-lock, absent, skipped, unavailable, failed, deferred,
   and inconclusive checks from passes.

## Self-Validation

- The decision follows evidence, and actual declaration/lock/environment effects match
  authorization rather than merely the recommendation.
- Lock/sync success is not presented as proof of behavior, all-platform compatibility,
  complete security, legal compatibility, or policy approval.

## Expected Output

Return the no-add/add/replace/defer decision with rationale, candidate/source identity,
precedence applied, unresolved risk/approval, changed paths and environment effects
(or none), and exact validation evidence. State untested targets, blockers, and bounded
next steps without claiming another operation's outcome.

## Docs

- [Evaluation and environment changes](reference/evaluation-and-environment-changes.md) —
  candidate decisions, dependency roles, and declaration/lock/sync effects.

Explicitly load `python-project-reference` before reading a relevant module below.
Its passive context grants no effects, policy, or completion evidence.

- `python-project-reference -> reference/environment-and-dependencies.md` — manager,
  dependency roles, evaluation, and lock/sync context.
- `python-project-reference -> reference/project-context-and-layout.md` — project kind
  and compatibility.
- `python-project-reference -> reference/distribution-artifacts.md` — dependency versus
  build/artifact boundaries.
