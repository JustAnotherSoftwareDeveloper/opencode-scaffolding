---
name: skill-script-node-writer
description: "Use when generating deterministic TypeScript Node scripts from skill requirements, including cleye CLI entry points, library modules, shared lib modules, and package.json/biome.json/tsconfig registration."
tags: [node-code-generation, typescript, cleye, cli, package-json, node-scripting]
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

This skill consumes shared reference documentation from the `skill-node-script-conventions` skill. All generated scripts must conform to these conventions.

- **`skill-node-script-conventions` (typescript-node-style-guide)** — TypeScript/Node style guide: Biome lint rule catalog, strict-mode flag breakdown, import ordering convention, naming conventions table, type annotation patterns, and coverage exemption conventions.
- **`skill-node-script-conventions` (shared-lib-rules)** — Five rules for shared library modules under `src/lib/shared/`: no CLI entry points, 100% coverage, consumer documentation in module-level JSDoc, domain-based naming, and extraction discipline.
- **`skill-node-script-conventions` (path-layout)** — Directory and file path conventions for Node scripts — `src/` layout, test layout, import conventions with `.ts` extensions, and module organization principles.
- **`skill-node-script-conventions` (tooling-config)** — Tooling configuration for `biome.json` (single quotes, semicolons asNeeded, indent 2, lineWidth 120), `tsconfig.json` (module: Preserve, types: [bun], strict flags), and `package.json` (bun deps, cleye, script entries).
- **`skill-node-script-conventions` (bun-test-conventions)** — Conventions for `bun:test` test files: globals, `Bun.spawnSync` CLI test pattern, fixture setup, parameterized tests, mocking patterns, and paired source-to-test file mapping.
- **`skill-node-script-conventions` (coverage-strategy)** — Coverage measurement via `bun --coverage`, source path boundaries, `fail_under = 100` threshold policy, 6-category edge case identification checklist, error path testing requirements, and c8 exemption conventions.
- **`skill-node-script-conventions` (test-examples)** — Complete runnable test examples covering CLI integration tests, file-based unit tests, module mocking, spy patterns, parameterized tests, and shared fixture helpers.
- **`skill-node-script-conventions` (reference-README)** — Index of all reference files in the conventions skill with one-sentence descriptions.

## Style Guide Coverage

Generated scripts must adhere to the shared conventions defined in `skill-node-script-conventions`. That skill covers naming conventions, path and project layout, tooling configuration (biome.json, tsconfig.json, package.json), testing conventions, and coverage strategy — load it for authoritative reference.

## Docs

See `./reference/README.md` for this skill's reference file index.
See `skill-node-script-conventions` (reference-README) for the shared conventions reference file index.
