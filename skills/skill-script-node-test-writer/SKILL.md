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

The `skill-node-script-conventions` skill holds shared reference documentation for all Node/TypeScript testing conventions. Load it via the skill tool for authoritative guidance on bun-test-conventions, coverage-strategy, path-layout, tooling-config, shared-lib-rules, and typescript-node-style-guide. Procedure steps above reference specific topics within that skill.

### CLI Conventions (Script Writer)

See `skill-script-node-writer` (cli-conventions) for expected CLI behavior (cleye decorators, argument parsing, exit codes) to test against.
