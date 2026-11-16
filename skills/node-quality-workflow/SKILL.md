---
name: node-quality-workflow
description: "Use when configuring or running standalone code-quality checks for a TypeScript Node.js or Bun project."
selection:
  role: owner
  tags:
    actions: [configure quality checks, run quality diagnostics]
    inputs: [TypeScript Node.js or Bun project, quality request]
    outputs: [bounded quality configuration or diagnostic report]
    topics: [type checking, linting, formatting, file scope, program membership]
    environments: [Node.js project, Bun project]
    constraints: [standalone quality outcome, TypeScript source scope, separate diagnostic and mutation modes]
  use_when:
    - a request is limited to type checks, lint, or formatting for TypeScript source in a Node.js or Bun project
  not_for:
    - a JavaScript-only request, including JavaScript checking or JSDoc typing of JavaScript source
    - production behavior changes, test-only changes, dependency or runtime environment changes, or package artifact validation
    - this repository's scripts/node/ utilities and their repository-specific conventions
class: operation
---

# Standalone Quality Workflow

Own standalone quality configuration and diagnostic requests for TypeScript Node.js and
Bun projects. The subject is TypeScript source, TypeScript configuration, declaration
output, and TypeScript quality diagnostics in those projects, including diagnostics over
TypeScript test files. A JavaScript-only request is reported as out of scope rather than
answered with TypeScript guidance, and JavaScript or mixed-language eligibility,
JavaScript checking, and JSDoc typing of JavaScript source are out of scope. Do not infer
the execution runtime from TypeScript syntax, package manager, framework name, or
repository path.

Authority covers TypeScript surfaces plus only the manifests and configuration named in
the authorization. JavaScript source edits are out of scope and are reported as such.

Keep production behavior, test-only work, dependency/environment changes, and package
artifact work with their respective outcome owners. Existing `scripts/node/` utilities
remain a separate repository-specific route; do not transfer their tool choices or
defaults to ordinary projects.

## Routing Boundaries

- A request to inspect, configure, or run type-checking, lint, or format diagnostics
  without unrelated outcomes belongs here.
- If diagnostics reveal a source defect, report it; do not repair production or test
  behavior under standalone quality ownership. Source repair belongs to
  `node-project-writer`.
- A request to add or change quality-tool dependencies, lockfiles, or runtime selection
  belongs with `node-project-dependencies`.
- A request whose main outcome is writing tests or interpreting test and coverage results
  belongs with `node-project-test-writer`, even if a quality check is also mentioned.
- A request whose main outcome is building, packing, or validating package artifacts
  belongs with `node-package-distribution`.
- Work on this repository's `scripts/node/` utilities belongs with
  `skill-script-node-writer` or `skill-script-node-test-writer`.
- For a no-Vite request, do not select Vite or rely on a Vite-based workflow. An
  incidental dependency edge is not by itself proof of direct selection; do not claim
  dependency-graph absence without project-specific resolved-tree evidence.

## Normalize Input

Identify the project and effective package/workspace scope, requested quality result,
target runtime(s) if relevant, allowed paths and effects, existing tools/configuration,
project commands, and requested evidence. Confirm that the requested targets are
TypeScript surfaces and that any accompanying manifest or configuration edit is named in
the authorization. Repository access alone does not authorize edits, installs, or source
fixes. Ask when an unknown target, quality mode, or permitted effect could materially
change the work.

## Procedure

1. **Inspect the effective project scope.** Read repository instructions, relevant
   manifests and scripts, manager/runtime selectors, quality configuration, TypeScript
   project configuration, ignore and file-selection rules, workspace boundaries, and
   applicable CI commands. Establish the actual invocation and versions when available.
   Do not infer coverage from a repository root, filename extension, or one config file
   alone. When a changed file appears absent from a passing TypeScript check, trace the
   package script and working directory, then inspect the effective compiler config and
   file list before interpreting the pass; see
   [Quality Scope And Mutation](reference/quality-scope-and-mutation.md#diagnose-a-changed-file-missing-from-a-green-check).
2. **Separate the quality responsibilities and establish TypeScript program membership.**
   Determine which requested checks are type checking, linting, formatting, or a
   configured combination. A runtime's TypeScript execution or a transform does not itself
   establish type checking unless the invoked tool explicitly enables a checking mode.
   Typed lint rules remain linting, not proof of a complete compiler check. Then determine
   whether each authorized target is a member of the TypeScript program that the invoked
   compiler check uses: a file can receive typed-lint diagnostics while a compiler file
   list omits it, and a program member need not be selected by a lint or format command.
   Type information supplied by a lint tool's own mechanism does not establish program
   membership. Read-only `--showConfig` and `--listFilesOnly` probes over the project's own
   invocation expose the resolved configuration and file list; see
   [Quality Scope And Mutation](reference/quality-scope-and-mutation.md#establish-the-actual-target-set).
3. **Resolve scope and effects.** Determine what each command includes based on its own
   CLI, config, cwd, references, ignores, and tool version. Distinguish read-only scope
   probes and diagnostic/check-only invocation from formatter rewrites, lint fixes, or
   other writes. Use non-mutating modes for diagnostics where available; never infer file
   scope or write behavior from a command label such as `check` or `lint`. For ESLint,
   Biome, and Prettier target expansion, configuration discovery, ignore rules, and the
   no-files-matched case, see
   [Lint And Format Target Selection](reference/lint-and-format-target-selection.md).
4. **Make only the authorized quality change or run.** Preserve existing project
   conventions and scope. Change only the specifically authorized quality configuration,
   and only the manifests or configuration the authorization names. Before any rewrite or
   fix, confirm that the mutation is explicitly within scope and identify the affected
   paths. Do not add or update dependencies, alter lockfiles/runtime selection, remediate
   source or tests, modify package artifacts, or create universal thresholds as incidental
   work. If a requested workflow would rely on Vite, do not treat it as a no-Vite
   workflow.
5. **Validate and report the bounded result.** Review the exact diff and identify each
   command, tool/version when known, working directory, selected project/files, program
   membership where relevant, check or mutation mode, and outcome. Distinguish pass, fail,
   skipped, unavailable, and inconclusive evidence. A clean result over an empty or
   unintended target set does not establish a check of the intended source. Report scope
   gaps and pre-existing issues without claiming a full project, runtime, or compatibility
   guarantee.

## Self-Validation

- The work stays within an explicitly requested standalone quality outcome on TypeScript
  surfaces.
- Type checking, linting, formatting, and any combined command are described according to
  their configured roles.
- TypeScript program membership, effective file/project scope, and check-versus-write
  effects are reported rather than inferred from command names.
- No JavaScript source edit, production, test, dependency/environment, package-artifact, or
  `scripts/node/` change was made outside authorization.
- Tool/version and runtime claims remain bounded by available project evidence; no
  universal stack, gate, or compatibility promise is implied.

## Expected Output

Return the bounded quality change or diagnostic result, program membership where relevant,
scope and tools examined, exact commands and modes, changed paths or none, and validation
evidence. State failures, skipped or unavailable checks, unresolved scope, and next
bounded action. Do not claim correctness beyond the checks actually run or coverage of
files the invocation did not select.

## Docs

- [Reference index](reference/README.md) — navigation for this workspace's supporting
  reference.
- [Quality Scope And Mutation](reference/quality-scope-and-mutation.md) — checker, linter,
  formatter, and transform role separation, TypeScript program membership, the
  missing-file diagnosis, check-versus-write semantics, and evidence limits.
- [Lint And Format Target Selection](reference/lint-and-format-target-selection.md) —
  per-tool target expansion, configuration discovery, ignore rules, and no-files-matched
  behavior for ESLint, Biome, and Prettier.
