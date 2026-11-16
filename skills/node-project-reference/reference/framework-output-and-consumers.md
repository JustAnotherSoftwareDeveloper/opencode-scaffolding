# Framework Output And Consumers

## Scope

This page answers what a framework build emitted, for which runtime, and who consumes it. It owns the invocation-to-consumer chain for framework and application output: which command ran, which mode and build-time runtime it used, which adapter or preset shaped it, which files and declared target it produced, and which runtime, host, or package consumer receives the result.

The subject is TypeScript source, configuration, declarations, and output in Node.js or Bun projects. JavaScript-only work is out of scope, and this page excludes JavaScript eligibility, `allowJs` and `checkJs` guidance, JavaScript diagnostics, and JSDoc typing of `.js` files. The page states passive mechanisms and interpretation; changing framework configuration, build scripts, or dependencies belongs to an outcome owner. Every claim stays with the named product, version, mode, and configuration it came from, because the cited pages are rolling or version-scoped and either kind can change.

The framework, adapter, and build-output statements here are interpretations of publisher and maintainer documentation, not executed builds, a resolved dependency audit, or a compatibility finding. Named products illustrate categories; the names are not a recommendation, ranking, complete catalog, tested combination, or supported stack, and not every Node or Bun project needs a web framework.

## The Invocation-To-Consumer Chain

A framework result carries five evidence points, and each answers a different question:

1. **Invocation.** The exact command, its package script, any wrapper, the working directory, the manager or launcher that started it, and the environment it ran in.
2. **Selected mode and build-time runtime.** The framework mode that actually took effect, and the runtime and version that executed the build.
3. **Adapter or preset.** The integration layer that shapes deployment output or selects a host convention, named with the version that supplied it.
4. **Emitted output and declared target.** The files the build wrote, their module format and assets, and any target the tooling declared for them.
5. **Consuming runtime or host.** The runtime version, host, server engine, or package consumer that loads the result.

Read the points in order because each later question presupposes an earlier answer, but keep the conclusions independent: an earlier pass does not clear a later point, and a later failure does not prove that an earlier one is sound. A build log names an invocation but can omit the effective mode. A preset name names an integration target, not a runtime. Emitted files show what exists, not that the deployment received all of it. A consumer failure identifies the layer to investigate, not the cause.

### Invocation And Build-Time Runtime

Start from the exact invocation rather than the framework name. A package script can call a framework binary, a wrapper can call the script, and the launcher can differ from the runtime the application uses later. The Next.js installation page states a minimum Node.js version of 20.9 while also showing Bun package-manager and command examples; those facts describe framework requirements and documented command forms, and they do not identify which runtime executes a particular project's build ([Next.js installation](https://nextjs.org/docs/app/getting-started/installation)). Record the script, wrapper, working directory, and runtime version before attributing behavior to the framework.

The build-time runtime also executes application code in some modes. The Next.js build guide describes compilation, static analysis, prerendering, and output into `.next`, identifies the compiler as Turbopack or webpack depending on configuration, and documents the static-export mode in which Server Components execute during `next build` ([Next.js building](https://nextjs.org/docs/app/guides/building), [Next.js static exports](https://nextjs.org/docs/app/guides/static-exports)). A successful build therefore can run application logic on the build machine, and build success can coexist with different request-time behavior.

Type-checking is a separate question from building. The same Next.js build guide says TypeScript checking in the build is conditional on the `typescript.ignoreBuildErrors` setting, so a green framework build does not by itself establish that the project was type-checked. Which program a check covered is interpreted in [Quality Scope And Tool Effects](quality-scope-and-tool-effects.md).

### Mode, Adapter, And Preset

Mode decides what kind of output the build produces. The Next.js pages distinguish the server-oriented build output, standalone output under `.next/standalone`, and static export, where `output: 'export'` emits HTML, CSS, and JavaScript files for a static host and omits features that require a server. The static-export page records that `output: 'export'` replaced the `next export` command in v14.0.0, which is a version boundary for that mode's configuration.

An adapter or preset names an integration target and shapes generated output; it does not rename the runtime. Next.js documents its deployment adapter API as customizing build and deployment output at build time, and it separates adapter output from the runtime cache interfaces a host implements ([Next.js deploying to platforms](https://nextjs.org/docs/app/guides/deploying-to-platforms)). Nitro documents a production default preset, `node_server`, whose `nitro build` produces `.output/server/index.mjs` launched with Node, a separate `bun` preset, and a `standard` preset that emits a web-standard entry exporting a `fetch` handler with public assets emitted separately ([Nitro deploy](https://nitro.build/deploy), [Nitro Node.js](https://nitro.build/deploy/runtimes/node), [Nitro Bun](https://nitro.build/deploy/runtimes/bun), [Nitro standard](https://nitro.build/deploy/runtimes/standard)).

Preset selection is not always an explicit request. Nitro's configuration page documents a `preset` that detects known environments, and `defaultPreset` precedence with a runtime-based fallback ([Nitro configuration](https://nitro.build/config/general)). A configuration file can therefore state one intention while the effective preset is chosen by detection. Record the preset that produced the output, not only the value written in configuration.

### Emitted Output And Declared Target

The output files are the build's product; the declared target is a statement about the environment the tooling intended. Bun's bundler page labels the page for v1.4.4 and defines `target` as the intended execution environment — `browser`, `bun`, or `node` — with target-sensitive resolution, configurable formats, `external` imports left for runtime resolution, opt-in declaration output, and build artifact records ([Bun bundler](https://bun.com/docs/bundler)). tsdown's rolling documentation likewise separates format and declaration settings from external dependency handling and optional export-map generation ([tsdown how it works](https://tsdown.dev/guide/how-it-works), [tsdown output format](https://tsdown.dev/options/output-format), [tsdown dependencies](https://tsdown.dev/options/dependencies)).

A declared target does not execute the artifact. Files intended for Node can be produced by a Bun-driven build, a Node-intended file can be deployed somewhere else, and an externalized import remains an import that the consuming installation must resolve. Treat the target label and the file list as claims about intent and content, and look for consumer evidence separately.

### The Consuming Runtime Or Host

The consumer is the runtime version, host, server engine, or package consumer that actually loads the output, and it can differ from the build machine, from the adapter's named platform, and from the framework's documented minimum. Node.js v26.13.0 documents package entry points, subpath exports, conditional exports, and module-type determination for Node's own resolution ([Node.js v26.13.0 packages](https://nodejs.org/download/release/v26.13.0/docs/api/packages.html)); Bun documents its own conditions and resolution behavior ([Bun module resolution](https://bun.com/docs/runtime/module-resolution)). Neither runtime's resolution rules transfer to the other without that runtime's own evidence. Module kind and source execution are interpreted in [Runtime And Project Structure](runtime-and-project-structure.md).

## Keep The Entity Categories Distinct

The chain mixes products that solve different problems. Keep these classes apart even when one product bundles several functions:

- **UI libraries** supply components or rendering primitives; React is a UI library, not an application framework.
- **Application frameworks** structure an application and define build and output paths; Next.js, SvelteKit, Nuxt/Nitro, Astro, and React Router illustrate products whose paths differ.
- **Server frameworks** provide request handling and routing abstractions; Express, Fastify, NestJS, Hono, and Elysia differ in their runtime integration claims.
- **Build and transformation tools** compile, transform, bundle, or emit package output; TypeScript `tsc`, esbuild, SWC, Bun's bundler, and tsdown occupy different roles among those jobs ([Quality Scope And Tool Effects](quality-scope-and-tool-effects.md) owns the role distinctions).
- **Server engines** accept connections and dispatch requests; Node's HTTP server in `node:http` and Bun's native serving surface are engines, not frameworks.
- **Deployment adapters and presets** translate a product's build output to a platform or engine convention; `@hono/node-server`, Nitro presets, and the Next.js adapter API are integration layers.
- **Runtimes** execute JavaScript; Node.js and Bun are the runtimes in scope here, with their own versions and semantics.

A product can combine roles — a framework with a built-in server, a bundler with a declaration flag, a server framework with a runtime adapter — but combined interfaces do not merge their evidence. A framework's compatibility statement does not certify the adapter package, the server engine, or the deployed runtime, and an adapter's presence does not establish that the framework's selected mode was used.

## Mode And Dependency Graph Answer Different Questions

A framework's selected mode and its resolved dependency tree are separate facts, and neither substitutes for the other:

- **The mode question** is what the framework was asked and configured to produce — a server build, standalone output, static export, or a preset-specific artifact — under a named version. The answer comes from configuration, effective preset detection, and the files actually written.
- **The graph question** is which packages and versions an installation resolved. npm CLI v12 documents `npm ls` as a logical dependency tree and `--all` as listing packages beyond direct dependencies ([npm ls v12](https://docs.npmjs.com/cli/v12/commands/npm-ls/)); that logical tree is not the installed bytes, and it is not evidence about which command a workflow invoked ([npm scripts v12](https://docs.npmjs.com/cli/v12/using-npm/scripts)).
- **A manifest label is not a resolved graph.** Naming a framework, adapter, or plugin in a manifest declares an intention for an installer; it does not show the resolved version, the effective mode, or that the package participates in the invoked path.
- **A documented adapter claim is narrower than verified compatibility.** Next.js publishes adapter-level test results, and the inspected support page reported the Bun adapter at 97.4% (3,739/3,838 assertions) on its latest listed run dated 2026-10-21 ([Next.js adapter support](https://nextjs.org/docs/app/api-reference/adapters/supported-providers)). That is a dated adapter test-suite snapshot, not a statement about every Next.js feature, Bun version, plugin, native dependency, or application. Nitro's statement that its Node output also runs on Bun is a Nitro-specific maintained claim ([Nitro Bun](https://nitro.build/deploy/runtimes/bun)), not cross-framework parity evidence.
- **Build and output claims are interpretations.** The distinctions on this page synthesize publisher-reported positions; they do not establish behavior for an uninspected project, combination, platform, version, or dependency graph. Keep every compatibility statement scoped to the product, version, mode, feature, manager, adapter, output, and consumer that the source named.

The practical consequence is that a requested mode and an installed dependency graph require different evidence. A request names a mode and a configuration; it does not show that the installed framework version supports that mode or that the resolved packages provide the adapter, engine, or plugin the mode needs. Configuration and version establish what the build was asked to do and what that release documents; an installer's resolution and the actual installed tree establish what is present; the produced files and the consumer's load establish what happened. None of the three answers the others.

## Four Worked Contrasts

These combinations are illustrative readings of the documented mechanics, not executed builds or deployment tests.

### A Preset Names One Host While The Deployed Runtime May Differ

Nitro's production default preset is `node_server`, whose build writes `.output/server/index.mjs` for launch with Node. Nitro's Bun page states that its default Node output also runs in Bun and that the `bun` preset enables Bun-specific optimizations. The deployed runtime can therefore differ from the preset's named default without the build having targeted the deployed runtime: a project built with the default preset and launched under Bun is running a Node-intended output under Bun, relying on Nitro's product-specific statement. That reading does not extend to another framework's preset, to another output, or to every Bun version. Record the effective preset, the build runtime and version, the deployed runtime and version, and the output path; if the deployed runtime is unknown, the preset name alone does not supply it.

### A Build Succeeds While The Consumer Still Fails

The Next.js output page describes `output: 'standalone'` as producing `.next/standalone` with a minimal `server.js`, and it notes that `public` and `.next/static` are not copied by default, with monorepo tracing-root caveats ([Next.js output](https://nextjs.org/docs/app/api-reference/config/next-config-js/output)). Deploy only the standalone directory and the server entry can start while requests for static assets fail, because the build succeeded and the deployment is still incomplete. The same shape appears with dependencies: an externalized import stays in the output for runtime resolution, so a deployment image that omits that package can load the bundle and fail on first use, and a module-format or condition mismatch surfaces as a loader error rather than as a framework error.

The consequence is that "the build succeeded" records only that the selected command completed. Consumer failure falls into entry-point or included-file gaps, module-format mismatches, and dependency assumptions that the output does not satisfy. Keep that framework-level reading here; when the failing consumer is a packed package subpath, diagnose it as the ordered four-layer question owned by `node-package-distribution -> reference/consumer-resolution-and-declarations.md` rather than by this page.

### The Bun Bundler Builds One Target For Another

Bun executes `bun build`, and its v1.4.4 bundler page separates that build execution from the output's intended environment. `target: "node"` declares Node as the intended consumer and applies target-sensitive resolution, while the build itself runs under Bun; configurable formats decide the emitted module form; `external` leaves imports for runtime resolution; and `dts: true` or `--dts` adds declaration output as a separate product from the runtime bundle. None of those facts makes the emitted files Bun-targeted, and none makes the build machine the consumer. A target label, an emitted format, an externalized import, and a declaration file are four separate claims that each need the matching consumer evidence.

The bound is the documented release and the installed one. The page header displayed Bun v1.4.4 as the documentation context, not as the version installed in any project, and the page is rolling. Declaration output availability is version-specific, and Bun's own declaration-generation documentation conflict is kept visible in `node-package-distribution -> reference/consumer-resolution-and-declarations.md`; this page does not resolve it or project it onto a selected release.

### One Application, Two Runtime Integrations

Hono's Node guide uses `@hono/node-server`, says its `serve()` wraps `node:http`, and states Node version minima of 18.14.1+, 19.7.0+, and 20.0.0+ for those major lines ([Hono Node.js](https://hono.dev/docs/getting-started/nodejs)). Its Bun guide instead exports the application as a Fetch handler for Bun's native serving model, runs it with `bun run`, and documents `@hono/bun` for static serving ([Hono Bun](https://hono.dev/docs/getting-started/bun)). One application definition therefore yields different integration packages, different engines, and different consumer evidence, even though the application source is shared. The guides show runtime-specific integration examples; they do not describe a common generated deployment artifact, and neither page establishes equivalent behavior across runtimes or versions. A passing Node integration says nothing about the Bun integration, and a Bun guide example does not certify a Node deployment.

## Application Output Compared With A Package Tarball

A framework or application build produces something a runtime or host consumes: a server bundle, a standalone directory, or a static file set. A package tarball is a different delivery form whose consumer is an installer, a resolver, and possibly a compiler. Application deployment and package publication are therefore separate concerns, and one does not validate the other.

This page does not own the package consumer surface. Package module format, the `type` field, `main` and `exports`, conditional exports, declaration wiring, packed file selection, and the behavior of an installed archive route to the package owner: start from `node-package-distribution -> reference/artifact-and-consumer-boundaries.md` for the delivered contract, build-pack-publish separation, and consumer testing scope, and use `node-package-distribution -> reference/consumer-resolution-and-declarations.md` for the consumer-facing resolution and declaration question. That second page is the single canonical home of the four-layer packed-subpath diagnosis; this page points to it and does not restate the layers. Neither routing step establishes publication, release, registry, or deployment authority.

## The Vite Boundary In This Page's Own Terms

Nothing on this page selects, prescribes, or relies on Vite. The framework, adapter, build-tool, and consumer examples are bounded illustrations, not endorsements, and no sequence described here forms an implicit build or deployment pipeline. When a framework's own documented setup, development, or build path requires Vite, report that workflow as Vite-dependent and do not present it as a no-Vite path.

A Vite package appearing somewhere in an installed tree is a separate fact from workflow reliance. It is not evidence that any invoked command selects Vite, and it is not evidence that a resolved graph lacks Vite. Only exact project versions, the effective mode and configuration, the invoked command path, and resolved-tree evidence could support a dependency claim about a specific project, and this page asserts neither a blanket transitive ban nor graph absence for any framework or project. Inspected Vite-dependent framework snapshots and their version bounds are carried in `node-domain-planning -> reference/project-structure.md`; this page does not restate or extend those values, and the boundary holds independently of them. Never infer Vite status from a framework name.

## Limits, Diagnostics, And Consequences

Framework output and adapter claims are mode- and version-specific. The Next.js pages cited here are rolling and displayed no framework version except the static-export history note for v14.0.0; the adapter results page is a live snapshot with a dated run. Nitro's pages are rolling and showed no release. Bun's bundler page is labeled v1.4.4. tsdown's documentation is rolling and showed no release. Hono's guides are rolling and state their Node minima as page text rather than as a current support matrix. Node package behavior is tied to the v26.13.0 documentation page, and npm tree behavior to CLI v12. No framework build, generated file, deployment, or consumer installation was run for this page.

Read the observable before assigning a cause:

- A zero build exit establishes that the selected command completed under its configuration. It does not establish the effective preset, the completeness of copied assets, the output's module format, or that the deployed runtime can load it.
- A server that starts while static routes return missing files points to included-file or asset-copy selection, including the standalone tracing caveats above, not to a runtime compatibility verdict.
- A loader error naming a module or format points to the selected output target and the consuming runtime; a missing externalized dependency points to the deployment's dependency assumptions; a typed consumer's unresolved declaration points to the package surface and routes to the package owner.
- An unknown effective preset or build runtime is an evidence gap. Stop at that uncertainty rather than inferring framework behavior from a package name, a manifest entry, or a lockfile.
- A consumer result from one runtime, version, integration, or module format does not transfer to another; record each separately.

For a concrete report, name the framework and version, the invoked script and wrapper, the build-time runtime and version, the effective mode and preset, the adapter or preset version, the emitted output paths and declared target, the consuming runtime or host and version, and the exact failure the consumer surfaced. If one of those is unavailable, say which one is missing instead of completing the chain by assumption.

## Ownership And Cross-Links

This page owns interpretation only. It selects no framework, adapter, bundler, or stack, and it promises no compatibility across products, versions, plugins, native dependencies, or deployments.

- Package artifact work — tarball contents, export maps, declarations, packed-install consumer testing — goes to `node-package-distribution`.
- Framework configuration, build scripts, and application code changes go to `node-project-writer` as the production owner, and dependency or environment changes go to `node-project-dependencies`, each as the request scopes them.
- Check-versus-target interpretation, including whether a framework build type-checked the project, belongs to [Quality Scope And Tool Effects](quality-scope-and-tool-effects.md).
- Runtime execution, module kind, and resolution belong to [Runtime And Project Structure](runtime-and-project-structure.md); manager and invocation evidence belongs to [Manager, Workspace, And Invocation Evidence](manager-workspaces-and-invocation.md).
- Project structuring, the provisional outcome roster, and the carried Vite snapshot values belong to `node-domain-planning -> reference/project-structure.md`.
- Package consumer resolution and declaration diagnosis belong to `node-package-distribution -> reference/consumer-resolution-and-declarations.md`.

No deployment, release, registry-administration, or publication authority follows from this reference.
