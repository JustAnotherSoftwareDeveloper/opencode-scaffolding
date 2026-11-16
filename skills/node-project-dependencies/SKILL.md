---
name: node-project-dependencies
description: "Use when evaluating a dependency or making an authorized dependency or environment change in a TypeScript Node.js or Bun project."
selection:
  role: owner
  tags:
    actions: [evaluate dependencies, change dependencies, manage project environment]
    inputs: [TypeScript Node.js or Bun project, dependency or environment request]
    outputs: [evidence-based dependency decision, authorized environment outcome report]
    topics: [dependency graph, package managers, lockfiles, runtimes, workspaces]
    environments: [TypeScript Node.js project, TypeScript Bun project]
    constraints: [preserve manager conventions, authorized dependency and environment effects]
  use_when:
    - a request asks whether to add, remove, replace, or defer a dependency
    - a request asks to change dependency declarations, lockfiles, manager or runtime selection, or install state
  not_for:
    - a JavaScript-only request, including JavaScript source edits, JavaScript checking, or JSDoc typing of JavaScript files
    - changing production behavior or writing tests without a dependency or environment outcome
    - standalone quality configuration or diagnostics
    - building or validating package artifacts, publishing, or deploying
    - changing this repository's scripts/node/ automation or its dependencies
class: operation
---

# Dependency Decision And Environment Workflow

Own the dependency decision and any authorized dependency or environment change in an
existing TypeScript Node.js or Bun application, service, CLI, package, library, or
workspace. The scope is TypeScript-only: TypeScript source, configuration, declaration
output, tests, quality diagnostics, and package artifacts. TypeScript API documentation
comments on exported declarations are in scope. Node.js and Bun runtime, module, loading,
and emitted-JavaScript mechanics appear only where they explain how TypeScript source
executes, emits, resolves, declares, or reaches a consumer. Standalone JavaScript source
guidance, JavaScript or mixed-language eligibility, JavaScript checking (`allowJs`,
`checkJs`), and JSDoc typing of `.js` files are out of scope, and a JavaScript-only request
is reported out of scope.

An authorized change covers the TypeScript surface and only the manifests or configuration
the authorization names. Report JavaScript source edits as out of scope rather than
broadening them into mixed-source authoring.

Keep production behavior, test-only, standalone quality, and package-artifact outcomes with
their respective owners. Naming a neighboring owner identifies where an outcome belongs; it
does not start that work, promise its result, or establish a required sequence. Repository
`scripts/node/` utilities and their tests keep their repository-specific route, and their
Bun conventions are not evidence about an application's manager.

## Routing Boundaries

- “Should this project add a package for the requested capability?” is a dependency
  evaluation here, even when the answer is no-add or defer.
- “Fix the behavior after upgrading the package” is production behavior work for
  `node-project-writer`; “add tests for the existing contract” is test-only work for
  `node-project-test-writer`.
- “Configure linting” is standalone quality work for `node-quality-workflow`. “Pack the
  library and inspect the consumer artifact” is package-artifact work for
  `node-package-distribution`.
- Changes to this repository's `scripts/node/` utilities stay with
  `skill-script-node-writer` or `skill-script-node-test-writer`; their Bun defaults do not
  apply to general Node.js or Bun applications.
- For a no-Vite request, do not select Vite or rely on a Vite-based workflow. An incidental
  dependency edge is not by itself proof of direct selection; do not claim dependency-graph
  absence without project-specific resolved-tree evidence.

## Normalize Input

Identify the project and effective workspace root, requested capability or environment
outcome, candidate dependency if supplied, target runtime(s), compatibility constraints,
relevant policy and evidence, requested validation, authorized paths, and permitted effects.
Default to read-only evaluation. Reading a repository, inspecting a manifest or lockfile, or
evaluating a candidate is not permission to edit declarations, resolve or install packages,
rewrite a lockfile, change a manager or runtime selector, synchronize an environment, or run
dependency lifecycle scripts. Ask when a missing candidate, target, policy decision, or
effect could materially change the result. Do not invent a candidate, support matrix, or
approval policy.

## Procedure

1. **Inspect the existing project without changing it.** Establish the applicable package
   boundary and workspace root; inspect manifests, manager and version selectors,
   lockfile(s), runtime selection, scripts, configuration, CI behavior, repository
   instructions, and relevant dependency declarations. Distinguish declared compatibility,
   selected runtime, manager dispatch, resolved dependency graph, installed environment,
   and workspace membership. A `package.json`, TypeScript file, framework name, or use of
   `bun install` alone does not establish which runtime executes the project.
2. **Establish evidence and precedence.** Preserve existing project configuration and
   compatibility promises first, applicable approved local policy next, and proposed
   defaults only for an unconfigured project when the request permits a choice. Identify
   conflicts and unknowns. Ground version-sensitive claims in evidence for the target
   manager, runtime, and project versions; distinguish publisher documentation from executed
   project checks. If the evidence is insufficient, name the affected claim and defer rather
   than guessing.
3. **Evaluate the need and candidate.** Consider whether existing code or an approved
   dependency already meets the need. For a proposed dependency, compare its specific API
   and functional fit, target-runtime and platform compatibility, maintenance and support
   evidence, transitive, install, and build implications, authentic package identity, and
   relevant license or security information where available. Treat popularity, activity,
   badges, and automated scores as investigation leads, not conclusions. Do not invent
   vulnerability thresholds, license allowlists, or organization-wide security policy;
   escalate policy and legal decisions to their responsible owner. A recommendation is not
   authorization to install, remove, or migrate. For identity dimensions, see
   [Evaluation And Environment Changes](reference/evaluation-and-environment-changes.md#check-package-identity);
   for a bounded example of metadata that narrows questions without proving runtime support,
   see
   [Evaluation And Environment Changes](reference/evaluation-and-environment-changes.md#interpret-claims-without-overreading-them).
4. **Record a bounded decision.** Choose **no-add** when the need is absent or already met;
   **add** when concrete need and evidence support the candidate within known constraints;
   **replace** when an evidenced issue and understood migration impact justify it; or
   **defer** when material evidence, compatibility, or an owner decision is missing. State
   the evidence class behind the decision, its source and version scope, trade-offs, and
   unresolved risk. For deferral, name the next bounded evidence check or the decision
   owner. When only publisher metadata is available, the result is defer rather than
   supported or incompatible.
5. **Apply only authorized effects.** Confirm exact target files and environment before
   editing declarations, resolving or installing packages, updating a lockfile, changing a
   manager or runtime selector, or synchronizing an environment. Preserve the selected
   manager and its conventions unless the requested change authorizes otherwise. Keep
   dependency groups and peer or optional roles distinct where the manager defines them.
   Do not hand-edit or regenerate a lockfile, change indexes, migrate managers, broaden
   constraints, or install optional groups as incidental work. Stop before any effect
   requiring additional authorization or a policy decision; keep source, test, quality,
   build, publication, and deployment changes out of scope. See
   [Manager Semantics And Workspace Placement](reference/manager-semantics-and-workspace-placement.md#preflight-a-requested-install-or-lock-change)
   for the manager, workspace, and write-set questions to settle before an install or lock
   change.
6. **Validate the requested outcome.** When applicable and authorized, use the selected
   manager's project-configured, non-rewriting lock-currency or resolution check; trusting a
   checked-in lock is not the same as verifying it against the manifest and manager
   behavior, and a non-rewriting check can still replace an installed tree. For authorized
   installation or synchronization, report manager and runtime versions, package and
   workspace scope, platform, selected groups, and material install or removal effects.
   Run only requested or project-configured checks within the authorized scope. Record
   exact commands, targets, versions when known, and results. Distinguish stale lock,
   missing evidence, skipped, unavailable, failed, deferred, and inconclusive checks; do not
   imply that install success proves application behavior, all-target compatibility,
   complete security, legal compatibility, or policy approval.

## Self-Validation

- The work stays inside the TypeScript-only scope, with ancillary edits limited to the manifests or configuration the authorization names.
- The decision follows stated need, applicable evidence, project constraints, and approved policy without inventing a candidate or support matrix.
- Actual declaration, lockfile, manager or runtime, and environment effects match explicit authorization; a recommendation alone caused no change.
- Manager, lockfile, workspace graph, runtime, and installed state are not conflated; version and platform gaps are reported.
- Candidate metadata and publisher documentation are not reported as project execution evidence; unresolved compatibility is dispositioned explicitly.
- Version, platform, and tool claims stay bounded by project evidence; no universal stack or compatibility promise is implied.
- No unrelated source, test, quality, artifact, publication, deployment, or `scripts/node/` changes were made, and no neighboring outcome is reported as completed.

## Expected Output

Return the no-add, add, replace, or defer decision and rationale, the evidence class and
scope behind it, candidate and version limits, precedence applied, unresolved risks or
required approval, changed paths and environment effects (or none), and exact validation
evidence. State untested targets and bounded next steps. If blocked or unchanged, explain
why without claiming another operation's result.

## Docs

- [Dependency And Environment Reference](reference/README.md) — workspace index, supporting scope, and read-only limits.
- [Evaluation And Environment Changes](reference/evaluation-and-environment-changes.md#choose-no-add-add-replace-or-defer) — candidate evidence, the four decision outcomes, package identity, and authorized environment effects.
- [Manager Semantics And Workspace Placement](reference/manager-semantics-and-workspace-placement.md#lock-and-install-guarantees-by-manager-and-command) — per-manager groups, lock and install guarantees, workspace placement, and install preflight.
