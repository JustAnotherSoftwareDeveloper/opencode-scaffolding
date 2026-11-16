# Quality Scope And Mutation

This page owns the cross-tool questions for standalone quality work on TypeScript in Node.js or Bun projects: which responsibility a command performs, which files a compiler invocation includes, why a changed file can be absent from a green check, and whether an invocation reports or writes. It is the canonical home of the missing-file diagnosis.

It is not the home of per-tool target expansion. Working directory, configuration lookup, ignore handling, scanner inputs, and the no-files-matched case for ESLint, Biome, and Prettier belong to [Lint And Format Target Selection](lint-and-format-target-selection.md); a short cross-owner summary belongs to `node-project-reference -> reference/quality-scope-and-tool-effects.md`.

The subject is TypeScript source, TypeScript configuration, declaration output, TypeScript tests, and TypeScript quality diagnostics in Node.js or Bun projects. JavaScript-only work and JavaScript or mixed-language eligibility are out of scope, and a JavaScript-only request is reported as out of scope rather than answered with TypeScript guidance.

## Keep Responsibilities Distinct

Quality tools can share command interfaces without doing equivalent work. A TypeScript compiler check evaluates types within its configured program. Runtime TypeScript execution or transpilation can transform code without checking types. A linter evaluates configured rules; typed linting consults type information for selected rules but is not interchangeable with a separate compiler check. A formatter parses and rewrites source for formatting rather than evaluating general code-quality rules. A product may combine several of these operations, so name the work performed rather than treating a bundled command as one indivisible check. A successful check does not establish runtime behavior or validate emitted artifacts.

Typed linting uses the linter's own mechanism, not the compiler's. In typescript-eslint, the parser supplies type information for the files a rule requests it for: current documentation recommends `languageOptions.parserOptions.projectService: true`, older setups use `project`, and `allowDefaultProject` admits selected files outside the project. A file can therefore receive a type-aware lint diagnostic while a compiler file-list probe omits it, or sit in the compiler program while the lint command does not select it. Neither result substitutes for the other. Program membership remains the compiler question diagnosed below; per-tool file selection belongs to [Lint And Format Target Selection](lint-and-format-target-selection.md).

The common compile-time signal for a detached method shows the split. Referencing `obj.method` and calling it without a receiver produces no general compiler error; the TypeScript project records that omission as a design limitation ([issue #35451](https://github.com/microsoft/TypeScript/issues/35451), [issue #46027](https://github.com/microsoft/TypeScript/issues/46027)). TS2684 appears only when the declaration has an explicit `this` parameter and the call supplies an incompatible receiver, while `noImplicitThis` (TS2683) and `strictBindCallApply` check different things. The usual signal is the type-aware lint rule `@typescript-eslint/unbound-method`, which requires type information and is enabled by a type-checked configuration such as `recommended-type-checked`; its gate is typed-lint configuration, not `strict` ([typed linting](https://typescript-eslint.io/getting-started/typed-linting/), [unbound-method](https://typescript-eslint.io/rules/unbound-method/)). Methods annotated `this: void` and bound arrow-function class fields are the documented exemptions, and the rule's `ignoreStatic` option skips `static` methods. The runtime loss of the receiver is a separate behavior determined by the call site, not a compile-time diagnostic. These statements are bounded to the inspected TypeScript 5.9.3 compiler behavior and the current typescript-eslint documentation.

A compiler diagnostic can mean less than its name suggests. TS7016 reports that a module specifier resolved to a JavaScript file with no declaration file: "Could not find a declaration file for module ... implicitly has an 'any' type." With `noImplicitAny` enabled and a module being resolved, it is an error; with `noImplicitAny` disabled it is still produced, but as a suggestion diagnostic that `tsc` does not print and a language service can surface. The module remains untyped in both cases, so the flag changes the diagnostic's severity and display surface, not whether the import is `any`. TS2307 is the neighboring resolution-failure diagnostic for a specifier that resolves to nothing. In a TypeScript 5.x project, `strict` or `noImplicitAny` had to be enabled for TS7016 to be an error; the TypeScript 6.0 announcement states that `strict` is now `true` by default, so an unconfigured 6.0+ project has `noImplicitAny` effectively enabled ([TSConfig reference](https://www.typescriptlang.org/tsconfig/), [TypeScript 6.0](https://devblogs.microsoft.com/typescript/announcing-typescript-6-0/)). The error-versus-suggestion condition was verified in the pinned 5.9.3 compiler source and a bounded probe on one host with `module: commonjs` and `moduleResolution: node10`; do not extend it to every resolver, module mode, or TypeScript 7.x.

## Establish The Actual Target Set

Each tool has its own CLI and configuration rules. Determine its effective target from the invocation, working directory, config discovery, include/exclude or ignore settings, and project graph. TypeScript `exclude` limits files initially discovered through `include`; imports, references, explicit `files`, and type inclusions may still bring files into the program. Project references and build mode can change which projects are traversed. Linter globs, formatter arguments, and a checker's project membership are not portable definitions of the same file set.

Configuration inheritance changes this reading. `extends` loads the base configuration first, the child's own settings take precedence over the base, and a child's `files`, `include`, or `exclude` replaces the base value rather than adding to it. A project that inherits its roots can therefore select a different file set than either the base or the child suggests when only one file is read ([TSConfig reference](https://www.typescriptlang.org/tsconfig/)).

Plain `tsc` is not interchangeable with `tsc --build`. Build mode traverses project references and rebuilds out-of-date projects, whereas an ordinary compiler invocation does not automatically build referenced dependencies; the two can examine different projects. Build mode can also emit, so compare it with a diagnostic invocation as an effect question as well as a scope question ([Project References](https://www.typescriptlang.org/docs/handbook/project-references.html)).

For a workspace or monorepo, identify the package root and command context for each check. Report when tool scanners or project-aware rules may read additional files to understand the program, even if the set of files that receive diagnostics is narrower. Do not claim "all files" unless the effective selection has been established.

### Diagnose A Changed File Missing From A Green Check

Use the command that the project actually declares, but separate its wrapper from the compiler invocation. TypeScript CLI behavior makes the distinction material: running `tsc` without input files searches for a nearby configuration; passing file names directly ignores `tsconfig.json`; `--project` selects a configuration. In a monorepo, an unqualified `tsc` started at the repository root can therefore examine a different project than the package script that declares it. A package manager, task runner, or custom script can also change the working directory, add flags, or call a different binary, so the script text alone does not establish the compiler invocation that ran.

For an existing package script such as `"typecheck": "tsc --noEmit -p tsconfig.json"`, run read-only scope probes from that package's directory (or give the same explicit project path):

```sh
tsc --showConfig -p tsconfig.json
tsc --listFilesOnly -p tsconfig.json
```

Interpret the output as evidence, not as a diagnosis by itself:

- If the changed path is absent from `--listFilesOnly`, that invocation did not type-check that file. Check that the intended package script ran from the expected directory, confirm the selected config and any inherited `extends`, then inspect `files`, `include`, and project references. Do not treat the green exit as evidence about the missing file.
- If the path is present, it belongs to that compiler program; confirm the command completed with the expected checking options and no suppression or wrapper behavior that changes the result. Presence alone does not prove that a different package script, lint command, runtime, or build checked it.
- `exclude` only filters files discovered via `include`. An excluded file can still enter through an import, `files`, a type inclusion, or a triple-slash reference. Conversely, a file in the repository is not automatically part of the program.
- A referenced project's files are not automatically members of the referencing program. Build mode changes which projects are built, so confirm whether the relevant project references were built and whether the program consumes their declarations.

`--showConfig` prints the resolved configuration, including inherited options, and `--listFilesOnly` prints the compiler's file list; neither substitutes for inspecting the script or CI job that actually ran.

These probes report TypeScript's effective configuration and program membership for that compiler invocation. They do not show which command CI or a developer actually invoked unless you inspect that script/job, and they do not cover a different checker, editor service, build tool, or test runner. CLI and configuration behavior can vary with the installed TypeScript version; use the project's installed compiler and preserve its working directory and arguments.

### Separate Manager Clues From Runtime Clues

Manager evidence and runtime evidence answer different questions. A lockfile records a package manager's resolution. A package script's text declares a command. A `type` field and file extensions state module format. A green test or check records only the execution it selected. None of these selects another, and a lockfile does not prove which process ran the code.

The canonical worked case — a repository containing `bun.lock`, a `"start": "node server.js"` script, a `tsconfig.json`, and a green test command — is in `node-project-reference -> reference/runtime-and-project-structure.md#reconcile-mixed-runtime-clues`. Read that page for the clue-by-clue reconciliation; do not reconstruct a runtime from a manager file here.

The quality consequence is narrower. A check's scope comes from its compiler invocation, working directory, selected configuration, and wrapper, not from the manager that installed the tool. A root-level `tsc` in a monorepo may examine a different project than the package script that declares it, so run probes from the package directory or pass the explicit project path. If quality setup requires changing the package manager, the runtime selector, or dependencies, hand off that separate outcome to the dependency owner rather than making it an incidental quality edit.

## Distinguish Diagnostics From Writes

Record whether an invocation only reports diagnostics or can alter files. A command's label does not establish its effect; the tool, its flags, and any wrapper do.

- TypeScript: `noEmit` suppresses compiler output files while retaining the checker role, so it makes a compiler invocation non-writing for its own outputs only. Ordinary `tsc` emits according to configuration. Build mode `tsc --build` traverses project references, builds out-of-date projects, and can write generated files; `--clean` deletes outputs. Build mode documents `--dry` to show what would be built or deleted without doing it ([noEmit](https://www.typescriptlang.org/tsconfig/noEmit.html), [Project References](https://www.typescriptlang.org/docs/handbook/project-references.html)).
- Bun: ordinary execution transpiles TypeScript without checking types; `--check` and `bun check` are separate interfaces that check before running and exit non-zero on error. Neither makes a plain `bun run` a checker, so confirm which interface the script selects and which TypeScript configuration it uses ([Bun runtime](https://bun.com/docs/runtime), [Bun type checking](https://bun.com/docs/runtime/check)). Those pages are rolling documentation without a pinned release.
- Biome: `biome check` combines formatter, linter, and assist checks; as a diagnostic surface it reports unless write or fix behavior is enabled. `check --write` applies formatting, safe lint fixes, and safe assists, and `--unsafe` extends a combined command to unsafe fixes and assists. Safe and unsafe lint fixes are distinct, so `--write` alone applies less than every available fix. `biome lint` and `biome format` have their own write variants, and a project script can add further commands around any of them ([Biome CLI](https://biomejs.dev/reference/cli/), [Biome linter](https://biomejs.dev/linter/)).
- ESLint: a plain run reports configured rule diagnostics. `--fix` writes fixable changes into files; `--fix-dry-run` obtains fixes and reports them without saving changes. Use the dry run when a request must not mutate but the proposed fixes matter; it does not prove what a differently configured `--fix` run would change ([ESLint CLI](https://eslint.org/docs/latest/use/command-line-interface)).
- Prettier: `--check` reports whether selected files differ from formatter output; `--write` overwrites them. The check covers the files the command selected, not every file the project owns ([Prettier CLI](https://prettier.io/docs/cli)).

Inspect configuration before a check with read-only probes: `tsc --showConfig`, `eslint --print-config <file>`, and `prettier --find-config-path <file>` print resolved configuration without performing the check or a write. Treat them as context, not as evidence that the intended check ran or that a later mutation is impossible.

Use the project's diagnostic mode when the request is to inspect quality. Before any rewrite or fix, confirm that source mutation is explicitly within scope and identify the affected paths. Keep configuration changes separate from source remediation. A diagnostic that exposes a defect is evidence to report or hand off, not authority to fix it.

For example, a formatter's check mode and its write mode answer different questions: `prettier --check src` reports whether selected files differ from formatter output, while `prettier --write src` rewrites them. Likewise, an ESLint run without a fix flag reports, while `--fix` writes the fixes it can apply and `--fix-dry-run` previews them without saving. Verify the installed tool's help/configuration and the actual script before invoking it; do not assume these illustrative spellings match every tool version or project wrapper.

When output changes unexpectedly, compare the exact command, cwd, explicit paths/globs, config discovery, ignore rules, and tool version before changing configuration. A "no files matched" or clean result over an empty target set is not a passing check of the intended source. If the discrepancy is a coverage percentage after a test move, treat coverage's source universe and test collection as the relevant evidence rather than a type/lint/format result.

No mutation command was executed as evidence for this page. The statements above classify publisher-documented effects; a specific project's installed versions, flags, and wrappers must be verified before relying on them, and no observed-mutation claim is made for an uninspected project.

## Preserve Compatibility Qualifications

Establish the selected runtime separately from the package manager used to install or invoke a tool. Tool requirements may concern the runtime executing the CLI or loading its config, and those constraints can differ from package-manager examples. Node.js and Bun are distinct execution contexts; Bun-specific checker settings or declarations are not universal Node settings. Confirm exact installed versions and project configuration before relying on version-sensitive behavior.

No single tool set, quality gate, threshold, diagnostic equivalence, or Node/Bun compatibility matrix follows from representative tool documentation. Publisher statements describe their documented version and use case; they are not cross-tool benchmark results or project-specific tests. Treat project configuration as the governing source for current quality commands and thresholds.

## Report Evidence Precisely

For every relevant check, record:

- tool and version when known;
- exact command, flags, and working directory;
- project/package or file scope and how it was established;
- diagnostic-only, fix-preview, or mutating mode;
- the files the tool read and the files that received diagnostics when those sets differ;
- result, including failures, skips, unavailable commands, and existing findings; and
- relevant runtime/configuration gaps that limit the conclusion.

A passing command supports only the files and behavior that its actual configuration and invocation checked. It does not prove complete project coverage, runtime compatibility, absence of other diagnostics, or artifact correctness. A clean result over an empty or unintended target set establishes nothing about the intended source.

## Route Findings To Owners

Keep the quality diagnosis with this owner and route the underlying outcome to its owner:

- A lint, type, or format finding that exposes a production source defect goes to `node-project-writer` as a report; do not repair source under a diagnostic-only request.
- A test-file or coverage finding, including coverage drift after a test move, goes to `node-project-test-writer`.
- A change to dependencies, lockfiles, package-manager state, or runtime selection goes to `node-project-dependencies`; see `node-project-dependencies -> #routing-boundaries`.
- A package-artifact or consumer-facing declaration problem goes to `node-package-distribution`.
- Work on this repository's `scripts/node/` utilities goes to `skill-script-node-writer` or `skill-script-node-test-writer`; their tool choices are not ordinary project defaults.

Configuration changes for this project's TypeScript, ESLint, Biome, Prettier, or other quality tools stay with this standalone quality owner. Keep a quality configuration change separate from dependency installation and from source remediation.

## Primary Documentation For Mechanism Checks

These links describe tool-specific behavior, not a prescribed stack. Recheck the installed version and project configuration before applying an option:

- [TypeScript CLI options](https://www.typescriptlang.org/docs/handbook/compiler-options) documents project selection, explicit file arguments, `--showConfig`, `--listFilesOnly`, and build mode.
- [TypeScript TSConfig reference](https://www.typescriptlang.org/tsconfig/) documents `files`, `include`, `exclude`, `extends` inheritance, and the `noImplicitAny`, `noImplicitThis`, and `strictBindCallApply` options.
- [TypeScript project references](https://www.typescriptlang.org/docs/handbook/project-references.html) documents build mode, `--build`, `--clean`, and `--dry`.
- [TypeScript noEmit](https://www.typescriptlang.org/tsconfig/noEmit.html) documents compiler output suppression.
- [typescript-eslint typed linting](https://typescript-eslint.io/getting-started/typed-linting/) and [unbound-method](https://typescript-eslint.io/rules/unbound-method/) document type-aware lint configuration and the detached-method rule; [parser options](https://typescript-eslint.io/packages/parser/) documents `projectService` and `project`.
- [ESLint CLI](https://eslint.org/docs/latest/use/command-line-interface) documents `--fix`, `--fix-dry-run`, and configuration lookup options.
- [Biome CLI](https://biomejs.dev/reference/cli/) and [Biome linter](https://biomejs.dev/linter/) document `check`, write variants, `--unsafe`, and safe versus unsafe fixes.
- [Prettier CLI](https://prettier.io/docs/cli) documents `--check`, `--write`, and configuration lookup.
- [Bun runtime](https://bun.com/docs/runtime) and [Bun type checking](https://bun.com/docs/runtime/check) document script launch, `--bun`, and the separate check interfaces; [Bun install](https://bun.com/docs/pm/cli/install) documents Bun as a package manager usable in Node projects and does not make a lockfile evidence of runtime selection.
- [c8 README](https://github.com/bcoe/c8) explains the loaded-file default and how `--all`, source roots, and include/exclude patterns change its coverage universe. This is rolling project documentation, not a pinned release guarantee.
- [Node.js v26.13.0 test runner coverage](https://nodejs.org/docs/latest-v26.x/api/test.html#collecting-code-coverage) documents that version's built-in coverage controls and experimental status. Do not transfer those defaults to c8 or another provider.
