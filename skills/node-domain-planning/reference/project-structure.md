# Project Structure

## Purpose

Describe the project dimensions that may relate to a planning question about a TypeScript project in Node.js or Bun. The relevant subset depends on the requested outcome and evidence; no project is presumed to use every layer. This page is passive structural context: it states relationships and limits, creates no task, sequence, approval, or execution step, and supplies no project-specific assessment or executable plan. JavaScript-only guidance, JavaScript or mixed-language eligibility, JavaScript checking options, and JSDoc typing of `.js` files are out of scope; a JavaScript-only request is reported as out of scope. An authorized change covers the TypeScript surface plus only the manifests or configuration its authorization names, and JavaScript source edits are reported as out of scope. Node.js and Bun runtime, module, loading, and emitted-JavaScript mechanics appear only where they explain how TypeScript source executes, emits, resolves, declares, or reaches a consumer. Outcome routing is in [Planning Boundaries](planning-boundaries.md).

## Runtime And Source Processing

Node.js and Bun are separate execution targets. Bun can be a package manager or command runner without being the application's runtime. TypeScript source processing also has separate dimensions: runtime type stripping or transpilation, static type checking, module resolution, JavaScript or declaration emission, and bundling. For example, the documented Node.js v26.13.0 native TypeScript path strips erasable syntax without checking types and ignores `tsconfig.json`; Bun's runtime transpiles TypeScript, but ordinary execution also does not check types ([Node.js v26.13.0 TypeScript modules](https://nodejs.org/download/release/v26.13.0/docs/api/typescript.html), [Bun runtime](https://bun.com/docs/runtime)). These versioned or documented examples are not parity tests or universal claims about every release.

Module mode, package boundaries, runtime version, and TypeScript configuration shape what is accepted and what loads. A checker may model one resolver while the actual runtime or artifact consumer uses another. A green check therefore answers only for the checked program, tool, and configuration; it does not prove runtime or artifact compatibility.

### Interpreting Mixed Runtime And Check Evidence

A lockfile, a package script, a TypeScript configuration, and a green test command answer different questions. In a repository containing `bun.lock`, a `"start": "node server.js"` script, `packages/api/tsconfig.json`, and a green test command, the lockfile describes manager state, the script describes a declared command, the configuration describes a possible checker scope, and the test result describes the runner's selected tests and assertions. None alone establishes the others. The canonical worked case, including launcher and module-format detail and the limit of each clue, is `node-project-reference -> reference/runtime-and-project-structure.md#reconcile-mixed-runtime-clues`; this page keeps only the summary.

The meaningful unresolved facts are the package or workspace script actually invoked, its working directory and wrapper, the runtime and version that executed it, and the effective checker configuration and file set. If these facts are unavailable, the structure supports a question or assumption, not a claim that the repository is Node-only, Bun-compatible, or fully type-checked.

### File Presence Compared With Program Membership

A `.ts` file can exist under a package and still be outside the selected checker program. This configuration selects only `src/index.ts`, and `src/generated/client.ts` is neither listed nor imported by a program file:

```json
{
  "compilerOptions": {
    "strict": true,
    "noEmit": true
  },
  "include": ["src/index.ts"]
}
```

`tsc --listFilesOnly --project tsconfig.json` omits `src/generated/client.ts` even though the file exists. Presence in the repository is not program membership. Explicit source-file arguments bypass `tsconfig.json`; `--project` selects a config, and `--showConfig` and `--listFilesOnly` expose effective settings and program membership. `include` patterns are relative to the config, and `exclude` only prevents discovery through `include`: imports, `files`, `types`, and triple-slash references can still bring a file into the program ([TypeScript CLI](https://www.typescriptlang.org/docs/handbook/compiler-options), [TSConfig reference](https://www.typescriptlang.org/tsconfig/)).

The diagnostic is asymmetric: a listed file establishes compiler-program membership, not successful completion or runtime correctness; an absent file establishes that this TypeScript program did not check it, not that another checker or test transform also omitted it. A passing check and each emitted artifact are separate evidence.

## Packages And Workspaces

Package manager, lockfile, workspace membership, local package linking, and runtime selection are separate concerns. Before reading any of them, record the effective package or workspace root, the manager, and its version: npm, pnpm, Yarn generations, and Bun differ in workspace declaration, lockfile, linking, and task-graph behavior, and shared manifest fields do not guarantee common semantics. A workspace declaration does not establish equivalent membership across managers, and two lockfiles establish competing repository evidence rather than which manager the team intends to use. A lockfile is a manager-specific resolution record, not an installer guarantee and not a statement of which runtime executes the application.

Manager-specific facts are owned by the dependency operation:

- Dependency groups and peer resolution: `node-project-dependencies -> reference/manager-semantics-and-workspace-placement.md#dependency-groups-and-peer-mechanics`
- Lock and install guarantees by manager and command: `node-project-dependencies -> reference/manager-semantics-and-workspace-placement.md#lock-and-install-guarantees-by-manager-and-command`
- Workspace membership and placement: `node-project-dependencies -> reference/manager-semantics-and-workspace-placement.md#workspace-declarations-do-not-establish-equivalent-membership`

Changes to dependencies, manifests, lockfiles, or the environment belong to that operation and its authorization.

Packed-consumer facts are different again. What a package delivers, which files an archive contains, and which entry points and declarations a consumer receives belong to the package owner: start from `node-package-distribution -> reference/artifact-and-consumer-boundaries.md`. A workspace symlink or `file:` link resolves to the source tree, so it is not evidence about the packed artifact. Runtime and invocation interpretation remains the shared reference's question; the canonical mixed-clue case is linked above.

## Toolchain And Framework Layers

Checking, testing, linting, formatting, transformation, compilation, bundling, and package production may be combined in a product interface but remain distinct evidence. A test runner's TypeScript support may transform files without type-checking. A build's output format, declarations, package conditions, external dependencies, adapter, and consumer runtime determine which later compatibility questions apply.

The distinction matters when a command appears green. `tsc` can check a selected program without producing the package artifact; a transformer can emit JavaScript without checking types; and a bundler can produce output whose external dependencies or module format still fail in the target runtime. “Build passed” is therefore incomplete evidence until the task identifies what the command checks or emits and who consumes that output. Tool documentation explains a tool's stated behavior, but does not show that the project's wrapper selected the expected config or that the resulting artifact works in an untested runtime.

Coverage has a similar denominator issue. c8 documents a default based on files loaded by V8; its `--all` option includes matching files in configured source directories and treats uncovered files as zero. Node.js v26.13.0 documents a distinct built-in coverage interface behind `--experimental-test-coverage`, marked experimental, with its own include and exclude controls. If a moved test changes a reported percentage, the plausible explanation may be a changed discovered-test set or measured source universe rather than changed behavior. Those observations do not establish a cause without the provider and version, source roots, patterns, loaded modules, and before and after test discovery; c8's README is rolling and its defaults must not be transferred to Node or another provider ([c8 documentation](https://github.com/bcoe/c8), [Node.js v26.13.0 test coverage](https://nodejs.org/api/test.html#collecting-code-coverage)).

Framework, UI library, build tool, server engine, adapter or preset, rendering mode, and runtime are also distinct. Examples such as Next.js, SvelteKit, Nuxt/Nitro, Astro, React Router, Express, Fastify, Hono, and Elysia illustrate different structures; they do not imply that every project is a server or uses a framework. Framework compatibility claims must remain scoped to documented version, mode, adapter, and output.

### Build Evidence Separates Command, Output, And Consumer

A `.ts` entry point can be reached through three different paths, and each produces different evidence:

- Node's native TypeScript path can run the entry directly, stripping types under the selected Node version without a type check.
- A TypeScript build can check that same entry against a selected program and emit JavaScript for a declared target; its success establishes that program and those files, not that a host loads them correctly.
- A host runtime loads that emitted output under its own version, conditions, and module resolution; that load is separate again.

For a framework build, record one bounded trace: the command and selected mode; the build-time runtime; the configured output target or adapter preset, such as Bun's bundler `target` or a Nitro preset for Node or Bun; and the consuming runtime. Each is a separate fact, and none implies the others. These paths are separate evidence stages, not a prescribed workflow or an implicit pipeline. The examples are version-bounded illustrations, not selected stacks: Bun's bundler page labels v1.4.4 and defines `target` as the intended execution environment, and Nitro documents separate Node and Bun presets ([Bun bundler](https://bun.com/docs/bundler), [Nitro Node.js](https://nitro.build/deploy/runtimes/node), [Nitro Bun](https://nitro.build/deploy/runtimes/bun)). The invocation-to-consumer chain is interpreted in `node-project-reference -> reference/framework-output-and-consumers.md`.

## Vite Boundary

This family does not select or prescribe Vite as a tool or default, and does not describe workflows that invoke or rely on Vite. The following are bounded documentation or package-metadata snapshots, not an exhaustive framework audit or runtime tests. The version values below are baseline carry-forward values that were not re-verified for this page; the no-Vite boundary does not depend on them.

- **SvelteKit v3:** inspected v3 project-structure documentation requires Vite for project setup; the separate registry snapshot identifies `@sveltejs/kit@3.1.1`. This setup evidence does not say the Kit package itself has a Vite runtime dependency.
- **Astro v7:** inspected documentation describes Vite as the development server and production bundler. Registry metadata for `astro@7.3.5` lists Vite as a normal dependency, while the documentation reported 7.4.5 as latest. The 7.4.5 package manifest was not inspected, so the discrepancy is unresolved.
- **React Router v8 Framework Mode:** inspected v8 documentation uses a Vite plugin; `@react-router/dev@8.5.1` lists Vite as a peer dependency. Do not generalize the v8 mode requirement to every v7 installation or equate a peer edge with a regular dependency.
- **Vitest:** inspected `vitest@4.1.12` metadata lists Vite as a regular dependency and required peer; `vitest@5.0.5` lists it as a required peer rather than a regular dependency. Both are Vite-dependent runner/toolchain snapshots, even if the application uses another build path.
- **Nuxt 4.6.4:** inspected metadata shows Nuxt → `@nuxt/vite-builder@4.6.4` → Vite as a transitive package path. Selecting another builder does not establish that the resolved installation omits Vite.
- **Next.js 16.3.4:** the inspected default path uses Turbopack and its package manifest omits Vite; this is not an audit of every dependency in a consuming project's graph.
- **Standalone Nitro v3:** inspected v3 documentation describes Rolldown as default and Vite as selectable; v3 release-candidate metadata lists Vite in devDependencies, not normal published dependencies. This does not establish stable Nitro v2 behavior or Nuxt's separate graph.

The inspected Express, Fastify, NestJS, Hono, and Elysia package graphs were not audited for Vite; their status is unknown, not Vite-free. Incidental transitive presence does not establish direct selection, while absence from a direct command does not make a Vite-reliant workflow no-Vite. No blanket transitive dependency ban or project graph-absence claim follows; such a claim would require exact project versions and resolved-tree evidence. Documentation and registry snapshots can differ or change over time, and direct setup, selected builder, peer dependency, regular dependency, and transitive package path are distinct evidence.

## Conditional Concerns And Evidence Limits

Security and configuration, observability, concurrency, reliability, and public source and API compatibility may matter when the request and evidence make them relevant. They do not form a universal checklist or organization-wide policy. Package artifact validation is not publication or deployment authority.

Publisher and maintainer documentation and package metadata are point-in-time evidence, often version-sensitive. They are not runtime experiments, a resolved dependency audit for a particular repository, a universal support matrix, or proof that distinct tools interoperate. Examples on this page are version-bounded documentation or metadata, not audits, tests, or support claims. Preserve unknowns where the project's sources do not establish them, and claim no compatibility result beyond the cited version, mode, and configuration.

### Dependency Claims And Evidence Weight

Manifest fields narrow a question; they do not substitute for evidence at the intended runtime. For example, npm v12 documents dependency `engines` as advisory unless `engine-strict` is enabled; optional dependency installation can fail without failing the whole install, leaving application code responsible for handling absence. Bun's rolling install docs describe its own peer-install and lifecycle-script trust behavior, which is not proof that npm and Bun produce equivalent installed trees ([npm package.json, CLI v12](https://docs.npmjs.com/cli/v12/configuring-npm/package-json/), [Bun install](https://bun.com/docs/pm/cli/install)).

In a hypothetical candidate with the needed API, an `engines.node` declaration, an optional native package, and an install or build script, these facts mean “declared Node range,” “install may tolerate missing optional package,” and “manager-dependent script behavior”—not “works on the target runtime.” An absent Bun-support statement is also not proof of incompatibility. The remaining decision may depend on exact package and version source, manager and version, platform and native artifact, and a test in the intended consumer. Until those are known, deferral is an evidence-limited planning disposition, not a general policy against the dependency.

### Package Subpath Failure Layers

A packed consumer failing to import `pkg/feature` has four ordered but independent evidence layers: whether the archive actually contains the intended target; whether the exact specifier is exposed by the package `exports` map for the active consumer condition; whether the selected target exists and its module format loads under the consumer runtime; and whether TypeScript declarations resolve for that consumer's compiler and resolution mode. An earlier pass does not clear a later layer, and a runtime import cannot stand in for typed consumption. The canonical ordered diagnosis, its diagnostics, and its worked examples are owned by `node-package-distribution -> reference/consumer-resolution-and-declarations.md#diagnose-a-packed-subpath-in-four-ordered-layers`; this page keeps only the cross-layer summary. No publication, artifact repair, or deployment authority follows.

### Ownership And Passive Boundary

This page is passive structural context. Project-specific assessments and executable plans are outside it. Changes and validation remain with the operation owners and their contracts — `node-project-writer`, `node-project-test-writer`, `node-project-dependencies`, `node-quality-workflow`, and `node-package-distribution` — while executable source-based plans remain with `plan-writer` and outcome routing is in [Planning Boundaries](planning-boundaries.md). The repository's `scripts/node/` utilities keep their separate route, and nothing here forms an implicit pipeline or a compatibility promise.
