---
name: skill-script-node-test-writer
description: "Use when generating Bun test files for existing Node scripts under scripts/node/, including CLI and library tests."
selection:
  role: owner
  tags:
    actions: [write Node tests]
    inputs: [existing Node script]
    outputs: [Bun test suite]
    topics: [script testing]
    environments: [Bun test]
  use_when: [an existing Node script needs Bun tests]
  not_for: [creating the Node implementation]
class: operation
---

# Skill Script Node Test Writer

## Normalize Input

Map invocation context to one internal input object with these required fields:

- **Script name** — Kebab-case entry point name that must already exist under `scripts/node/`.
- **Module structure** — The `src/lib/` package modules and functions to test.
- **CLI interface** — Cleye command definition, arguments, and options for integration tests.
- **Known edge cases** — Empty input, malformed input, boundary conditions relevant to this script.

For the blocked-message formats below, substitute the **Script name** input value for the first `<name>` and the concrete shared-module name from **Module structure** for the second `<name>`; never emit `<name>` literally.

`BLOCKED: Source script <name> not found under scripts/node/.`
`BLOCKED: Shared module <name> not found under src/lib/shared/.`
`BLOCKED: Scripts directory not found at scripts/node/.`

## Procedure

Use numbered steps for ordered stages and nested bullets for independent requirements.
Do not delegate sub-tasks.

1. **Parse input** — Read the source script files under `src/cli/<name>.ts` and `src/lib/<name>/`.
   Extract module structure, public functions, CLI cleye decorators, and known edge cases.
   Identify shared lib dependencies (`from 'lib/shared/*'`) for separate test generation.
   Read `src/lib/shared/exit-codes.ts` for expected exit code constants.

2. **Generate unit test file** — Write `tests/<script-name>.test.ts` for the inspected
   `src/lib/<script-name>/` modules. Keep one `describe` block per module and use
   `toBe`, `toEqual`, and `toThrow` as appropriate to its behavior. Assert observed
   behavior, including applicable nominal, edge, error, and exception cases; do not
   infer behavior from convention examples. Follow these loaded documentation references
   for reusable test mechanics:
   - `skill-node-script-conventions -> reference/bun-test-conventions.md`
   - `skill-node-script-conventions -> reference/path-layout.md`
   - `skill-node-script-conventions -> reference/coverage-strategy.md`
   - `skill-node-script-conventions -> reference/test-examples.md`

3. **Generate CLI integration test file** — Write `tests/<script-name>.cli.test.ts`
   to exercise each applicable argument and option in the inspected CLI definition
   and its observed output and exit behavior. Use source-derived expectations;
   shared conventions and examples do not override the source. Follow the same four
   shared references for reusable CLI testing mechanics. CLI conventions supplied
   as read-only task context may inform the work; do not load a second operation owner.

4. **Update package.json** — Add test script entries under `"scripts"`:
   - Register `test:<script-name>` and `test:<script-name>:cli` using the commands in
     `skill-node-script-conventions -> reference/tooling-config.md#configure-packagejson`.
   - Append `&& bun test tests/<script-name>.test.ts tests/<script-name>.cli.test.ts` to the existing `"test"` command, preserving its existing chain.

5. **Validate and report** — Run tests and type check.
   `bun test tests/<script-name>.test.ts tests/<script-name>.cli.test.ts`
   `bun run --cwd scripts/node tsc --noEmit`
   On test failure, retry once with expanded edge-case tests.
   On second failure, return `PARTIAL` with failing test names and coverage gaps.

## Self-Validation

Each check is a yes/no assertion.

- All generated tests pass (`bun test --tb=short`).
- No `.skip` or `.todo` modifiers exist in generated files; see
  `skill-node-script-conventions -> reference/bun-test-conventions.md#test-structure`.
- Type check passes (`bunx tsc --noEmit` on test files).

## Expected Output

Test files under `scripts/node/tests/`:

- `tests/<script-name>.test.ts` — Unit tests for `src/lib/<script-name>/` modules using `bun:test` globals.
- `tests/<script-name>.cli.test.ts` — CLI integration tests for `src/cli/<script-name>.ts` using `Bun.spawnSync`.

`package.json` test scripts updated under `"scripts"`.
All tests pass, no skipped tests, and type check is clean.

## Docs

This skill has no standalone reference directory. Load `skill-node-script-conventions`
as passive documentation, not an execution dependency. Consult its exact `reference/`
files named here; do not load a second operation owner.

### Shared Node Script Conventions

Apply `skill-node-script-conventions -> reference/typescript-node-style-guide.md`
to generated test code. `skill-node-script-conventions -> reference/shared-lib-rules.md`
applies when the inspected source includes `src/lib/shared/` modules. These references
do not define the implementation baseline, task scope, outputs, retries, or operation
ownership.

### CLI Conventions (Script Writer)

The `cli-conventions` reference belongs to `skill-script-node-writer`, a separate operation. Consult it only when supplied as read-only task context; do not load that operation as a second owner. Otherwise, inspect the source CLI for cleye decorators, argument parsing, and exit codes.
