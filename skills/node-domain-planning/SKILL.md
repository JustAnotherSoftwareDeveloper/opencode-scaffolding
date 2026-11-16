---
name: node-domain-planning
description: "Use as planning reference for TypeScript-only Node.js and Bun project structure, outcome boundaries, and planning constraints."
selection:
  role: reference
  tags:
    actions: [explain, plan]
    inputs: [TypeScript Node.js or Bun project request]
    outputs: [project planning context]
    topics: [project structure, runtime boundaries, outcome ownership]
    environments: [Node.js projects, Bun projects]
    constraints: [passive, no task generation or execution]
  use_when:
    - a project design or planning discussion needs context on how Node/Bun project concerns relate
  not_for:
    - implementing or validating a project change
    - generating executable tasks or creating a source-based plan
    - deterministic utilities in this repository's scripts/node/ workspace
    - JavaScript-only source work or JavaScript diagnostics, which are out of scope
class: planning
---

# Node Project Planning Context

This reference describes structural relationships and planning-relevant constraints for TypeScript-only Node.js and Bun project work. Its scope is TypeScript source, TypeScript configuration, declaration output, TypeScript tests, TypeScript quality diagnostics, TypeScript package artifacts, and TypeScript API documentation comments on exported declarations. Node.js and Bun runtime, module, loading, and emitted-JavaScript mechanics appear only where they explain how TypeScript source executes, emits, resolves, declares, or reaches a consumer. An authorized change covers the TypeScript surface plus only the manifests and configuration that the authorization names; JavaScript source edits are reported as out of scope, and a JavaScript-only request is reported as out of scope. This is passive context, not a project-specific assessment, execution procedure, task list, approval, or completion result.

## Domain Context

A project may use Node.js or Bun as its runtime; it may also use Bun only for package installation or command execution. Source execution or transformation, static type checking, module resolution, package-manager behavior, build artifacts, and artifact consumption interact, but each remains a distinct concern. Frameworks and adapters add their own output and runtime surfaces.

The [Project Structure](reference/project-structure.md) reference explains the structural model and evidence qualifications. The [Planning Boundaries](reference/planning-boundaries.md) reference describes outcome ownership and planning boundaries.

## Key Considerations

- Establish only project facts relevant to the requested outcome from source and repository evidence. A manifest, `.ts` file, framework name, or repository root alone does not establish the full project structure.
- Distinguish runtime target and version from package manager, module mode, checker, transformer or builder, test runner, framework, adapter, workspace scope, and output consumer. Compatibility is conditional on those facts; examples do not establish a universal stack or Node/Bun parity.
- TypeScript execution or transformation does not by itself establish type checking. A successful type check or build does not by itself establish that the selected output works in its actual consumer runtime.
- Keep proposed outcome ownership distinct: production behavior, test-only changes, dependency/environment work, standalone quality work, and package artifact/consumer work have different potential write and evidence boundaries. This provisional family roster is not a universal architecture or an orchestration contract.
- Do not select or prescribe Vite, or describe a workflow that invokes or relies on it. The inspected SvelteKit v3 setup, Astro v7 documentation snapshot, React Router v8 Framework Mode, and Vitest 4.1.12/5.0.5 are Vite-dependent examples, not no-Vite alternatives; the Astro registry snapshot and documentation versions differ. These snapshots are version-bounded, point-in-time observations, not current recommendations, and their version values were not re-verified for this entrypoint. An incidental dependency edge is not direct selection, and no blanket transitive ban or graph-absence claim follows. See [Project Structure](reference/project-structure.md) for the qualifications.
- The repository's deterministic utilities in `scripts/node/` have a separate, local route. Their Bun, Biome, test-layout, and coverage conventions are not general project defaults.
- Publisher documentation and package metadata are point-in-time and version-sensitive; a compatibility or behavior claim stays scoped to its cited version, mode, and configuration.
- Security, observability, concurrency, reliability, and source/API concerns are conditional context, not an organization-wide policy or mandatory checklist. No deployment, release, registry-administration, or publishing authority is implied.

For a common mixed-clue case, `bun.lock` establishes lockfile evidence, while `"start": "node server.js"` is only a declared command; neither alone proves what actually ran. The invoked wrapper/runtime, package boundary, and effective TypeScript program answer separate questions. [Project Structure](reference/project-structure.md) gives a worked interpretation, including checker membership, coverage denominators, dependency metadata, and packed-subpath failures.

## Planning Context

The [reference index](reference/README.md) routes structural questions to focused notes, not executable workflows. A project-specific plan depends on its source evidence, stated outcome, and authorized scope; unresolved facts remain assumptions or questions rather than invented requirements. [Planning Boundaries](reference/planning-boundaries.md) illustrates how ambiguous “release ready” requests can resolve to different outcomes without implying order or bundled authorization.

The associated project-mechanics reference is `node-project-reference -> #shared-project-mechanics-reference`. It describes technical details; this planning context describes how those layers and outcome boundaries relate. Neither reference chooses a project stack or transfers authority.

For executable, source-based plan production, the existing `plan-writer` operation remains the owner. Persisted analysis and relevant evidence can proceed through its analysis-to-plan path when sufficient; proposal-specific authorization applies only to the proposal-derived path defined by its own contract. No separate active planner, formal decision owner, or approval gate is created here.

## Passive Contract

This planning-class skill provides structural knowledge only. It defines no execution steps, commands, tools, writes, task generation, verification selection, delegation, approval, or completion authority. Its presence or use does not establish that project planning or implementation occurred.

## Docs

See [Reference Index](reference/README.md) for the focused structural context and its limits.
