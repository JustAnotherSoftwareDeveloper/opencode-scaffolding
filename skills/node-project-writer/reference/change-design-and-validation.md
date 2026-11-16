# Change Design And Validation

Use this reference when an authorized production change crosses project boundaries,
version-sensitive APIs, or more than one runtime or tool layer. It is the canonical
production answer home for the change's context-and-validation question: which package,
workspace, runtime, manager, compiler, runner, framework, adapter, and consumer matter; how
to reconcile mixed clues; how to align TypeScript module settings with the runtime loader;
and how far validation must reach. The caller-contract question — what a caller observes in
results, failures, timing, cancellation, and side effects — is answered in
[Behavior And Caller Contracts](behavior-and-caller-contracts.md). Apply only the guidance
relevant to the requested outcome.

The subject is production TypeScript source, TypeScript configuration, declarations, and
directly coupled regression tests in Node.js or Bun projects. Node.js and Bun runtime,
module, loading, and emitted-JavaScript mechanics appear only where they explain how
TypeScript source executes, emits, resolves, or reaches a consumer. JavaScript-only work is
out of scope, and `allowJs`, `checkJs`, and JSDoc typing of `.js` files are excluded. This is
reference context; the operation entry point owns authorization, edits, commands, and
completion claims.

## Establish Effective Project Context

Start from the affected package and its actual workspace. A repository root or `package.json`
alone may not identify the package, manager, runtime, module mode, or active command.
Inspect relevant scripts, lockfiles, workspace declarations, runtime dispatch, compiler
and test configuration, and framework or adapter configuration as needed. Use their
evidence to answer a specific question; do not infer an entire stack from a filename,
framework label, or manager choice.

Keep these roles distinct even where one product exposes several of them:

- **Runtime:** Node.js and Bun execute program code. A project may target one, both, or
  another documented surface. A Bun install does not prove that Bun executes the app.
- **Package manager and workspace:** The manager, its version, lockfile, workspace graph,
  install layout, and task graph have manager-specific behavior. Do not treat them as a
  runtime choice or infer equivalent behavior across managers.
- **TypeScript processing:** Runtime execution, type checking, transpilation, JavaScript
  emission, declaration generation, and bundling answer different questions. A runtime
  that accepts TypeScript or a successful transform does not thereby type-check it.
- **Tests and quality checks:** A test runner has its own runtime, transform, discovery,
  isolation, and coverage behavior. Type-checking, linting, formatting, and tests are not
  interchangeable. A tool's TypeScript support does not guarantee static type checking.
- **Framework, adapter, and consumer:** Framework mode, build-time runtime, server adapter,
  generated output, and deployed or consuming runtime may differ. Follow the project's
  actual path rather than assuming compatibility from a framework name.

Treat documented examples as version-qualified illustrations, not tested parity or a
universal support matrix. For example, the inspected Node.js v26.13.0 documentation
describes native TypeScript execution that strips erasable syntax without type-checking
and ignores `tsconfig.json`; Bun documentation describes runtime TypeScript/TSX
transformation while ordinary execution also does not type-check. These examples do not
establish behavior for other versions or configurations. Verify claims against the target
project and its versions.

## Reconcile Conflicting Project Clues

Projects routinely present clues that appear to disagree: a lockfile from one manager, a
script that names another runtime, package markers in a subdirectory, and a green check
that says nothing about the changed file. The canonical mixed-clue case — each clue's actual
question, the diagnosis that separates manager state from runtime dispatch, and the limits
on what a green check establishes — is in
`node-project-reference -> reference/runtime-and-project-structure.md#reconcile-mixed-runtime-clues`.
Read it there; this page does not repeat it.

The production question is narrower than the case. For an authorized change, identify which
clue is attached to the artifact the change touches and whether that clue names the loader,
checker, or consumer the change will actually run under. A lockfile decides nothing about
execution; the exact invocation decides which runtime started; the nearest package boundary
and the file extension decide module interpretation; the selected configuration and file
list decide what a check covered. When two clues still conflict after those readings, the
unresolved one is what to report, not something to average or resolve by preference.

A changed file that is absent from a green check is a scope question about that check, and
its diagnosis belongs to the quality owner:
`node-quality-workflow -> reference/quality-scope-and-mutation.md#diagnose-a-changed-file-missing-from-a-green-check`.
Keep one consequence here: a successful run shows the files it checked, not that a changed
file was in the program.

## Relate Module Configuration To The Runtime

Module interpretation is decided per file by the nearest package boundary and the file
extension, not by the compiler's model of a module. On Node's native path an explicit
nearest package `type` field governs `.js` and `.ts`; `.mjs`/`.cjs` state a format outright,
and `.mts` is always ESM while `.cts` is always CommonJS, whatever `type` says ([Node.js
modules: Packages](https://nodejs.org/api/packages.html#determining-module-system)). A
`tsconfig` with `module: "nodenext"` describes TypeScript's Node-aware resolution and emit
model; it does not set the package's format, and it cannot prove that emitted files match
the loader that runs them. The `module` choice also changes which module resolution
TypeScript applies and which import types the checker observes ([TypeScript compiler
options](https://www.typescriptlang.org/docs/handbook/compiler-options); [TSConfig
reference](https://www.typescriptlang.org/tsconfig/)).

If no controlling `type` is set, do not assume the file is CommonJS. The Node v26.13.1
Packages page documents syntax detection for ambiguous `.js` input, where ESM-only syntax
can select ESM interpretation, and marks that feature Stability 1.2 (Release candidate)
([Node.js modules: Packages](https://nodejs.org/api/packages.html#determining-module-system)).
The behavior depends on the Node version, the exact invocation, and the source syntax;
confirm all three before concluding a file's mode, and do not carry the reading to Bun or to
another Node release.

### Trace The Change From Invocation To Consumer

A production change touches one or more artifacts, and each artifact has its own checker,
loader, and consumer. Two shapes cover most TypeScript changes.

The first is a `.ts` file that a runtime executes directly. On Node's native path the file
is type-stripped rather than compiled: erasable TypeScript syntax is replaced with
whitespace, no type checking is performed, `tsconfig.json` is ignored so settings such as
`paths` and `moduleResolution` never reach that execution, and `.tsx` is refused ([Node.js
v26.13.0 TypeScript modules](https://nodejs.org/download/release/v26.13.0/docs/api/typescript.html)).
Erasable syntax is a bound, not a preference: `enum` declarations, namespaces that contain
runtime code, parameter properties, and non-ECMAScript `import =`/`export =` aliases error
on that path. Node's own recommendation for this path is TypeScript 5.8 or newer with
`noEmit`, `target: esnext`, `module: nodenext`, `rewriteRelativeImportExtensions`,
`erasableSyntaxOnly`, and `verbatimModuleSyntax`; that list is a publisher recommendation
whose rationale is to keep the compiler's model aligned with stripping, not a language rule
the loader enforces. The source has a checker only when a separate compiler invocation
selects it:

```ts
// src/cli.ts, executed by Node's native path with no build step
import type { Options } from "./options.js"; // the `type` keyword is required here
import { parse } from "./parse.js"; // relative extensions are mandatory
```

Without the `type` keyword Node treats the import as a value import and fails at run time
because the type has no runtime binding; `verbatimModuleSyntax` reproduces that requirement
at check time instead ([Node.js v26.13.0 TypeScript
modules](https://nodejs.org/download/release/v26.13.0/docs/api/typescript.html)).

The second shape compiles first. Here the compiler reads source and writes JavaScript and
declarations, and a different set of readers picks them up:

```json
{
  "type": "module",
  "exports": {
    ".": { "types": "./dist/index.d.ts", "import": "./dist/index.js" }
  }
}
```

```ts
// src/index.ts   -> dist/index.js, plus dist/index.d.ts
// src/modern.mts -> an emitted ESM file, plus dist/modern.d.mts
// src/legacy.cts -> an emitted CommonJS file, plus dist/legacy.d.cts
```

On a build with `module: "nodenext"` and `declaration: true`, the checker analyzes `src`,
the loader executes `dist/index.js` under the package's ESM scope, and a typed consumer
resolves `dist/index.d.ts`. The extensions in the example hold the formats apart: `.mts` is
always ESM and `.cts` is always CommonJS, a plain `.ts` follows the package `type` field,
and the declaration files take the matching `.d.mts` and `.d.cts` names. Each artifact
answers a different question, so a green check on the source is not evidence about the
emitted file, and a successful import of the emitted file is not evidence that a typed
consumer resolves its declarations.

For emitted output the same rule applies one layer later. The package `type` field and the
emitted extension decide interpretation as they do for hand-written files, and when an
emitted `.js` sits in a package with no controlling `type`, the Node v26.13.1 syntax
detection above applies again at load time. That is emitted-output mechanics; it is not a
claim that the compiler chose the format or that the loader agrees with the compiler's
model.

### Keep Checker Resolution And Loader Resolution Apart

A resolver that accepts a specifier is not necessarily the resolver that loads it.

```json
{
  "compilerOptions": {
    "module": "nodenext",
    "moduleResolution": "nodenext",
    "baseUrl": ".",
    "paths": { "@app/*": ["./src/*"] }
  }
}
```

TypeScript `paths` informs TypeScript's resolver only; it does not rewrite emitted import
paths. A built file still contains the alias, and whatever loads it must map that name.
Node's native path reports `paths` aliases as unsupported rather than resolving them. A
second setting, `moduleResolution: "bundler"`, permits extensionless relative resolution
that Node's ESM loader does not, so `import { parse } from "./parse"` can pass the checker
and fail to resolve at load. Do not "fix" either mismatch by changing the package's module
format or rewriting imports until the actual consumer and its intended contract are
established: the loader that already consumes the current format is what such a change puts
at risk.

### Ask Five Questions About The Invocation

Five questions locate the artifact a change actually affects. They are a bounded trace, not
a runbook, and answering them does not execute, validate, or authorize anything. Invocation
detail is interpreted in
`node-project-reference -> reference/manager-workspaces-and-invocation.md#seven-layers-of-evidence`.

1. **Which exact package script and wrapper ran?** The command, working directory, and
   launcher decide the runtime and the project root. A script's text or a lockfile does not.
2. **Which framework mode and adapter or preset applied?** Mode decides the kind of output,
   and an adapter or preset names an integration target rather than a runtime.
3. **Which build-time runtime executed, and what output target did it declare?** A build can
   run application code on the build machine, and it can declare a target for what it
   writes.
4. **Which files and formats were produced?** Name the emitted JavaScript, its module
   format, and any declaration files.
5. **Which runtime consumes them?** Identify the runtime version and loader that actually
   receive the output, whether that is the project's own runtime, a host, or a package
   consumer.

The framework, adapter, and consumer contrasts behind the second and fifth questions are in
`node-project-reference -> reference/framework-output-and-consumers.md#the-invocation-to-consumer-chain`.
Do not reconstruct a runtime from a manager file or infer an adapter from a command name.

The consequence to carry into a report: a green check on one artifact is not evidence about
another. A type check covers its selected program and options; a transform or build covers
the output it wrote; a test covers the code it imported under its own runtime. When a
changed file is absent from a green check, the question is the check's scope, diagnosed in
`node-quality-workflow -> reference/quality-scope-and-mutation.md#diagnose-a-changed-file-missing-from-a-green-check`.
Program-membership interpretation for other checks is in
`node-project-reference -> reference/quality-scope-and-tool-effects.md#compiler-program-membership-compared-with-a-successful-check`.

## Keep Vite Out Of Direct Workflows

Do not select Vite as a tool, default, or supported workflow, and do not prescribe or rely
on a workflow that invokes Vite or depends on Vite-based operation. Do not recommend a
runner or framework mode whose requested workflow requires Vite. Separately, do not turn
this direct-workflow boundary into a blanket prohibition on every transitive package or a
claim that a particular framework graph is Vite-free. An incidental dependency edge alone
does not establish direct selection; a workflow that relies on Vite is not a no-Vite
workflow. Any project-specific graph claim requires exact versions and resolved dependency
evidence.

## Scope Regression Tests

Choose regression cases from the changed observable contract and affected callers. The
caller-observable surfaces worth covering — results, failure channels, public runtime and
type paths, timing, and side effects — are enumerated in
[Behavior And Caller Contracts](behavior-and-caller-contracts.md); this section decides only
which cases an authorized change needs. Use the configured test runner and the runtime it
actually executes under; do not infer Node and Bun parity from a shared API shape or a green
test in only one runtime. Keep tests, fixtures, and helpers limited to the behavior change. A
discovered unrelated production defect, missing test infrastructure, or separate test-only
request is not permission to expand the production change.

When an application or package has multiple output consumers, validate only the outputs and
consumers required by the request. Distinguish a source-level type check from executing
transformed code, from testing a framework adapter, and from consuming a built package. If
output validation is outside the authorized scope, report the unverified boundary rather than
implying success.

## Report Evidence And Limits

Record changed paths, behavior established by the change, relevant project and runtime
versions, exact authorized commands, and their outcomes. State the target files or tests
covered where material, and say which artifact each check covered: the source program, the
emitted JavaScript, the declaration output, or a packed consumer. Name checks that did not
run and why. Do not claim compatibility for untested versions, APIs, adapters, platforms, or
output consumers. A passing type check establishes only the checker and program scope it
actually covered; it does not prove runtime correctness, safe configuration, deployment
readiness, or package-consumer compatibility.

Keep the runtime limits with their version. Node's native path is described from pinned
v26.13.0 documentation, accepts erasable syntax only, ignores `tsconfig.json`, and does not
type-check; Bun's ordinary execution transpiles without checking types and reaches checking
through a separate interface, with its documentation pages rolling and naming no release
baseline. Those are different bounds, not a parity result, and neither description carries
to another release or to the other runtime.

These examples synthesize documented behavior; they are not reports of executed commands
or guarantees for another version. For current specifics, consult the [TypeScript CLI reference](https://www.typescriptlang.org/docs/handbook/compiler-options)
and [TSConfig reference](https://www.typescriptlang.org/tsconfig/), [Bun runtime documentation](https://bun.com/docs/runtime),
and [Node package documentation](https://nodejs.org/api/packages.html). The TypeScript and
Bun pages are rolling; the Node package page is versioned (v26.13.1). Confirm the target
versions, command form, and configuration before applying a documented behavior.

Keep dependency edits, environment and lockfile changes, standalone quality work, package
artifact production or consumer validation, publishing, and deployment outside this
operation unless a separate explicit contract authorizes them. Do not imply registry
administration or organization-wide policy authority.

## Ownership And Routing

This page owns the change's context-and-validation decision: which package, runtime,
manager, compiler, runner, framework, adapter, and consumer surround an authorized
production change, how TypeScript module configuration relates to the runtime loader, and
how far validation must reach. As an outcome owner, `node-project-writer` also owns the
production behavior change itself and the regression tests directly coupled to it; the
caller-contract reasoning behind that behavior is the behavior page's subject.

- Caller-observable results, failure channels, timing, cancellation, and side effects:
  [Behavior And Caller Contracts](behavior-and-caller-contracts.md).
- Invocation, workspace, and manager evidence:
  `node-project-reference -> reference/manager-workspaces-and-invocation.md`.
- Runtime, checker, and module mechanics:
  `node-project-reference -> reference/runtime-and-project-structure.md`.
- Framework build output and its consumer:
  `node-project-reference -> reference/framework-output-and-consumers.md`.
- Check-versus-target semantics for other tools:
  `node-project-reference -> reference/quality-scope-and-tool-effects.md`.
- A changed file missing from a green check, and standalone quality configuration or
  reporting: `node-quality-workflow`.
- Archive validation, packed-consumer resolution, and declaration wiring:
  `node-package-distribution -> reference/consumer-resolution-and-declarations.md`. Archive
  validation belongs to that owner; this page does not reproduce it.
- Test-only work: `node-project-test-writer`. Dependency and environment changes:
  `node-project-dependencies`. Publication and deployment stay outside this operation.
- This repository's `scripts/node/` utilities are a separate route with their own Bun and
  repository conventions, not ordinary project defaults: script work belongs to
  `skill-script-node-writer` and their tests to `skill-script-node-test-writer`.
- Executable source-based plans remain with `plan-writer`.

A routing statement names an owner; it does not grant authority. The operation entry point
still decides what may be edited or run, and a passed check is evidence only for the artifact
it examined.
