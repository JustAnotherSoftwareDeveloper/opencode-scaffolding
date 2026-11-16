# Lint And Format Target Selection

## Scope

This page answers one question: which files did a given ESLint, Biome, or Prettier invocation target, which configuration and ignore rules applied, and which files actually received diagnostics. It expands the per-tool mechanisms that the quality-scope page deliberately leaves generic. [Quality Scope And Mutation](quality-scope-and-mutation.md) keeps the cross-tool target-set principles, the TypeScript missing-file diagnosis, and check-versus-write semantics; this page is the canonical home for the per-tool expansion. The shared distinction summary is `node-project-reference -> reference/quality-scope-and-tool-effects.md`.

The subject is TypeScript work in Node.js or Bun projects. JavaScript-only work is out of scope, and this page does not establish JavaScript or mixed-language eligibility. A tool's documentation describes its own mechanism; the project's exact command, working directory, effective configuration, installed version, and argument expansion establish what ran. No command result in this page is a claim about an uninspected project.

## Establish The Invocation

Record the following before interpreting a result:

- tool and installed version;
- exact command and flags, including check versus write mode;
- working directory and package or workspace root;
- whether the shell or the tool expanded the file arguments;
- configuration files found and the scope each governs;
- ignore files and ignore patterns that applied; and
- the files the tool read and the files that received diagnostics.

Quote patterns such as `"src/**/*.ts"` when the tool should expand them. ESLint and Biome document shell expansion of unquoted glob arguments, and Prettier uses its own glob implementation for non-literal arguments. An unquoted pattern can therefore reach the tool as a different list, or as no arguments, before any tool rule applies. Record the effective argument list, not only the typed command.

A package script is not the invocation by itself. The script text, its working directory, the wrapper it calls, and the actual tool binary each answer a different part of the question. Run a scope probe from the package directory or pass the explicit package or configuration path when the command's working directory is uncertain. The compiler-side version of this problem is diagnosed in Quality Scope And Mutation; for the lint and format tools, the same discipline applies to their own working directory and configuration discovery.

## ESLint Per-File Configuration Lookup

ESLint's CLI targets explicit file paths, directories, or globs. Without paths it uses the current directory. Current flat-config documentation determines configuration for each target file by searching from that file's directory upward; `--config` supplies an alternate configuration and stops that search. The `files` and `ignores` patterns in a configuration resolve relative to that configuration's location, or relative to the working directory for an alternate configuration. Global ignores and per-object ignores are different mechanisms, and the documented default extensions are JavaScript, so a TypeScript target needs a configuration that selects `.ts` or `.tsx` patterns and a TypeScript parser.

A nested configuration changes the rules for one directory. If `packages/app/eslint.config.mjs` exists, files under `packages/app` can use it even when the command starts at the repository root, because lookup begins at each file's directory. Path selection and configuration selection are separate: a root pattern such as `"src/**/*.ts"` does not reach `packages/app/src/main.ts`, while `eslint .` does select the package file but still resolves the package's own configuration for it. The root configuration does not automatically reach a file governed by the nearer package configuration. Check both layers rather than assuming one root configuration governs the tree.

Version and configuration bound: this describes the current flat-config system. The cited pages are rolling and did not expose a release number at access; the installed ESLint version and flat or legacy configuration system define the applicable rules. Legacy `.eslintrc` configuration and older installed versions resolve and cascade differently. Identify the installed ESLint version and configuration system before applying the mechanism. Sources: [CLI reference](https://eslint.org/docs/latest/use/command-line-interface), [configuration files](https://eslint.org/docs/latest/use/configure/configuration-files), [ignore files](https://eslint.org/docs/latest/use/configure/ignore), [typescript-eslint getting started](https://typescript-eslint.io/getting-started/).

## Biome Working Directory, Configuration, And Scanner Inputs

Biome accepts file and directory paths, processes directories recursively, and uses the current working directory when no path is supplied. Its CLI glob arguments are expanded by the shell. Configuration discovery starts at the CLI working directory and searches parent directories, then the documented home configuration location; nested configurations and `extends` affect the settings applied to a project. `files.includes` is the shared upper scope, and per-tool `includes` can narrow it. VCS-ignore behavior and scanner processing also affect what is read.

A nested `packages/app/biome.json` can change linter or formatter settings for files under that package, while a root `biome check .` and a package `biome check src` start from different working directories and can apply different effective settings. Record the working directory, the configuration that started discovery, and any nested configuration that applies.

### Scanner Inputs Are Not Diagnostic Targets

The scanner read set and the diagnostic set are different sets, and a count from one is not a count from the other. Biome's scanner may index supporting source or dependency metadata needed by project or type rules beyond the files that receive the immediate diagnostics. Suppose `packages/app/src/ui/Widget.tsx` is excluded from Biome's diagnostic targets by an ignore rule but is imported by a selected file that a project rule analyzes. The scanner may still read `Widget.tsx` to obtain project or type context; that read does not mean the file was linted or formatted, and no diagnostic is reported against it. Report the read set separately from the diagnosed set.

The same separation appears in type-aware linting: the parser service can read TypeScript program files that are not ESLint targets in order to answer a rule. A file that contributes type information is not thereby a lint target, and a lint target that receives a diagnostic is not thereby part of the compiler's program.

Version and configuration bound: the Biome CLI, configuration, and language pages are rolling documentation. At access the configuration reference exposed schema 2.6.6 and the language page stated TypeScript 5.9 support; those are documentation snapshots, not a compatibility guarantee for an installed version. The installed Biome version, its schema, and the project's `biome.json` remain authoritative. Sources: [CLI](https://biomejs.dev/reference/cli/), [configuration guide](https://biomejs.dev/configuration/configure-biome/), [configuration reference](https://biomejs.dev/reference/configuration/), [language support](https://biomejs.dev/introduction/language-support/), [linter](https://biomejs.dev/linter/).

## Prettier Path Expansion, Configuration, And Ignore Rules

Prettier treats each CLI argument first as a literal file or directory; it recursively selects supported files from directories, and otherwise expands the argument as a glob with its own glob implementation. It skips `node_modules` by default, does not follow symlinks when expanding CLI arguments, and applies ignore rules. Configuration is found starting from the formatted file and walking upward; configuration-file precedence is distinct from configuration-versus-CLI option precedence, and `overrides` paths are relative to their configuration file. `.prettierignore` uses gitignore syntax, and the CLI by default honors the `.gitignore` at its run location; `--ignore-path` replaces the default ignore path unless the defaults are also listed.

A nested configuration therefore follows the file: a package-local Prettier configuration changes the formatting options for files under that package even when the command starts at the repository root, because resolution walks upward from each formatted file. Ignore selection is different: it follows the invocation's run location. That difference produces the common root-versus-CI disagreement.

### Root Check Versus Package CI

Suppose the root `.prettierignore` excludes `packages/web/src/generated/**/*.ts` and `packages/web/.prettierignore` does not. A root `prettier --check "packages/*/src/**/*.ts"` does not select the generated TypeScript files, so it can report no change. A CI job in `packages/web` runs `prettier --check "src/**/*.ts"` and reports those files as different. The root run is not a superset of the package run: each command expands its own arguments, resolves configuration from each formatted file, and applies the ignore rules of its run location. Reproduce the CI command, working directory, and ignore files before treating the root result as the project's formatting state.

Version and configuration bound: this is the current CLI, configuration, and ignore documentation. The cited pages are rolling and did not expose a release number at access; the installed Prettier version defines the applicable behavior. Parser and plugin availability, ignore-file details, and option defaults remain specific to that version. Sources: [CLI](https://prettier.io/docs/cli), [configuration](https://prettier.io/docs/configuration), [ignoring code](https://prettier.io/docs/ignore), [Prettier versus linters](https://prettier.io/docs/comparison).

## Typed Lint Is Not Program Membership

Typed lint uses type information for the lint rules that request it. In typescript-eslint, the parser's project service supplies that information; current documentation recommends `languageOptions.parserOptions.projectService: true`, while older setups use `project`. The project service can also admit selected out-of-project files through `allowDefaultProject`. That route gives the parser type information for a selected file; it does not make the file a member of an ordinary `tsc` program.

The distinction matters when a green typed-lint run is offered as evidence about a compiler check. A file can receive a typed-lint rule diagnostic while `tsc -p tsconfig.json --listFilesOnly` omits it, or a file can be in the compiler program while the lint command does not select it. Neither result substitutes for the other. Program membership, `tsc` selection, and the missing-file diagnosis remain in Quality Scope And Mutation.

### A Typed-Lint Example

```ts
import tseslint from "typescript-eslint";

export default tseslint.config(
  ...tseslint.configs.recommendedTypeChecked,
  {
    files: ["**/*.ts"],
    languageOptions: {
      parserOptions: {
        projectService: {
          allowDefaultProject: ["tools/*.ts"],
        },
      },
    },
  },
);
```

```ts
// tools/report.ts — admitted to typed lint, absent from tsconfig.json
class Report {
  render(value: string) {
    return value.trim();
  }
}

const render = new Report().render;
const line = render("  total  ");
```

This configuration can give the parser type information for `tools/report.ts` and let `@typescript-eslint/unbound-method` evaluate the detached `render` reference. It does not add `tools/report.ts` to `tsconfig.json`; a compiler file-list probe can omit the file while typed lint reports on it. The example shows a configured rule using type information, not a full compiler check of the program.

The compiler side is narrower than the rule name suggests. The TypeScript project labels the general detached-method omission a design limitation ([issue #35451](https://github.com/microsoft/TypeScript/issues/35451), [issue #46027](https://github.com/microsoft/TypeScript/issues/46027)); TS2684 appears only when the declaration has an explicit `this` parameter and the call supplies an incompatible receiver. `noImplicitThis` (TS2683) and `strictBindCallApply` address different checks. The `unbound-method` gate is type-aware lint configuration, not `strict`. This distinction is bounded to the inspected TypeScript 5.9.3 compiler behavior and the current typescript-eslint documentation; do not extend it to every compiler or rule version. Sources: [typed linting](https://typescript-eslint.io/getting-started/typed-linting/), [parser options](https://typescript-eslint.io/packages/parser/), [typed-lint troubleshooting](https://typescript-eslint.io/troubleshooting/typed-linting/), [unbound-method](https://typescript-eslint.io/rules/unbound-method/), [TSConfig reference](https://www.typescriptlang.org/tsconfig/).

## When No Files Match

A file pattern that expands to zero files can produce an error, a silent success, or an allowed empty result, depending on the tool version and flags. An error may name the unmatched pattern; a silent success can make a CI job green with no file checked; an explicitly allowed empty set can be intended for a filtered run but still establishes nothing about the intended source. Do not encode a universal exit code or an example result for "no files matched" without checking the installed tool's version, help output, and actual invocation.

The empty case is easy to confuse with a clean case. A formatter check that accepts an empty file list reports no formatting differences; a linter that accepts one reports no rule violations; neither result covers the files the project meant to check. Report the effective argument list, the number of files selected, and the tool's no-match behavior. If the shell expanded a pattern to nothing, restore the intended argument and run the tool from the intended directory before drawing a conclusion.

## Route Findings And Configuration Changes

Keep the quality diagnosis with this owner and route the underlying outcome to its owner:

- A lint or format finding that exposes a production source defect goes to `node-project-writer` as a report; do not repair source under a diagnostic-only request.
- A test-file or coverage finding goes to `node-project-test-writer`.
- A change to dependencies, lockfiles, package-manager state, or runtime selection goes to `node-project-dependencies`; see `node-project-dependencies -> #routing-boundaries`.
- A package-artifact or consumer-facing declaration problem goes to `node-package-distribution`.
- Work on this repository's `scripts/node/` utilities goes to `skill-script-node-writer` or `skill-script-node-test-writer`; their tool choices are not ordinary project defaults.

Configuration changes for ESLint, Biome, or Prettier stay with this standalone quality owner. Keep a quality configuration change separate from dependency installation and from source remediation. A finding is evidence to report or hand off, not authority to fix the code that produced it.

## Limits And Evidence To Report

ESLint, Biome, and Prettier target and configuration behavior is tool-version-specific. The pages cited here are rolling or version-scoped, and a project's installed versions, configuration files, ignore rules, and wrapper commands can change the effective set. No cross-tool target-set equivalence, implicit pipeline, or compatibility promise follows from this page: one tool's run does not establish that another tool ran, and a passing lint or format result does not establish a compiler check or runtime behavior.

Report tool and version, exact command and flags, working directory, effective argument list, configuration files and their scope, ignore files, read set, diagnosed set, and check-versus-write mode. State when the installed version's no-match or configuration behavior was not verified. For TypeScript program membership and mutation semantics, use [Quality Scope And Mutation](quality-scope-and-mutation.md). Do not select Vite or a framework workflow from an incidental dependency edge, and do not claim dependency-graph absence without project-specific evidence.
