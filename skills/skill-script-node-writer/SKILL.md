---
name: skill-script-node-writer
description: "Use when generating deterministic TypeScript Node scripts from skill requirements, including cleye CLI entry points, library modules, shared lib modules, and package.json/biome.json/tsconfig registration."
class: operation
---

# Skill Script Node Writer

## Normalize Input

Map invocation context to one internal input object.
Define these required fields:

- **Script name** — kebab-case entry point name (e.g., `lint-md`).
- **Purpose** — What the script computes or processes.
- **Input contract** — CLI arguments, stdin format, or file paths the script reads.
- **Output contract** — stdout format (JSON preferred), exit codes, stderr behavior.
- **Dependencies** — npm packages required (e.g., `cleye`, `remark`).
- **Skill consumers** — Which skills will invoke this script.

`BLOCKED: Missing script name — provide a kebab-case entry point name.`
`BLOCKED: Missing purpose — describe what the script computes or processes.`
`BLOCKED: Missing input contract — define CLI arguments, stdin format, or file paths.`

## Procedure

Each step is one imperative action.
Do not delegate sub-tasks.

1. **Parse requirements** — Extract script name, purpose, input/output contracts, dependencies, and skill consumers from the normalized input.
   Validate script name is kebab-case.
   Validate dependencies exist in `package.json` or add them.

2. **Select platform** — Default to Python for general-purpose scripts.
   Choose Node only when the task requires Node-specific libraries (remark ecosystem, filesystem-heavy operations, or npm ecosystem tools).
   See `./reference/path-layout.md` for platform selection context.

3. **Generate CLI entry point** — Write `src/cli/<script-name>.ts` with a cleye command definition, typed arguments and options, JSON stdout output via `process.stdout.write`, and error handling via `process.stderr.write` with `process.exit`.
   Follow conventions in `./reference/cli-conventions.md`.

4. **Generate lib modules** — Write `src/lib/<script-name>/core.ts` with typed function signatures, explicit return types, and imports from `lib/shared/*` where applicable.
   Follow conventions in `./reference/path-layout.md`.

5. **Register dependencies in package.json** — Add required npm packages under `dependencies` or `devDependencies`.
   Add a script entry under `"scripts"`: `<script-name> = "bun src/cli/<script-name>.ts"`.
   Follow conventions in `./reference/tooling-config.md`.

6. **Ensure tooling config** — Create or update `biome.json` and `tsconfig.json` if absent.
   Follow conventions in `./reference/tooling-config.md`.

7. **Run validation** — Execute type check, lint, and `--help` verification.
   Report `BLOCKED: <step> failed — <details>` on any failure.

## Self-Validation

Each check is a yes/no assertion.

- Type check passes — `bun run --cwd <scripts-node-dir> tsc --noEmit` exits zero.
- Lint passes — `bunx biome check src/cli/<script-name>.ts src/lib/<script-name>/` exits zero.
- Script `--help` works — `bun run --cwd <scripts-node-dir> <script-name> --help` exits zero.

## Expected Output

One or more files under `scripts/node/`:

- `src/cli/<script-name>.ts` — cleye CLI entry point with typed arguments, JSON output, and error handling.
- `src/lib/<script-name>/core.ts` — Core logic module with typed signatures.

`package.json` script entry registered under `"scripts"`.
`biome.json` and `tsconfig.json` present or updated.

## Shared Conventions

This skill consumes shared reference documentation from the `skill-node-script-conventions` skill at `../skill-node-script-conventions/`. All generated scripts must conform to these conventions.

| Reference File | Description |
|---|---|
| `../skill-node-script-conventions/reference/typescript-node-style-guide.md` | TypeScript/Node style guide: Biome lint rule catalog, strict-mode flag breakdown, import ordering convention, naming conventions table, type annotation patterns, and coverage exemption conventions. |
| `../skill-node-script-conventions/reference/shared-lib-rules.md` | Five rules for shared library modules under `src/lib/shared/`: no CLI entry points, 100% coverage, consumer documentation in module-level JSDoc, domain-based naming, and extraction discipline. |
| `../skill-node-script-conventions/reference/path-layout.md` | Directory and file path conventions for Node scripts — `src/` layout, test layout, import conventions with `.ts` extensions, and module organization principles. |
| `../skill-node-script-conventions/reference/tooling-config.md` | Tooling configuration for `biome.json` (single quotes, semicolons asNeeded, indent 2, lineWidth 120), `tsconfig.json` (module: Preserve, types: [bun], strict flags), and `package.json` (bun deps, cleye, script entries). |
| `../skill-node-script-conventions/reference/bun-test-conventions.md` | Conventions for `bun:test` test files: globals, `Bun.spawnSync` CLI test pattern, fixture setup, parameterized tests, mocking patterns, and paired source-to-test file mapping. |
| `../skill-node-script-conventions/reference/coverage-strategy.md` | Coverage measurement via `bun --coverage`, source path boundaries, `fail_under = 100` threshold policy, 6-category edge case identification checklist, error path testing requirements, and c8 exemption conventions. |
| `../skill-node-script-conventions/reference/test-examples.md` | Complete runnable test examples covering CLI integration tests, file-based unit tests, module mocking, spy patterns, parameterized tests, and shared fixture helpers. |
| `../skill-node-script-conventions/reference/README.md` | Index of all reference files in the conventions skill with one-sentence descriptions. |

## Style Guide Coverage

Generated scripts must adhere to the shared conventions defined in `../skill-node-script-conventions/reference/`. The following areas are covered by this style guide:

### Naming Conventions

- **Script names** — kebab-case matching the entry point file name (e.g., `lint-md`, `format-json`). Used as the `package.json` script key and `src/lib/` directory name.
- **Files** — kebab-case `.ts` for CLI entry points (`src/cli/<script-name>.ts`), lib modules (`src/lib/<script-name>/<module>.ts`), shared libs (`src/lib/shared/<module>.ts`), and test files (`tests/<name>.test.ts`, `tests/<name>.cli.test.ts`).
- **Identifiers** — camelCase for functions (`lintFile()`, `resolveTarget()`), PascalCase for const enums and types (`ExitCode`, `LintResult`), branded types for path-like identifiers.
- **Shared libs** — Domain-based naming (`exit-codes.ts`, `format.ts`, `path.ts`) not consumer-based (`lint-md-utils.ts`).

### Path and Project Layout

- Generated scripts live under `scripts/node/` with the canonical layout: `src/cli/`, `src/lib/<name>/`, `src/lib/shared/`, `tests/`.
- CLI entry points are thin — parse args, call lib functions, handle errors. Business logic lives in `src/lib/`.
- Imports use relative paths with `.ts` extensions (Bun requirement), organized in three groups (Node built-ins, third-party, local) separated by blank lines.
- No barrel files (`index.ts`) — import directly from source modules.

### Tooling Configuration

- `biome.json` — Enforces single quotes, semicolons asNeeded, 2-space indent, 120 line width. Covers both `src/**/*.ts` and `tests/**/*.ts`. Installed with `bun add -d -E @biomejs/biome`.
- `tsconfig.json` — Uses `module: "Preserve"`, `moduleResolution: "bundler"`, `strict: true`, `noUncheckedIndexedAccess`, `verbatimModuleSyntax`, `exactOptionalPropertyTypes`, `types: ["bun"]`.
- `package.json` — ESM module (`"type": "module"`), `cleye` as runtime dependency, `bun` scripts for CLI entry points and test invocation.

### Testing and Coverage

- Unit tests use direct imports from lib modules with `bun:test` globals (`describe`, `test`, `expect`, `beforeAll`, `afterAll`).
- CLI integration tests use `Bun.spawnSync` to invoke entry points, asserting on `exitCode` and `stdout`/`stderr` content.
- Fixture setup follows `mkdtempSync` + `beforeAll` / `rmSync` + `afterAll` pattern with temp directories.
- Coverage target is `fail_under = 100` via `bun test --coverage`. Every `process.exit()` code path must have a corresponding `Bun.spawnSync` test.
- Coverage exemptions are limited to three categories: unreachable defensive code, type narrowing fallthroughs, and `@ts-expect-error` suppressions.
- The 6-category edge case checklist (input, file I/O, CLI arguments, error handling, output, boundary values) guides test completeness.

## Docs

See `./reference/README.md` for this skill's reference file index.
See `../skill-node-script-conventions/reference/README.md` for the shared conventions reference file index.