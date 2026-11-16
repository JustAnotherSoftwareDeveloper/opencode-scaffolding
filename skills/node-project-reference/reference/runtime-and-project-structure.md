# Runtime And Project Structure

## Scope

This page answers four questions about a TypeScript project in Node.js or Bun: what executes the code, what the checker covers, what a module specifier resolves to, and which project clue answers which of those questions. It states passive mechanics and interpretation. TypeScript surfaces are the subject; JavaScript-only work is out of scope, and the JavaScript checking options `allowJs` and `checkJs`, together with JSDoc typing of `.js` files, are excluded from this reference. Each statement stays with its named runtime, tool, version, mode, or configuration, because the cited pages are version-pinned or rolling and either kind can change.

## The Source-To-Consumer Chain

A TypeScript project moves through distinct stages, and each stage produces its own evidence:

- **Source.** `.ts`, `.mts`, `.cts`, and `.tsx` files, plus the TypeScript configuration that selects the program.
- **Selected runtime or transformer.** Node's native TypeScript path, Bun's transpiler, or a build step that runs before any runtime.
- **Checker and resolver.** A checker such as `tsc` with its selected program, `module`, and `moduleResolution` settings.
- **Emitted output and declarations.** JavaScript in the selected format, and `.d.ts`, `.d.mts`, or `.d.cts` output when declarations are generated.
- **Consumer.** The runtime that loads the output, a dependent package that imports it, or a tool that reads only its declarations.

Keep three separations when reading evidence from that chain:

- TypeScript syntax transformation is not static checking. A runtime can erase or rewrite type syntax without reporting a type error, and a checker can accept a program it never executes.
- A package manager or lockfile does not identify the executing runtime. Bun documents `bun install` as usable in existing Node.js projects, which establishes manager capability and nothing about what runs the application ([Bun install](https://bun.com/docs/pm/cli/install)).
- A build command alone does not identify an adapter, an output format, or a consumer. The command, its configuration, and the produced files each have to be read.

## Runtime And TypeScript Processing

Node.js v26.13.0 documents native TypeScript execution as type stripping: erasable TypeScript syntax is replaced with whitespace, no type checking is performed, and the runtime ignores `tsconfig.json`, so settings such as `paths` never apply ([Node.js v26.13.0 TypeScript modules](https://nodejs.org/download/release/v26.13.0/docs/api/typescript.html)). On that pinned page the native path also refuses `.tsx` and errors on syntax that would require generating JavaScript: `enum` declarations, namespaces that contain runtime code, parameter properties, and non-ECMAScript `import =`/`export =` aliases. Those are the limits recorded for that version and path, not a statement about every Node release.

Bun documents a different split. It transpiles TypeScript and TSX on the fly before running a file, and ordinary execution does not check types; `--check` and `bun check` are separate interfaces that check before running and exit non-zero on error ([Bun runtime](https://bun.com/docs/runtime); [Bun type checking](https://bun.com/docs/runtime/check)). Those Bun pages were rolling and surfaced no release version, so treat the described behavior as the accessed documentation rather than a contract for a specific Bun release.

A checker result covers only the program, options, and files it selected. A green type check therefore says nothing about what the runtime loaded, what a bundler emitted, or whether a consumer can resolve the package. Program membership and target selection are interpreted in [Quality Scope And Tool Effects](quality-scope-and-tool-effects.md).

## Module Kind And Resolution

Module kind is decided per file from the nearest package boundary and the file extension. A package's `type` field controls how `.js` and, under Node's native path, `.ts` files are interpreted; `.mjs`/`.cjs` and `.mts`/`.cts` state an explicit format; `.tsx` is not accepted by Node's native path ([Node.js modules: Packages](https://nodejs.org/api/packages.html#determining-module-system)). The Node v26.13.1 Packages page also records syntax detection for ambiguous `.js` or extensionless input with no controlling `type`, where the parser may detect ESM syntax and treat the file as a module, and it advises package authors to set `type` explicitly. A missing `type` field is therefore not decisive on its own; read the runtime version and the actual invocation.

Node's native path also requires the explicit `type` keyword on type-only imports. Without it, Node treats the import as a value import and fails at run time because the type has no runtime binding:

```ts
import type { RetryPolicy } from "./retry-policy.js";
```

The v26.13.0 page names `verbatimModuleSyntax` as the compiler setting that matches this behavior. Source-level conventions for these imports and exports belong to [Source And API Conventions](source-and-api-conventions.md).

TypeScript's checker models a host, and the model can disagree with the loader that actually runs the code:

- `moduleResolution: "bundler"` accepts extensionless relative imports, while Node's ESM loader requires the extension in a relative specifier ([TypeScript modules: Reference](https://www.typescriptlang.org/docs/handbook/modules/reference.html); [Node.js v26.13.0 ESM](https://nodejs.org/download/release/v26.13.0/docs/api/esm.html)). Code that imports `./config` passes the checker and fails to resolve under Node.
- `paths` maps module names for the checker only. It does not rewrite emitted import specifiers, so a built file still contains the alias and whatever loads it must handle that name; Node's native path does not implement `paths` aliases and reports them as unsupported ([TSConfig `paths`](https://www.typescriptlang.org/tsconfig/paths.html); [Node.js v26.13.0 TypeScript modules](https://nodejs.org/download/release/v26.13.0/docs/api/typescript.html)).
- A declaration path and the runtime export can name different files. Package metadata selects a type entry separately from the executed entry, and `.d.mts`, `.d.cts`, and `.d.ts` take their format from their own naming and package scope ([TypeScript modules: Reference](https://www.typescriptlang.org/docs/handbook/modules/reference.html)). A consumer can type-check against a declaration whose shape the runtime never provides.

### A Documented Wording Difference

Two publisher pages describe an unmarked `.js` file differently:

- The rolling TypeScript Handbook Modules: Theory page contrasts the CommonJS-only era of "Node.js v11 and earlier" with modern module support, and its example states that a `.js` file in a package without `"type": "module"` is CommonJS ([TypeScript modules: Theory](https://www.typescriptlang.org/docs/handbook/modules/theory.html)).
- The Node v26.13.1 Modules: Packages page documents both CommonJS and ESM, classification by `.mjs`/`.cjs` and the nearest package `type`, and syntax detection for ambiguous input ([Node.js modules: Packages](https://nodejs.org/api/packages.html#determining-module-system)).

The difference is one of completeness and emphasis, not a contradiction about which module systems Node supports. The TypeScript passage compresses a historical transition and does not restate syntax detection; the Node page makes that condition explicit for its own version. Do not turn either passage into a universal rule: name the runtime, its version, and the package markers of the file in question instead of inferring a format from the word Node or from TypeScript source syntax.

## Package Managers, Lockfiles, And Workspaces

The runtime and the package manager are independent axes. npm, pnpm, Yarn generations, and Bun have manager-specific installation, lockfile, workspace-linking, script, and configuration behavior; a shared `package.json` field does not prove identical implementation semantics across managers.

When a task needs package context, distinguish the selected manager and version, the lockfile, package and workspace membership, the install layout, the scripts, runtime declarations, and the task graph. Workspaces can link local packages and define repository-specific task relationships, but manager support and behavior vary. A Corepack or version-manager declaration does not prove which executable the current shell used.

Treat lockfiles as manager-specific resolution records. Do not assume that multiple lockfiles are interchangeable or that deleting one is harmless. Identify the authoritative lockfile and effective workspace root from project evidence before drawing conclusions about the installed graph.

These distinctions define vocabulary and state types. Which wrapper started, which executable ran, and which working directory and workspace root applied is invocation evidence: see [Manager, Workspace, And Invocation Evidence](manager-workspaces-and-invocation.md).

## Project Scope And Applicability

Determine whether the target is an application, service, command-line product, library, package, or multi-package repository. A CLI product is not automatically a repository utility. Browser-only or edge work is in scope here only when the requested outcome concerns a Node or Bun execution, package, build, or integration surface. Structuring a project for a change belongs to `node-domain-planning -> reference/project-structure.md`.

The repository's `scripts/node/` tree is a separate, deterministic utility workspace with its own Bun and repository-specific conventions. Its defaults do not establish a general Node or Bun application stack.

## Reconcile Mixed Runtime Clues

This section is the canonical home of the mixed-clue case. Other pages route a mixed manager-and-runtime observation here instead of restating it; the production reading of the same clues is handled in `node-project-writer -> reference/change-design-and-validation.md`.

Suppose a repository contains `bun.lock`, a package script `"start": "node server.js"`, a `tsconfig.json`, and a green test command. Each clue answers a different question:

- `bun.lock` is manager state. It records Bun lockfile resolution, not that application code executes under Bun, because Bun documents `bun install` as usable in existing Node projects ([Bun install](https://bun.com/docs/pm/cli/install)).
- The script declares a `node` command but does not show that this script ran. Identify the package or workspace script and the exact wrapper invoked; Bun's launcher documents shebang-sensitive behavior and a `--bun` override, so do not infer the effective runtime without the actual invocation ([Bun runtime](https://bun.com/docs/runtime)).
- A green test command establishes only the selected test execution and its assertions. It does not establish that the test runner checked the program's types or that the production entry point uses the same runtime. Runner interpretation belongs to [Test Execution And Measurement](test-execution-and-measurement.md).
- Module mode comes from the relevant package boundary and file extensions, not from the lockfile. On Node v26.13.1 an ambiguous `.js` file without an explicit marker may undergo syntax detection, so check the target version and the actual invocation rather than treating a missing `type` field as decisive ([Node.js modules: Packages](https://nodejs.org/api/packages.html#determining-module-system)).

For a concrete diagnosis, record the working directory, exact command, package script, runtime version, package boundary, and effective TypeScript configuration and file list. If `bun.lock` coexists with another lockfile, that establishes competing repository evidence, not which manager the team intends to use. If the command or configuration actually selected is unavailable, stop at that uncertainty rather than asserting runtime or type-check coverage. Bun documentation is rolling; its described launcher and installation behavior is not a cross-manager equivalence test.

A changed `.ts` file that is absent from a green check is a question about the check's scope, which is diagnosed in `node-quality-workflow -> reference/quality-scope-and-mutation.md`. Do not change a package's module format or rewrite imports to clear a resolution mismatch until the consumer contract is known: the loader that already consumes the current format may be the one being protected.
