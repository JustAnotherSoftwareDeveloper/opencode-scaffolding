# Quality Scope And Tool Effects

## Scope

This page interprets why a quality command passed, missed a file, or changed output. It separates five questions that a command's name or exit status can hide: which compiler program the command covered, which lint or format target set it covered, whether it checked types, whether it only transformed or emitted files, and whether it wrote to the source. The subject is TypeScript source, configuration, declarations, tests, and quality diagnostics in Node.js or Bun projects. JavaScript-only work is out of scope, and this page excludes JavaScript eligibility, `allowJs` and `checkJs` guidance, JavaScript diagnostics, and JSDoc typing of `.js` files.

The page states passive mechanisms and interpretation. Commands, configuration changes, and remediation belong to outcome owners. Each statement stays with its named tool, version, mode, or configuration, because the cited publisher pages are rolling or version-scoped and either kind can change.

## Five Check-Versus-Target Distinctions

### Compiler Program Membership Compared With A Successful Check

A TypeScript check evaluates the compiler program selected by the invocation: the working directory, the selected configuration, its root-file rules, and any referenced projects. Program membership is not the set of `.ts` files in the repository, and a file present on disk is not automatically a member. A green exit records that the selected program produced no reported errors under its options; it does not record that the intended package script ran or that a different command checked the file.

A successful run shows the files it checked, not that a changed file was in the program. The missing-file diagnosis, including `--showConfig` and `--listFilesOnly`, is canonical in `node-quality-workflow -> reference/quality-scope-and-mutation.md`; this page does not restate it ([TypeScript CLI](https://www.typescriptlang.org/docs/handbook/compiler-options), [TSConfig reference](https://www.typescriptlang.org/tsconfig/)).

### Typed Lint Compared With Ordinary Lint

Ordinary lint evaluates configured rules against the files the lint command selected. Typed lint gives selected rules type information through the linter's own parser or project service. In typescript-eslint, current documentation recommends `languageOptions.parserOptions.projectService: true`, older setups use `project`, and `allowDefaultProject` admits selected files outside the project. That mechanism is a lint feature, not a compiler mode: a file can receive a type-aware lint diagnostic while the compiler program omits it, or sit in the compiler program while the lint command does not select it. A compiler check likewise runs no lint rules.

The consequence is that neither green result substitutes for the other. Record which lint configuration and parser project supplied type information, and do not treat a typed-lint pass as a compiler check or a compiler pass as lint coverage ([typed linting](https://typescript-eslint.io/getting-started/typed-linting/), [parser options](https://typescript-eslint.io/packages/parser/)).

### Formatter Target Sets Compared With Checked Files

A formatter check covers the files its own invocation and configuration selected. Prettier, for example, classifies each argument as a literal file or directory first, otherwise expands a glob with its own implementation, skips `node_modules` by default, and resolves configuration upward from each formatted file. Its selection is not a definition of the compiler program or of a linter's targets. Formatting parses and reprints source; it does not evaluate general code-quality rules or TypeScript types.

Consider `prettier --check "src/**/*.ts"` run from a repository root. It reports differences for the files that pattern and the effective configuration select. It says nothing about `packages/api/src/route.ts` if that path was outside the pattern, and nothing about type or lint state for any selected file. The consequence is that a clean formatter result supports only the formatted target set; compare effective target sets rather than assuming one tool covers another's files ([Prettier CLI](https://prettier.io/docs/cli)).

### Transform And Build Output Compared With A Check

Transformation and checking are different jobs. Bun execution transpiles TypeScript and TSX before running and does not check types; `--check` and `bun check` are separate interfaces that check before running. TypeScript distinguishes a checker-only invocation from one that emits output: `--noEmit` suppresses compiler output files while retaining the checker role, and an ordinary invocation can emit JavaScript and declarations according to configuration. Build mode `tsc --build` traverses project references and rebuilds out-of-date projects, so it can write generated files; `--clean` deletes outputs and `--dry` shows what would be built or deleted.

A produced `.js` or `.d.ts` file is an artifact, not a passing type-check record. A declaration describes a static interface and performs no runtime validation. An artifact that builds can still fail in a consumer because its entry points, included files, module format, or dependency assumptions do not match. The consequence is that a green check, an emitted artifact, and a consumer result are three separate observations; the tool that checks need not be the tool that produces the artifact, and a successful compilation does not prove the selected runtime can load every dependency ([Bun runtime](https://bun.com/docs/runtime), [Bun type checking](https://bun.com/docs/runtime/check), [noEmit](https://www.typescriptlang.org/tsconfig/noEmit.html), [project references](https://www.typescriptlang.org/docs/handbook/project-references.html)).

### Check Mode Compared With Write Mode

A quality command can report, preview a fix, or rewrite files. The selected tool, flags, and wrapper decide which effect occurs; the command label does not. Examples span the tool families:

- TypeScript `--noEmit` writes no compiler outputs, while build mode can write generated files and `--clean` deletes outputs.
- ESLint without a fix flag reports, `--fix` writes fixable changes into files, and `--fix-dry-run` obtains fixes and reports them without saving changes.
- Biome `check` reports unless write or fix behavior is enabled; `check --write` applies formatting, safe lint fixes, and safe assists, and `--unsafe` extends a combined command to unsafe fixes and assists. `lint` and `format` have their own write variants.
- Prettier `--check` reports whether selected files differ from formatter output, while `--write` overwrites processed files.

The consequence is that a "check" label is not evidence of non-mutation and a "clean" result does not establish that a later fix would be empty. Record the diagnostic-only, fix-preview, or mutating mode before interpreting a result, and confirm that source mutation is authorized before invoking a write mode ([TypeScript CLI](https://www.typescriptlang.org/docs/handbook/compiler-options), [ESLint CLI](https://eslint.org/docs/latest/use/command-line-interface), [Biome CLI](https://biomejs.dev/reference/cli/), [Prettier CLI](https://prettier.io/docs/cli)).

## Target Selection For Lint And Format Tools

ESLint, Biome, and Prettier each derive a target set from their own invocation and configuration. The per-tool detail, including no-match handling and configuration discovery, is owned by `node-quality-workflow -> reference/lint-and-format-target-selection.md`; the summary here is only enough to keep the five distinctions above separate.

ESLint's CLI targets explicit file paths, directories, or globs and uses the current directory when no path is supplied. Under current flat configuration, configuration is determined for each target file by searching from that file's directory upward, and `--config` supplies an alternate configuration and stops that search. `files` and `ignores` patterns resolve from the configuration location, global ignores differ from per-object ignores, and the documented default extensions are JavaScript, so a TypeScript target needs a configuration that selects it.

Biome accepts file and directory paths, processes directories recursively, and uses the current working directory when no path is supplied. Its CLI glob arguments are expanded by the shell, configuration discovery starts at the working directory and searches parent directories and the documented home location, and `files.includes` sets a shared upper scope that per-tool includes can narrow. VCS-ignore behavior and the scanner also affect what is processed; the scanner can read supporting source or dependency metadata beyond the files that receive diagnostics.

Prettier treats each argument as a literal file or directory first and otherwise expands a glob with its own implementation; it skips `node_modules`, does not follow symlinks when expanding CLI arguments, and resolves configuration upward from each formatted file. `.prettierignore` uses gitignore syntax, and the CLI by default honors the `.gitignore` at its run location, while `--ignore-path` replaces the defaults unless they are also listed. Ignore selection follows the run location, so two invocations can apply different ignore sets while each is correct for its own working directory.

The three target sets need not agree. Do not use one tool's selection as another tool's scope, and do not infer a project-wide result from a command run in one directory ([ESLint configuration files](https://eslint.org/docs/latest/use/configure/configuration-files), [ESLint ignore files](https://eslint.org/docs/latest/use/configure/ignore), [Biome configuration guide](https://biomejs.dev/configuration/configure-biome/), [Biome configuration reference](https://biomejs.dev/reference/configuration/), [Prettier configuration](https://prettier.io/docs/configuration), [Prettier ignoring code](https://prettier.io/docs/ignore)).

## When A Pattern Matches No Files

A file pattern that expands to zero files is not a clean check. Depending on the tool version and flags, a no-match case may produce a tool error, a silent success, or an allowed empty result. An error may name the unmatched pattern; a silent success can leave a CI job green with no file checked; an explicitly allowed empty set can be intended for a filtered run but still establishes nothing about the intended source. A formatter check or linter that accepts an empty file list reports no differences or violations for an empty target set, which is not evidence about the files the project meant to check.

Do not assert a universal exit code or an example result for a no-match case until the installed tool's version, help or configuration, and actual invocation have been checked. This page makes no installed-tool no-match claim and records no such probe. The owner's target page expands the per-tool behavior and reporting expectations at `node-quality-workflow -> reference/lint-and-format-target-selection.md`.

## Tool Roles And Non-Interchangeability

Type checking, linting, formatting, transpilation, compilation, JavaScript emission, declaration generation, bundling, and standalone executable creation describe different jobs. A command-line product may combine several, so inspect the invoked command, its configuration, the included files, and the outputs rather than inferring behavior from its name.

Representative tool names illustrate those roles rather than rank a stack. TypeScript `tsc` covers checking and, according to options, emission. Transformation and bundling products such as esbuild and SWC occupy transform or build roles. Bun documents build and checker interfaces ([Bun bundler](https://bun.com/docs/bundler)), and package-oriented tools such as tsdown target artifact outputs ([tsdown](https://tsdown.dev/guide/how-it-works)). Those tools are not interchangeable: output module formats, declaration support, target assumptions, configuration scope, and runtime prerequisites differ. A type checker is not necessarily the artifact producer, and successful compilation does not prove the artifact's selected runtime can load every dependency. The names are examples, not a recommendation, ranking, complete catalog, tested combination, or supported stack.

Quality interfaces differ for the same reason. `tsc` and Bun's checker address static type diagnostics. ESLint with typescript-eslint, Biome, and Prettier have distinct linting, formatting, parser, project-selection, and mutation behavior. A tool name or a single wrapper command does not prove which files were checked or whether the mode mutates source. No universal formatter, checker, lint gate, threshold, or equivalent-diagnostics claim follows from any of these roles.

For package work, keep JavaScript outputs, declarations, package metadata and export conditions, packed file contents, and the consumer's module or runtime context distinct. A declaration describes a static interface and does not perform runtime validation. A package build can succeed and still fail for a consumer because entry points, included files, module format, or dependency assumptions do not match. Package artifact ownership and the consumer-resolution analysis belong to `node-package-distribution`; test-runner collection, execution, and coverage interpretation belong to the test-execution page and to `node-project-test-writer -> reference/test-design-and-measurement.md`. A runner that transforms TypeScript does not thereby type-check the project.

No step in this page selects or relies on Vite, and no command sequence here forms an implicit pipeline. An incidental dependency edge is neither direct selection evidence nor proof of graph absence; this page makes no blanket dependency ban and no graph-absence claim. Runtime execution and module resolution are interpreted separately in [Runtime And Project Structure](runtime-and-project-structure.md).

## Limits And Ownership

TypeScript CLI and TSConfig documentation establish compiler selection and configuration behavior; the installed compiler version and the exact invocation remain authoritative for edge behavior. ESLint, Biome, and Prettier target and configuration behavior is tool-version and configuration-specific. Current ESLint documentation describes flat configuration, so legacy `.eslintrc` configuration and older installed versions resolve differently. Biome's configuration reference exposed schema 2.6.6 and its language page stated TypeScript 5.9 support at access; those are documentation snapshots, not compatibility guarantees. The ESLint, Prettier, and Bun pages cited here are rolling and exposed no release number at access. No installed quality tool, version, or project target set was tested for this page, and no quality command was run.

This page owns interpretation only. Configuration and diagnostic work, including the missing-file diagnosis and per-tool target expansion, goes to `node-quality-workflow`. A source defect exposed by a diagnostic goes to `node-project-writer` as a report rather than an implicit repair. Test-file and coverage findings go to `node-project-test-writer`. Dependency, lockfile, package-manager, or runtime-selection changes go to `node-project-dependencies`, and package-artifact or consumer-facing declaration problems go to `node-package-distribution`. Work on this repository's `scripts/node/` utilities stays with `skill-script-node-writer` or `skill-script-node-test-writer`; those tool choices are not ordinary project defaults.

For a concrete result, report the tool and version when known, the exact command and flags, the working directory, the selected project or target set and how it was established, and the check or write mode. A passing command supports only the files and behavior its actual configuration and invocation covered. No cross-tool equivalence, compatibility promise, universal threshold, or complete-project coverage follows from a green result ([TypeScript TSConfig reference](https://www.typescriptlang.org/tsconfig/), [ESLint CLI](https://eslint.org/docs/latest/use/command-line-interface), [Biome CLI](https://biomejs.dev/reference/cli/), [Prettier CLI](https://prettier.io/docs/cli)).
