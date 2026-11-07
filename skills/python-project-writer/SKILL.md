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

Own one bounded production-behavior change in an ordinary Python application,
service, internal package, or library. Change production source and only regression
tests directly coupled to the requested behavior. This operation owns its inspection,
decisions, permitted effects, validation, and result report; passive references provide
context only.

## Normalize Input

Normalize the request into one change outcome, target project, authorized scope, and
available compatibility context. Identify the intended observable behavior and any
explicitly permitted paths or effects. Inspect the project to resolve details that the
request leaves open, but do not infer permission from repository access or from a file
being nearby.

The outcome must concern production behavior. If the intended behavior, target, or
material scope is ambiguous, ask a focused question before editing. If the request lacks
authorization for a required side effect, stop before that effect and report the exact
missing authorization. Keep test-only, standalone quality, dependency/environment,
distribution, publishing, and full deployment outcomes with their distinct owners; do
not perform them as incidental parts of a source change.

## Procedure

1. **Inspect the project without changing it.** Identify its kind and relevant package
   or runtime shape; inspect the behavior's implementation and callers, public imports
   and documented interfaces, supported Python/platform versions, dependency and
   environment assumptions, existing conventions, and relevant runtime, security, and
   reliability constraints. Read only the project files and configured guidance
   needed to understand the requested outcome. Keep `scripts/python/` conventions
   specific to that script tree.

   Load passive documentation selectively when its topic materially affects the
   change. Use explicit cross-skill references, and read only the relevant module:

   - `python-project-reference -> reference/project-context-and-layout.md` for project
     shape, compatibility promises, and layout context.
   - `python-project-reference -> reference/source-and-api.md` for public behavior,
     typed-interface promises, compatibility, and general failure/reliability context.
   - `python-project-reference -> reference/testing-and-coverage.md` for directly
     coupled regression-test or coverage context.
   - `python-project-reference -> reference/static-quality.md` for the target's
     configured Ruff/Pyright behavior and result limits.
   - `python-project-reference -> reference/environment-and-dependencies.md` when an
     existing interpreter or resolved environment materially affects the change.
   - `python-project-reference -> reference/secure-configuration-and-data-handling.md`
     when changed behavior handles secrets or sensitive data.
   - `python-project-reference -> reference/logging-and-observability.md` when changed
     behavior emits or routes log/context records.
   - `python-project-reference -> reference/async-and-concurrency.md` when changed
     behavior alters task, thread, process, synchronization, or shutdown behavior.
   - `python-project-reference -> reference/distribution-artifacts.md` only when an
     existing consumer or installation contract is relevant to the behavior change;
     artifact production and distribution outcomes remain outside this operation.
   - `python-source-style-guide -> reference/python-source-style-guide.md` when general
     source conventions are relevant.

   These references are passive, non-transitive context. They do not authorize an
   action, select a project policy, or establish validation or completion evidence.

2. **Decide the smallest correct change.** Preserve existing project configuration
   and compatibility promises first, then applicable approved local policy, then
   proposed defaults only for a new or unconfigured project when the task permits a
   choice. If sources conflict, expose the conflict to the responsible project or
   policy owner rather than silently migrating. Separate documented mechanics,
   project examples, proposed choices, and approved local requirements. Do not infer
   comparative outcomes, user demand, universal thresholds, enterprise policy, or
   effectiveness from the bounded evidence. (A_BASE: `.analysis/1793895766484-python-enterprise-quality-baseline-analysis.md#scope`; A_MAP: `.analysis/1793896454804-python-enterprise-module-allocation-analysis.md#canonical-module-map-and-operation-consumers`.)

   Trace the behavior and its compatibility surface before choosing edits. Limit
   production changes to what is necessary for the requested outcome and regression
   tests to the behavior directly affected. Do not broaden the task into unrelated
   refactoring, style migration, new test infrastructure, quality configuration,
   dependency changes, packaging, or deployment work.

3. **Authorize the proposed effects.** Before writing, state the intended production
   and directly coupled test paths, any compatibility impact, and the checks that may
   run. Confirm they fit the user's authorization and project policy. If the needed
   change exceeds the authorized scope, requires an unresolved policy decision, or
   requires a separate outcome owner, pause before that effect and report the boundary
   or ask for authorization. Do not change configuration, dependencies, locks, or
   distribution/deployment artifacts as a side effect of this operation.

   For concrete version-sensitive syntax, API behavior, commands, or tool behavior,
   use the target project's version/configuration documentation or other permitted
   project evidence. If the detail requires current external documentation, obtain
   separate scoped authorization before checking a current primary source. Record the
   exact source or document, applicable version, access context and date, and limits.
   If authorization, access, or suitable evidence is unavailable, name the affected
   detail and needed source/version, mark it deferred and non-executable, and give a
   bounded authorized refresh handoff. Do not guess or treat a snapshot hash as proof
   of freshness.

4. **Make only the authorized change.** Implement the requested production behavior
   and add or adjust only directly coupled regression tests. Preserve unaffected public
   names, imports, behavior, supported versions, and local conventions. Keep sensitive
   values out of source, test output, logs, and the report. Do not fetch external
   material without the scoped authorization in step 3, modify unrelated paths, or run
   a command with effects beyond the authorization. If work uncovers a required
   out-of-scope change, stop before making it and record the needed owner or
   authorization.

5. **Validate the changed outcome.** Run relevant configured behavior/API tests and
   the actual project-configured formatting, lint, and type checks that apply to the
   changed paths, when authorized and available. Select commands and targets from the
   project's own configuration and version context; do not invent a universal command
   or add a gate. Use non-writing checks where available unless a write is explicitly
   authorized. If a check requires an unavailable version-sensitive detail, apply the
   bounded deferral handoff from step 3. Record exact commands, versions when known,
   targets, and results. Distinguish failures caused by this change from pre-existing
   failures; do not repair unrelated findings. Report skipped, unavailable, or
   inconclusive checks and what evidence they leave missing. A passing static check or
   test run is evidence only for its actual configured scope, not proof of all
   compatibility, security, or production behavior.

6. **Report the result.** Provide a concise report with the requested behavior and
   outcome; changed production and directly coupled test paths; compatibility and
   support assumptions; exact validation commands, versions/targets when known, and
   results; and remaining failures, deferrals, or evidence gaps. State when no change
   was made and why. Do not claim a broader support matrix, deployment result, policy
   approval, or completion for another owner's outcome.

## Self-Validation

- The request is a bounded production-behavior change, not a test-only or standalone
  quality, dependency, distribution, publishing, or deployment outcome.
- Inspected project shape, interfaces, supported versions, dependencies, conventions,
  and relevant runtime/security/reliability constraints before proposing edits.
- Production edits and directly coupled regression tests stay within explicit
  authorization; unrelated paths and outcomes remain untouched.
- Existing configuration and compatibility promises take precedence over approved
  local policy, which takes precedence over proposed defaults where choice is allowed.
- Passive references were loaded selectively with explicit syntax and did not add
  authority, effects, or completion evidence.
- Concrete version-sensitive details have permitted source/version/access-context/date
  evidence and limits, or are named as deferred, non-executable details with a bounded
  authorized refresh handoff.
- Relevant configured behavior/API tests and applicable configured format/lint/type
  checks were run when authorized, and exact results and gaps are reported.
- The report identifies compatibility assumptions, changed paths, exact results, and
  remaining limits without claiming untested targets or unrelated outcomes.
- Filled content uses semantic prose forms and contains no Markdown tables.

## Expected Output

One bounded production-behavior change, with only directly coupled regression-test
changes, and a result report containing changed paths, compatibility assumptions,
exact validation commands and results, and any unresolved gaps. If required input,
authorization, or evidence blocks the work, make no unauthorized change and report the
specific blocker and bounded next step.
