# Planning Boundaries

## Purpose

Explain how TypeScript project concerns and candidate outcomes relate, how a compressed request resolves, and which owner answers a requested change, without assigning an implementation procedure, command selection, or project-specific requirements.

## Provisional Outcome Distinctions

- **Production behavior:** changes to an application's, service's, CLI product's, or library's behavior. Directly coupled regression tests may belong with that change when the applicable operation contract says so. The current owner is `node-project-writer -> #production-behavior-change-workflow`.
- **Test-only work:** tests, fixtures, helpers, or test layout without production-source edits. Exposing a defect does not itself authorize a production fix. The current owner is `node-project-test-writer -> #test-only-change-workflow`.
- **Dependency/environment work:** decisions about dependencies, manager/runtime declarations, lockfiles, installation, or environment. A decision and its possible mutations are distinct; scope and authorization come from the applicable contract. The current owner is `node-project-dependencies -> #dependency-decision-and-environment-workflow`.
- **Standalone quality work:** quality diagnostics or requested quality configuration. Check-only evidence differs from source mutation, and neither automatically includes remediation. The current owner is `node-quality-workflow -> #standalone-quality-workflow`.
- **Package artifact/consumer work:** package metadata, build artifacts, package contents, and consumer-facing entry-point or installation evidence. This is distinct from application deployment, registry administration, release governance, and publication. The current owner is `node-package-distribution -> #package-artifact-and-consumer-workflow`.

These five names are the bounded provisional family roster for this work, not a universal skill count, stack, or task-orchestration rule. Each possible outcome can depend on several technical layers; no single tool or framework name determines ownership. A request spanning outcomes does not by itself define how to delegate or sequence them.

## Question To Owner Routes

Each route pairs a discriminating question with the owner whose contract answers a change request and the page that holds the mechanics. A route is navigation only: it creates no delegation, sequence, permission, or execution step.

- **Which runtime ran, and what processed the source?** A `.ts` entry point, a green check beside a failing run, or a specifier that resolves for the checker but not the loader asks a mechanics question. [Runtime And Source Processing](project-structure.md#runtime-and-source-processing) summarizes the clues; the canonical mixed-clue chain is at `node-project-reference -> reference/runtime-and-project-structure.md#reconcile-mixed-runtime-clues`.
- **Why is a changed `.ts` file absent from a green check?** The quality owner answers: `node-quality-workflow -> #standalone-quality-workflow`, with its missing-file diagnosis at `node-quality-workflow -> reference/quality-scope-and-mutation.md#diagnose-a-changed-file-missing-from-a-green-check`. The shared distinction between program membership and a successful check is at `node-project-reference -> reference/quality-scope-and-tool-effects.md#compiler-program-membership-compared-with-a-successful-check`.
- **Does a packed subpath import?** The package owner answers: `node-package-distribution -> #package-artifact-and-consumer-workflow`, with the ordered four-layer diagnosis at `node-package-distribution -> reference/consumer-resolution-and-declarations.md#diagnose-a-packed-subpath-in-four-ordered-layers`.
- **Which dependency role applies?** The dependency owner answers: `node-project-dependencies -> #dependency-decision-and-environment-workflow`, with the no-add, add, replace, or defer decision at `node-project-dependencies -> reference/evaluation-and-environment-changes.md#choose-no-add-add-replace-or-defer` and manager-defined groups and roles at `node-project-dependencies -> reference/manager-semantics-and-workspace-placement.md`.
- **Does a change alter a public API?** The production owner answers: `node-project-writer -> #production-behavior-change-workflow`. The style consequence is at `node-source-style-guide -> reference/source-style-guidance.md#public-api-and-runtime-contracts`, and the public-compatibility boundary is at `node-project-reference -> reference/source-and-api-conventions.md#public-compatibility-boundaries`.
- **Is this a repository utility?** Utilities under `scripts/node/` route to `skill-script-node-writer -> #procedure`; their tests route to `skill-script-node-test-writer -> #procedure`. A repository utility is not automatically a general CLI product, and its conventions are not project defaults.
- **Is an executable plan required?** Executable source-based plan creation and bounded correction belong to `plan-writer -> #planning-and-task-authoring`; a proposal-derived path keeps its own authorization transition.

## Evidence Relationships

Relevant context may include the target package and workspace root, runtime(s) and versions, manager and lockfiles, module and TypeScript configuration, framework and adapter, checker/build/test tools, effective commands, emitted outputs, and the consumer runtime. Only facts that bear on the requested outcome need to be established. A manager choice does not imply runtime choice; a framework name does not establish its adapter or emitted target; and a tool's declared support is not project-specific execution evidence.

Potential evidence has bounded meanings. A type-check result concerns its selected program and checker configuration. A test result concerns the runner, runtime, and exercised cases. A build result concerns that build and output. Consumer installation or execution is separate evidence when relevant. None implies success on untested runtimes, versions, adapters, or dependency graphs.

When clues appear to conflict, first ask whether they describe the same layer. A `bun.lock` beside a `"start": "node server.js"` script is not inherently inconsistent: one concerns manager state and the other a declared launch command. The actual wrapper, working directory, and command determine which script ran; Bun's launcher can respect a Node shebang or explicitly override it with `--bun`. Likewise, a passing `tsc` command says nothing about a changed file until the selected config and effective program are known. This framing avoids both overclaiming from a lockfile and dismissing valid Node-targeted work just because Bun is present.

### Reading A Surprising Result

Some common observations have multiple plausible causes, so planning context should distinguish what the observation proves from what it leaves open:

- **Green type-check, changed file absent:** The successful process completed for its selected program, but absence from the effective TypeScript file list means that program did not check the file. Package/config selection, explicit CLI file arguments, `include`, imports, and project references are possible discriminators; it does not establish that another tool omitted the file too. The full diagnosis is the quality owner's: `node-quality-workflow -> reference/quality-scope-and-mutation.md#diagnose-a-changed-file-missing-from-a-green-check`.
- **Coverage percentage changed after a test move:** The aggregate changed, but that alone does not establish a behavior regression. Discovery, imported modules, coverage provider, source roots, filters, and denominator may have changed. c8's loaded-file default and Node v26.13.0's experimental built-in coverage have different documented controls, so provider identity matters. The canonical drift diagnosis is at `node-project-test-writer -> reference/collection-isolation-and-coverage.md#diagnose-a-coverage-drop-after-moving-a-test`.
- **Packed subpath import fails:** A missing tarball file, an undeclared `exports` path, a module loader or format error under the consumer runtime, and missing TypeScript declarations are distinct failures, so a Node runtime error such as `ERR_PACKAGE_PATH_NOT_EXPORTED` is not evidence of a declaration problem. The ordered diagnosis is at `node-package-distribution -> reference/consumer-resolution-and-declarations.md#diagnose-a-packed-subpath-in-four-ordered-layers`.

These distinctions identify which evidence is still needed; planning context holds no full troubleshooting procedure or command choice. The relevant project and tool versions, effective configuration, and actual consumer determine what a particular result means.

## Clarifying Combined Requests

Before interpreting a phrase, state two things separately: the requested result — the observable outcome the requester wants — and the authorized effects — the files, environment, artifact, or external state that a change may touch. Ask the requester when a different reading would change the scope, including a different outcome label, a wider set of files or environment changes, or the inclusion of publication or deployment.

Phrases such as “make the package release ready” compress materially different outcomes. A useful planning distinction is the requested result and its authorized boundary, not an assumed workflow order:

- If the requester means “fix the API behavior,” the outcome is production behavior. Whether directly coupled regression tests belong with it depends on the applicable operation contract.
- If the requester means “confirm consumers can import the packed subpath,” the outcome is package artifact/consumer validation. That does not imply changing dependencies, publishing to a registry, or deploying an application.
- If the requester means “select the install toolchain,” the outcome is a dependency/environment decision about the manager and runtime, and it is separate from actually installing or rewriting the lockfile.
- If the requester means “refresh the lockfile,” that is an authorized environment effect under dependency work, not a consequence of the release-ready phrase. The manager and runtime remain separate decisions unless both are expressly in scope.
- If “release ready” means all of those, each distinct outcome and its permitted changes need explicit scope. The phrase alone does not authorize bundled edits, choose an order, or create an orchestration contract.

**Scope diagnostic:** the requested result and the authorized effects can disagree. A request to validate packed imports that would require republishing, or a toolchain upgrade that would rewrite a lockfile, changes the request's scope, so the mismatch is a question rather than an assumed permission or sequence.

If the request is unclear, the material planning question is which result is sought—behavior, tests, dependency state, quality evidence, or packed-consumer evidence—and whether publishing/release actions are requested separately. An executable source-based plan remains owned by `plan-writer`; this context identifies boundaries and unknowns but does not create tasks or a plan.

## Planning And Ownership Handoffs

This reference may help identify structural assumptions for design or plan authoring. It does not formulate project-specific requirements, choose verification commands, produce tasks, sequence implementation, or authorize any change. A descriptive relationship between outcomes is not an imperative handoff, and a route creates no delegation, permission, or execution step.

Executable source-based plan creation and bounded plan correction remain with `plan-writer -> #planning-and-task-authoring`. Persisted analysis and relevant evidence may be handed to that operation directly when sufficient. A proposal-derived path has its own authorization transition; that condition does not become a general prerequisite for Node/Bun planning. This family adds no active planner, formal decision owner, or approval gate.

## Scope Exclusions

- **TypeScript-only scope.** The family covers TypeScript source, configuration, declarations, tests, quality diagnostics, package artifacts, and API documentation comments on exported declarations in Node.js or Bun projects. Node.js and Bun runtime, module, loading, and emitted-JavaScript mechanics appear only where they explain how TypeScript source executes, emits, resolves, declares, or reaches a consumer.
- **Authorization-named ancillary files only.** An authorized change covers the TypeScript surface plus only the manifests or configuration that the authorization names. JavaScript source edits are reported as out of scope, and a JavaScript-only request is reported as out of scope rather than answered with TypeScript guidance. Standalone JavaScript source guidance, JavaScript or mixed-language eligibility, JavaScript checking (`allowJs`, `checkJs`), and JSDoc typing of `.js` files are excluded.
- Repository utilities in `scripts/node/` remain with their existing script-specific contracts; a general CLI product is not automatically a repository utility.
- No universal Node/Bun dual-runtime requirement, compatibility matrix, tool default, framework preference, or project layout is specified.
- No deployment, release, registry-administration, publication authority, or organization-wide security policy is implied.
