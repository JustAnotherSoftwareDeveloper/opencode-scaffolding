# Reference Index

Use this index to identify which outcome a requested question belongs to, which owner
answers that change request, and which local structural note carries the relevant context.
The routes serve planning discussions about TypeScript project work in Node.js and Bun
projects; they do not answer a project-specific question themselves.

## Route By Requested Outcome

Each route names the requested outcome and its discriminating clue, the owner entrypoint,
and the local structural note. A route is navigation only: it creates no delegation,
sequence, permission, or execution step.

- **Production behavior change.** Clue: the requested result is a change to an
  application's, service's, CLI product's, or library's behavior. Owner:
  `node-project-writer -> #production-behavior-change-workflow`. Structural note:
  [Provisional Outcome Distinctions](planning-boundaries.md#provisional-outcome-distinctions)
  and [Toolchain And Framework Layers](project-structure.md#toolchain-and-framework-layers).
- **Test-only work.** Clue: the requested result is tests, fixtures, helpers, or test
  layout without production-source edits. Owner:
  `node-project-test-writer -> #test-only-change-workflow`. Structural note:
  [Provisional Outcome Distinctions](planning-boundaries.md#provisional-outcome-distinctions)
  and [Toolchain And Framework Layers](project-structure.md#toolchain-and-framework-layers).
- **Dependency or environment work.** Clue: the requested result is a dependency or
  environment decision, or an authorized effect on a manifest, lockfile, install, or
  environment. Owner:
  `node-project-dependencies -> #dependency-decision-and-environment-workflow`.
  Structural note:
  [Clarifying Combined Requests](planning-boundaries.md#clarifying-combined-requests)
  and [Packages And Workspaces](project-structure.md#packages-and-workspaces).
- **Standalone quality work.** Clue: the requested result is type-check, lint, or format
  diagnostics or quality configuration, and remediation is not implied. Owner:
  `node-quality-workflow -> #standalone-quality-workflow`. Structural note:
  [Reading A Surprising Result](planning-boundaries.md#reading-a-surprising-result)
  and [Toolchain And Framework Layers](project-structure.md#toolchain-and-framework-layers).
- **Package artifact or consumer work.** Clue: the question concerns package metadata,
  what an archive contains, or which entry point and declarations a consumer receives.
  Owner: `node-package-distribution -> #package-artifact-and-consumer-workflow`.
  Structural note:
  [Provisional Outcome Distinctions](planning-boundaries.md#provisional-outcome-distinctions)
  and [Package Subpath Failure Layers](project-structure.md#package-subpath-failure-layers).
- **Repository utility work.** Clue: the target is one of this repository's deterministic
  utilities under `scripts/node/`, not a general CLI product. Owner:
  `skill-script-node-writer -> #procedure`; its tests:
  `skill-script-node-test-writer -> #procedure`. Structural note:
  [Question To Owner Routes](planning-boundaries.md#question-to-owner-routes). Utility
  conventions are not project defaults.
- **Executable plan work.** Clue: the requested output is a source-based plan or a bounded
  plan correction, not a project change. Owner:
  `plan-writer -> #planning-and-task-authoring`. Structural note:
  [Planning And Ownership Handoffs](planning-boundaries.md#planning-and-ownership-handoffs).

For shared runtime, checker, test, configuration, diagnostics, concurrency, and API
mechanics, use the passive `node-project-reference -> #route-by-question` map. For
source-style context, use `node-source-style-guide -> reference/source-style-guidance.md`.
This workspace's notes supply outcome and structural context only. The five outcome owners
above own change work; `node-project-reference`, `node-source-style-guide`, and this
planning reference are passive. Executable source-based plans remain with `plan-writer`;
nothing here creates an active planner, formal decision owner, or approval gate.

## Reference Context

- [Planning Boundaries](planning-boundaries.md) — classify a compressed or mixed request,
  read a surprising result, and distinguish the owner of an executable plan.
- [Project Structure](project-structure.md) — interpret mixed runtime and checker clues and
  distinguish coverage, dependency, and package-consumer evidence.

## Scope

These pages cover TypeScript project work in Node.js and Bun projects: TypeScript source,
configuration, declarations, tests, quality diagnostics, package artifacts, and API
documentation comments on exported declarations. Node.js and Bun runtime, module, loading,
and emitted-JavaScript mechanics appear only where they explain how TypeScript source
executes, emits, resolves, declares, or reaches a consumer. An authorized change covers the
TypeScript surface plus only the manifests and configuration that the authorization names;
JavaScript source edits are reported as out of scope, and a JavaScript-only request is
reported as out of scope.

The repository's deterministic utilities in `scripts/node/` have a separate local route,
and their Bun, Biome, test-layout, and coverage conventions are not general project
defaults.

## Descriptive Limit

These pages are descriptive rather than workflows or requirements. They define no
execution steps, commands, tools, writes, task generation, or verification selection. A
route creates no delegation, sequence, permission, or execution step, and naming an owner
grants no edit, tool, or approval authority and establishes no completion result.

Examples explain documented mechanics and trade-offs; they do not establish tested
compatibility, defaults, support guarantees, or a project-specific diagnosis. No page here
selects or prescribes Vite, and no route describes a workflow that invokes or relies on
Vite. A described relationship between concerns is not an implicit pipeline, and no
compatibility promise follows from it.
