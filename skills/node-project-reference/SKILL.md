---
name: node-project-reference
description: "Use when a TypeScript question in a Node.js or Bun project needs the runtime, manager, checker, test runner, framework, configuration, diagnostic, concurrency, or public-API mechanics behind an observed behavior."
selection:
  role: reference
  tags:
    actions: [reference, explain]
    inputs: [project context, technical question]
    outputs: [project mechanics context]
    topics: [Node.js, Bun, TypeScript, runtimes, module resolution, package managers, quality tools, test runners, frameworks, configuration, diagnostics, concurrency, public APIs]
    environments: [Node.js projects, Bun projects]
    constraints: [passive, no tool or stack defaults]
  use_when:
    - a TypeScript project task needs context about its evidenced runtime, package, module, tool, framework, or consumer surface
    - TypeScript source, declaration, or public API conventions need to be interpreted in project context
  not_for:
    - implementing production behavior, tests, dependency changes, quality configuration, or package artifacts
    - deterministic utilities in this repository's scripts/node/ workspace
    - choosing a universal stack or treating examples as a compatibility guarantee
    - JavaScript-only source work, including JavaScript or mixed-language eligibility
    - JavaScript checking and diagnostics, such as allowJs and checkJs
    - JSDoc typing of .js files
class: documentation
---

# Shared Project Mechanics Reference

Use this passive reference when a TypeScript question in a Node.js or Bun project needs the mechanics an observed behavior depends on: which runtime ran, what the checker covered, which workspace and invocation the evidence describes, why a file or test was missed, which environment source supplied a value, what a framework emitted, which surface produced an output, whether work ran in parallel or still runs, or what a public contract requires. It informs other work; it does not own implementation, testing, dependency evaluation, quality changes, package artifacts, project decisions, or validation.

The reference covers TypeScript and only the emitted-JavaScript and runtime mechanics that TypeScript depends on. Its subject is TypeScript source, configuration, declarations, tests, quality diagnostics, package artifacts, and API documentation comments on exported declarations. Node.js and Bun runtime, module, loading, and emitted-JavaScript mechanics appear only where they explain how TypeScript source executes, emits, resolves, declares, or reaches a consumer. Standalone JavaScript source guidance, JavaScript or mixed-language eligibility, JavaScript diagnostics and the JavaScript checking options `allowJs` and `checkJs`, and JSDoc typing of `.js` files are out of scope, and a JavaScript-only request is reported as out of scope.

## Route By Question

Each route names the discriminating clue that selects it and the page that answers it, in question order. The clue is the deciding signal: a neighboring question has a different answer on a different page, and the toolchain layer named by the clue is the layer the page keeps separate. A route grants no operation, tool, edit, permission, sequence, approval, or completion authority.

- **Which runtime ran, and what processed the TypeScript.** Clue: a `.ts` entry point, a green type check beside a failing run, or a specifier that resolves for the checker but not the loader. [Runtime And Project Structure](reference/runtime-and-project-structure.md) keeps the source-to-consumer chain, the processing differences between native stripping, transpiling, and a build step, module kind and resolution, and the canonical mixed-clue case.
- **Which workspace and invocation the evidence concerns.** Clue: a manifest, lockfile, workspace glob, installed binary, or script line is being read as proof of what executed. [Manager, Workspace, And Invocation Evidence](reference/manager-workspaces-and-invocation.md) separates the seven evidence layers, their manager-specific routes, and the competing-lockfile question.
- **What a check or quality command actually covered or changed.** Clue: a command passed, missed a file, or rewrote output, and the question is which program members, target set, mode, or written files it touched. [Quality Scope And Tool Effects](reference/quality-scope-and-tool-effects.md) separates program membership, target selection, check versus write mode, and tool roles that are not interchangeable.
- **Why a test or a measurement misleads.** Clue: a test did not run although a command exited zero, or a percentage moved without a behavior change. [Test Execution And Measurement](reference/test-execution-and-measurement.md) keeps collection per runner, isolation, assertion strength, and the coverage denominator separate, with provider disagreements visible.
- **What a framework build emitted and who consumes it.** Clue: a build or dev command succeeded, and the question is which mode, adapter, output, declared target, and host or package received the result. [Framework Output And Consumers](reference/framework-output-and-consumers.md) keeps the invocation-to-consumer chain and the entity categories distinct.
- **Which source supplied a configuration value.** Clue: a setting is missing, defaulted, inherited, or differs between a shell and a runtime, and no precedence order is evident. [Configuration Loading And Validation](reference/configuration-loading-and-validation.md) separates the five loaders' precedence, presence, parsing, validation, and exposure.
- **Which surface produced a diagnostic or telemetry output.** Clue: a line appeared twice, carried a sensitive value, or arrived from a console, channel, report, context manager, or exporter. [Diagnostics And Telemetry](reference/diagnostics-and-telemetry.md) separates six surfaces and keeps documented maturity and naming disagreements visible.
- **Whether work runs in parallel, stopped, or still completes.** Clue: concurrency was assumed from `await`, a cancellation was requested, a stream write stalled, or shutdown returned before the work did. [Concurrency And Lifecycle](reference/concurrency-and-lifecycle.md) separates event-loop ordering, a cancellation request from an effect already produced, and cancelling a wait from destroying the work.
- **What a public source or API contract requires.** Clue: an import of a packed subpath fails, or a declaration, public name, or runtime module format must stay compatible for a consumer. [Source And API Conventions](reference/source-and-api-conventions.md) keeps the shared cross-layer rule and maps each failure to its layer, then points everyday source choices to the style workspace and the ordered packed-subpath diagnosis to the package consumer page.
- **Which owner has the deeper procedure.** Clue: the question asks for a change, command, configuration, or artifact rather than an interpretation. The deeper production procedure is owned by `node-project-writer -> #production-behavior-change-workflow`, test-only work by `node-project-test-writer -> #test-only-change-workflow`, dependency or environment changes by `node-project-dependencies -> #dependency-decision-and-environment-workflow`, standalone quality work by `node-quality-workflow -> #standalone-quality-workflow`, package artifacts by `node-package-distribution -> #package-artifact-and-consumer-workflow`, and project or outcome planning by `node-domain-planning -> #node-project-planning-context`.

## Shared Boundaries

- Establish the relevant project and package scope from request and repository evidence. Do not infer the whole stack from a `package.json`, `.ts` extension, framework name, or repository root alone.
- Keep runtime, package manager, module resolver, checker, transformer, builder, test runner, framework, adapter, and artifact consumer distinct. Products may combine functions, but combined interfaces do not make their responsibilities or compatibility evidence interchangeable.
- Treat versioned examples as illustrations of the stated documentation or metadata, not a tested compatibility matrix, supported baseline, universal default, or recommendation.
- A TypeScript label does not identify the executing runtime. Read the runtime, its version, the module mode, and the configured check that a specific claim depends on.
- This context does not select or support Vite, prescribe it as a default, or describe a workflow that invokes or relies on it. An incidental transitive package edge is not by itself evidence of direct selection; this reference makes no blanket dependency ban or graph-absence claim. Evaluate a concrete project's exact workflow and resolved dependencies when that distinction matters.
- The repository's deterministic utilities under `scripts/node/` have their own bounded conventions; do not generalize them as ordinary project defaults.
- No deployment, release, registry-administration, publication authority, or organization-wide security policy follows from this reference.

## Passive Use

This is descriptive context only. It provides no procedure, commands, edits, tool calls, policy decisions, approval, or completion evidence. Executable plans stay with `plan-writer`; consult the outcome owner named by the matching route for any requested change.

## Docs

See the [Route By Question](#route-by-question) list above for the question each reference answers.
