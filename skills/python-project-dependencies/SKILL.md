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

Own one bounded dependency decision or requested dependency/environment outcome for an
ordinary Python application, service, internal package, or library. Preserve the
project's compatibility promises and manager; do not treat this proposed family
guidance as approved policy.

## Normalize Input

Normalize one request record: target project/root and kind; requested capability and decision or change outcome; candidate identity if supplied; compatibility and target constraints; configured manager/version and relevant declarations, groups/extras, sources, lock, and environment; approved policy/evidence; requested checks/targets; and authorized paths/effects.

Default to read-only evaluation. Preserve the configured manager and declared targets; infer neither a candidate nor a support matrix. Do not edit, install, resolve, change a lock, or sync without explicit authorization for that effect.

If the project, requested capability, required candidate/change scope, or exact effect authorization is materially ambiguous, ask a focused question and block that effect. Treat unspecified validation targets as untested rather than inventing a matrix.

## Procedure

1. **Normalize the request.** Identify the project, capability or environment outcome,
   requested targets, permitted paths, and explicitly authorized effects. Distinguish
   an evaluation-only request from permission to edit declarations, locks, interpreter
   settings, or installed environments. Repository access does not grant write, install,
   lock, or sync permission. Ask a focused question if the candidate, need, scope, or
   authorization is materially ambiguous. Keep production behavior, test-only work,
   standalone quality work, and distribution artifacts with their respective owners.

2. **Inspect the existing project without changing it.** Read only relevant project
   files and configured instructions. Identify project kind, supported Python and
   platform promises, manager and version, direct requirements, dependency groups and
   extras, source/index configuration, lock or resolution files, environment selection,
   CI lock/sync behavior, and compatibility constraints. Separate declared support,
   selected interpreter, resolved graph, and installed environment; a local environment
   does not prove the full runtime or every supported target.

   Load passive context selectively and only when it materially helps interpret the
   target. Use `python-project-reference -> reference/environment-and-dependencies.md`
   for manager, dependency-category, lock/sync, or evaluation context;
   `python-project-reference -> reference/project-context-and-layout.md` for project
   and compatibility context; and
   `python-project-reference -> reference/distribution-artifacts.md` to distinguish
   dependency work from build/artifact work. These references are passive and
   non-transitive: they add no actions, permissions, policy, validation, or completion
   evidence.

3. **Decide from evidence, not a score.** Name the capability and constraints, then
   check whether the standard library, existing project code, or an already approved
   dependency can meet them. For a candidate or material version change, gather
   proportionate evidence about:
   - API and concrete functional fit, Python/platform compatibility, and stability;
   - maintenance and support signals, security response, authentic source, and
     relevant known-vulnerability evidence;
   - the resolved direct and transitive graph, install/build requirements, and target
     artifact availability; and
   - license metadata and shipped license evidence for the relevant graph and intended
     use, escalating legal or policy questions to the responsible owner.

   Preserve evidence links, dates, gaps, and qualifications. Popularity, activity,
   badges, and aggregate scores may prompt investigation but are not verdicts. Do not
   invent release-age limits, vulnerability thresholds, license allowlists, or a
   universal approval process. The bounded research supports evaluation dimensions,
   not any candidate-specific audit, legal conclusion, or comparative tool ranking
   (PW C09–C13; [OpenSSF evaluation guide (S11)](https://best.openssf.org/Concise-Guide-for-Evaluating-Open-Source-Software.html),
   [Scorecard limitations (S13)](https://github.com/ossf/scorecard/blob/main/README.md),
   [GitHub dependency-graph limits (S15)](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-graph-data),
   [PyPA license-expression specification (S16)](https://packaging.python.org/en/latest/specifications/license-expression/)).

   Record one outcome and its rationale:
   - **No-add:** the need is absent or existing capabilities adequately meet it.
   - **Add:** the need is concrete and evidence supports the candidate within project
     constraints and applicable approval requirements.
   - **Replace:** a concrete issue warrants replacement and compatibility/migration
     impacts are understood; do not infer permission to remove or migrate.
   - **Defer:** material evidence or an owner decision is missing. Name what is missing,
     why it matters, and the bounded next check or decision owner.

4. **Apply precedence and confirm effects.** Preserve existing project configuration
   and compatibility promises first; apply relevant approved local policy next; use a
   proposed default only for a new or unconfigured project when the task permits a
   choice. Surface conflicts rather than silently migrating. Preserve the established
   manager and its declaration, lock, groups, source settings, interpreter selection,
   and sync conventions unless the request explicitly authorizes a change. uv is a
   proposed option for a new or unconfigured project when choice is allowed, not a
   universal requirement or evidence of superiority.

   Before any write, installation, resolution, lock update, or sync, verify that the
   requested effect and exact files/environment are authorized. Keep edits to the
   authorized dependency and environment scope. Do not change production source, build
   or publish distributions, or migrate managers as incidental work. If authorization
   is absent or a separate policy decision is needed, stop before that effect and
   report the blocker.

5. **Make only the authorized change.** Preserve dependency roles: runtime requirements
   serve runtime use; published extras describe optional consumer-facing features;
   development groups are not automatically distribution metadata. Use the target
   manager's documented workflow and version to update declarations and resolution
   consistently. Do not hand-edit or regenerate a lock, broaden constraints, alter
   source/index settings, or install optional groups unless that effect is in scope.
   Record the exact files and environment changed; review the resulting diff and lock
   impact before proceeding.

6. **Validate the requested outcome.** Use the manager's documented non-rewriting
   lock-currentness check on the stated project and targets. Do not substitute a mode
   that merely trusts an existing lock for a check that verifies it matches project
   metadata. Sync only when explicitly authorized; record interpreter, platform,
   selected groups/extras, manager version, and whether the sync can remove or install
   packages. Run the requested project checks in the resolved environment only on the
   stated targets and with project-configured commands. Do not invent a universal test,
   CI matrix, or security gate.

   Record exact commands, versions, target context, and results. Distinguish an absent,
   skipped, unavailable, stale-lock, failed, or inconclusive check from a pass. A clean
   lock check or successful sync does not prove application behavior, all-platform
   compatibility, complete security coverage, or legal compatibility. Route separate
    quality configuration/check outcomes to `python-quality-workflow -> #scoped-quality-workflow`;
    production behavior to `python-project-writer -> #production-behavior-change-workflow`;
    test-only changes to `python-project-test-writer -> #test-only-change-workflow`; and
    build/distribution outcomes to `python-package-distribution -> #distribution-workflow`.

7. **Report the decision and result.** State the no-add/add/replace/defer decision and
   evidence-based rationale, project precedence applied, candidate/source identity,
   unresolved risk or approval, and whether any change was authorized and made. List
   changed paths and environment effects, exact validation commands/versions/targets,
   outcomes, and skipped checks. If no change occurred, say so. Do not claim a broader
   compatibility matrix, complete dependency security, policy approval, or another
   owner's outcome.

## Version-Sensitive Evidence

The following scoped command details were checked on 2026-11-06 through Context7 against
the official uv `0.13.5` tagged documentation: [dependency management](https://github.com/astral-sh/uv/blob/0.13.5/docs/concepts/projects/dependencies.md)
and [locking and syncing](https://github.com/astral-sh/uv/blob/0.13.5/docs/concepts/projects/sync.md).
The lookup covered the documented examples `uv add httpx` for a project dependency and
`uv add --group lint ruff` for a named development group, plus locked versus frozen
lock/sync behavior. The tagged documentation describes `uv add` as updating project
metadata, the lock, and environment; `uv sync --locked` checks that the lock does not
need an update, while
`--frozen` uses the lock without checking it against project metadata; syncing changes
the selected environment and can remove extraneous packages. These are uv `0.13.5`
mechanics, not a target project's installed-version evidence, a manager recommendation,
or authorization to run them. Confirm the target version and current project config
before relying on a concrete command. The separate research bundle's PW C01–C14 claims
and uv/PyPA/OpenSSF/GitHub sources were inspected on 2026-11-04; they are bounded
documentation evidence, not a comparative study or candidate audit. Hashes establish
source snapshot identity only, not freshness.

## Self-Validation

- The request and report own a dependency decision or authorized dependency/environment
  outcome, not production source, tests, standalone quality, or distribution work.
- Existing compatibility and configuration, approved local policy, and permitted
  proposed defaults were considered in that order; conflicts and uncertainty remain
  visible.
- The decision identifies concrete need, evidence, rationale, and unresolved risks;
  no unsupported score, universal threshold, or policy is presented as fact.
- Every declaration, lock, install, and sync effect stayed within explicit
  authorization; exact manager/version, paths, targets, and results are reported.
- Version-sensitive commands cite applicable versioned evidence or are deferred as
  non-executable with a bounded authorized refresh handoff.
- Passive references were selective and added no transitive authority or completion
  evidence; no source implementation or distribution build was performed.

## Expected Output

One evidence-based no-add/add/replace/defer decision, with any requested authorized
dependency/environment changes and scoped validation, plus a result report containing
the rationale, changed paths/effects, exact checks, and remaining risks or deferrals.
If authorization or material evidence blocks the outcome, make no unauthorized change
and report the blocker and bounded next step.
