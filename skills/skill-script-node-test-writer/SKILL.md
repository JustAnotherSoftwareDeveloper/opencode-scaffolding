---
name: skill-script-node-test-writer
description: "Use when generating bun test files for Node scripts under scripts/node/, covering CLI integration tests via Bun.spawnSync and unit tests for lib modules."
class: operation
---

# Skill Script Node Test Writer

## Normalize Input

Map invocation context to one internal input object with these required fields:

- **Script name** — Kebab-case entry point name that must already exist under `scripts/node/`.
- **Module structure** — The `src/lib/` package modules and functions to test.
- **CLI interface** — Cleye command definition, arguments, and options for integration tests.
- **Known edge cases** — Empty input, malformed input, boundary conditions relevant to this script.

`BLOCKED: Source script <name> not found — run skill-script-node-writer first.`
`BLOCKED: Shared module <name> not found — create it under src/lib/shared/ first.`
`BLOCKED: Scripts directory not found at scripts/node/.`

## Procedure

Each step is one imperative action.
Do not delegate sub-tasks.

1. **Parse input** — Read the source script files under `src/cli/<name>.ts` and `src/lib/<name>/`.
   Extract module structure, public functions, CLI cleye decorators, and known edge cases.
   Identify shared lib dependencies (`from 'lib/shared/*'`) for separate test generation.
   Read `src/lib/shared/exit-codes.ts` for expected exit code constants.

2. **Generate unit test file** — Write `tests/<script-name>.test.ts` with:
   Imports using `bun:test` globals (`describe`, `expect`, `it`, `beforeAll`, `afterAll`).
   Direct imports from `src/lib/<script-name>/<module>` (no barrel files).
   One `describe` block per module with `it` cases covering nominal and edge-case inputs.
   `mkdtempSync` from `node:fs` for temporary fixture directories.
   `beforeAll` / `afterAll` for fixture setup and teardown using `rmSync` with `recursive: true`.
   Coverage for error paths and exception handling.
   Assertions using `expect().toBe()`, `expect().toEqual()`, `expect().toThrow()`.

3. **Generate CLI integration test file** — Write `tests/<script-name>.cli.test.ts` with:
   `Bun.spawnSync` based tests covering all CLI arguments and options.
   Pattern: `const result = Bun.spawnSync(['bun', 'src/cli/<script-name>.ts', ...args])`.
   Assertions on `result.exitCode` and `result.stdout.toString()` / `result.stderr.toString()`.
   `mkdtempSync` for temporary fixture files used as CLI arguments.
   Parameterized error-path tests for non-zero exit conditions using `describe.each` or `it.each`.
   Reference `./reference/cli-conventions.md` from `skill-script-node-writer` for expected CLI behavior.

4. **Update package.json** — Add test script entries under `"scripts"`:
   `"test:<script-name>" = "bun test tests/<script-name>.test.ts"`.
   `"test:<script-name>:cli" = "bun test tests/<script-name>.cli.test.ts"`.
   `"test" = "... && bun test tests/<script-name>.test.ts tests/<script-name>.cli.test.ts"` (appended to existing chain).

5. **Validate and report** — Run tests and type check.
   `bun test tests/<script-name>.test.ts tests/<script-name>.cli.test.ts`
   `bun run --cwd scripts/node tsc --noEmit`
   On test failure, retry once with expanded edge-case tests.
   On second failure, return `PARTIAL` with failing test names and coverage gaps.

## Self-Validation

Each check is a yes/no assertion.

- All generated tests pass (`bun test --tb=short`).
- No `.skip` or `.todo` modifiers exist on any `it` or `describe` in generated files.
- Type check passes (`bunx tsc --noEmit` on test files).

## Expected Output

Test files under `scripts/node/tests/`:

- `tests/<script-name>.test.ts` — Unit tests for `src/lib/<script-name>/` modules using `bun:test` globals.
- `tests/<script-name>.cli.test.ts` — CLI integration tests for `src/cli/<script-name>.ts` using `Bun.spawnSync`.

`package.json` test scripts updated under `"scripts"`.
All tests pass, no skipped tests, and type check is clean.

## Docs

This skill has no standalone reference directory.
See the following shared convention skills for reference documentation:

### Shared Node Script Conventions

The `skill-node-script-conventions` skill (`../skill-node-script-conventions/`) holds shared reference documentation consumed by all Node/TypeScript script skills. Load it via the skill tool and reference its files by relative path.

#### Testing Conventions

File: `../skill-node-script-conventions/reference/bun-test-conventions.md`

The test writer aligns with these shared test conventions:

- **Test file naming** — `tests/<script-name>.test.ts` for unit tests, `tests/<script-name>.cli.test.ts` for CLI integration tests, `tests/<shared-module>.test.ts` for shared lib tests. See `bun-test-conventions.md` > Naming Conventions.
- **bun:test globals** — All test files import `describe`, `expect`, `test`/`it`, `beforeAll`, `afterAll`, `mock`, and `spyOn` from `bun:test`. See `bun-test-conventions.md` > bun:test Globals.
- **CLI integration via Bun.spawnSync** — CLI tests use `Bun.spawnSync(['bun', 'src/cli/<script-name>.ts', ...args])` with assertions on `result.exitCode`, `result.stdout.toString()`, and `result.stderr.toString()`. See `bun-test-conventions.md` > CLI Integration Tests with Bun.spawnSync.
- **Fixture setup** — Use `mkdtempSync` + `beforeAll` for temporary directories and `rmSync` + `afterAll` for cleanup. See `bun-test-conventions.md` > Fixture Setup Pattern.
- **Parameterized tests** — Use `test.each` for input variations and `describe.each` for error-path tests. See `bun-test-conventions.md` > Parameterized Tests.
- **Test isolation** — No module-level mutable state; mock restoration via `afterEach` with `mock.restore()` and `mock.clearAllMocks()`. See `bun-test-conventions.md` > Test Isolation Conventions.
- **Paired file mapping** — Source-to-test file mapping table in `bun-test-conventions.md` > Paired Source-to-Test File Mapping.
- **Mocking** — `mock.module()` for module-level mocks, `spyOn()` for method tracking. See `bun-test-conventions.md` > Mocking Patterns.
- **Assertions** — `expect().toBe()`, `expect().toEqual()`, `expect().toContain()`, `expect().toThrow()`, `expect().toHaveBeenCalledTimes()`. See `bun-test-conventions.md` > Assertion Best Practices.
- **Complete examples** — Runnable test examples covering all patterns are in `../skill-node-script-conventions/reference/test-examples.md`.

#### Coverage Threshold Policy

File: `../skill-node-script-conventions/reference/coverage-strategy.md`

The test writer aligns with the shared coverage strategy:

- **Tool** — Coverage is measured via `bun test --coverage` using c8 (Bun's integrated coverage engine). See `coverage-strategy.md` > Measurement Tool.
- **Source coverage boundaries** — Coverage is measured against `src/cli/*.ts`, `src/lib/<script-name>/*.ts`, and `src/lib/shared/*.ts`. The `tests/` and `node_modules/` directories are excluded. See `coverage-strategy.md` > Source Coverage Boundaries.
- **Threshold** — `fail_under = 100` (100% line coverage required). On failure, retry once with expanded edge-case tests. On second failure, return `PARTIAL` with failing test names and specific coverage gaps. See `coverage-strategy.md` > Threshold Policy.
- **Edge case identification** — Test suites must cover all 6 edge case categories: Input, File I/O, CLI Arguments, Error Handling, Output, and Boundary Values. See `coverage-strategy.md` > Edge Case Identification Checklist.
- **Error path testing** — Every non-zero `process.exit(code)` path must have a corresponding `Bun.spawnSync` test using `describe.each` or `test.each`. See `coverage-strategy.md` > Error Path Testing.
- **Coverage exemptions** — Use `/* c8 ignore */` sparingly and only for unreachable defensive code, type narrowing fallthroughs, and `@ts-expect-error` suppression. See `coverage-strategy.md` > Coverage Exemption Conventions.

#### Additional Convention Files

| File | Description |
|------|-------------|
| `../skill-node-script-conventions/reference/path-layout.md` | Directory structure, import conventions, and module organization for `scripts/node/` |
| `../skill-node-script-conventions/reference/tooling-config.md` | `biome.json`, `tsconfig.json`, and `package.json` configuration conventions |
| `../skill-node-script-conventions/reference/shared-lib-rules.md` | Five rules for `src/lib/shared/` modules including 100% coverage requirement |
| `../skill-node-script-conventions/reference/typescript-node-style-guide.md` | TypeScript coding style, import ordering, naming conventions, type annotation patterns |

### CLI Conventions (Script Writer)

See `../skill-script-node-writer/reference/cli-conventions.md` for expected CLI behavior (cleye decorators, argument parsing, exit codes) to test against.