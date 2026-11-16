---
name: node-package-distribution
description: "Use when building or validating package artifacts and consumer-facing entry points for a TypeScript package built for Node.js or Bun."
selection:
  role: owner
  tags:
    actions: [build package artifacts, validate package consumers]
    inputs: [TypeScript Node.js or Bun package, artifact or consumer request]
    outputs: [artifact validation evidence, package consumer report]
    topics: [package contents, entry points, declarations, tarballs]
    environments: [TypeScript Node.js package, TypeScript Bun package]
    constraints: [bounded artifact scope, no implied publication authority]
  use_when:
    - a request asks to build or inspect a package artifact or validate its consumer-facing interface
  not_for:
    - changing package dependencies, manager/runtime selection, or installation state
    - changing production behavior or writing tests as the primary outcome
    - deploying an application or publishing to or administering a registry
    - repository scripts/node/ utilities or their tests, which belong to skill-script-node-writer or skill-script-node-test-writer
    - JavaScript-only or mixed-language package requests
class: operation
---

# Package Artifact And Consumer Workflow

Own requested package build, pack, artifact inspection, and consumer-facing validation for TypeScript packages built for Node.js or Bun. The scope is TypeScript-only. Route by the requested outcome, not by the presence of a manifest or use of a particular build tool. TypeScript API documentation comments on exported declarations are in scope; Node.js and Bun runtime, module, loading, and emitted-JavaScript mechanics appear only where they explain how TypeScript source executes, emits, resolves, declares, or reaches a consumer. Standalone JavaScript source guidance, JavaScript or mixed-language eligibility, JavaScript checking (`allowJs`, `checkJs`), and JSDoc typing of `.js` files are out of scope, and a JavaScript-only request is reported as out of scope.

An authorized change covers the TypeScript surface and only the manifests or configuration the authorization names. Report JavaScript source edits as out of scope rather than broadening them into mixed-source authoring.

Keep production behavior, test-only work, dependency and environment changes, and standalone quality work with their respective owners. Repository `scripts/node/` utilities and their tests route to `skill-script-node-writer` or `skill-script-node-test-writer`, not to this operation. This scope does not imply application deployment, release governance, publication, registry administration, or organization-wide security policy.

## Normalize Input

Identify the target package and workspace, requested artifact or consumer outcome, effective runtime and module targets, package metadata and build commands, allowed paths/effects, and requested verification. Repository access does not authorize installation, lockfile changes, publication, or destructive cleanup. Ask when missing scope or permission could materially change the artifact or consumer result.

## Procedure

1. **Inspect the effective package contract.** Establish package/workspace root, manager and runtime separately, build and pack scripts, module format, entry points and conditions, declaration outputs, included files, ignore rules, and the intended consumer/runtime. Use the package's actual versions and commands; do not infer the complete target from a root manifest or framework name.
2. **Bound the artifact work.** Preserve existing package metadata and supported consumer interfaces. Determine whether the request concerns build output, packed contents, local artifact installation, or specified entry-point behavior. Do not silently change dependencies, lockfiles, public exports, release policy, or registry settings. Treat a request to publish or administer a registry as outside this owner.
3. **Build or inspect only as authorized.** Run the project-configured build or pack command when permitted. Lifecycle hooks such as `prepare` or `prepack` can generate files or otherwise affect the tree; inspect relevant scripts before running them. Prefer a dry-run contents listing when that answers the request, and distinguish it from creating a tarball. Do not clean or overwrite generated files without permission.
4. **Validate the requested consumer surface.** Compare the artifact's actual files and package metadata with declared entry points, subpaths, formats, and declarations. When requested and authorized, install the produced tarball into an isolated consumer fixture and exercise the specified imports or requires under the intended runtime. A linked working tree or passing source tests is not equivalent to consuming the packed artifact. For a failing subpath, follow the ordered four-layer diagnosis in [Consumer Resolution And Declarations](reference/consumer-resolution-and-declarations.md#diagnose-a-packed-subpath-in-four-ordered-layers) before assigning a cause. Limit checks to the requested formats, conditions, subpaths, runtimes, and versions; do not claim broader compatibility.
5. **Report evidence and limits.** Record exact commands, package and consumer scope, versions when known, output paths, packed-file evidence, entry points exercised, and results. Separate build success, tarball contents, local consumer behavior, declaration resolution, registry behavior, and untested compatibility. Report mutations and cleanup, and identify skipped or unavailable checks without expanding into publication or deployment.

For the delivered package contract, file selection and archive evidence, and consumer resolution or declaration questions, start at [Package Artifact And Consumer References](reference/README.md); the three detail pages under [Docs](#docs) own those mechanisms.

## Self-Validation

- Work is limited to the authorized package artifact or consumer outcome.
- Package manager and runtime are distinguished, and claims match the actual target evidence.
- Artifact contents, local consumer behavior, and declaration resolution are reported separately from each other and from source-tree checks.
- Version, tool, and fixture limits are explicit; no implicit compatibility promise is made.
- No unauthorized dependency, release, registry, publication, deployment, or unrelated source changes occurred.
- No workflow selects or relies on Vite; incidental transitive presence is not treated as direct selection or proof of graph absence.

## Expected Output

Return the requested artifact outcome and a concise report of package scope, changed paths, exact build/pack/consumer checks and results, target assumptions, and remaining gaps. If blocked or unchanged, state why and the bounded next step.

## Docs

- [Package Artifact And Consumer References](reference/README.md) — concern-based index for this workspace.
- [Artifact And Consumer Boundaries](reference/artifact-and-consumer-boundaries.md) — delivered contract, build, pack, and publish separation, consumer evidence scope, and registry limits.
- [Pack Preview And Archive Contents](reference/pack-preview-and-archive-contents.md) — preview versus archive, file selection, lifecycle effects, and the packing layer.
- [Consumer Resolution And Declarations](reference/consumer-resolution-and-declarations.md) — four-layer packed-subpath diagnosis, export branches, and declaration resolution.
