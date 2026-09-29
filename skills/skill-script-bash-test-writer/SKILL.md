---
name: skill-script-bash-test-writer
description: "Use when generating bats-core test files for existing Bash scripts under scripts/shell/."
selection:
  role: owner
  tags:
    actions: [write Bash tests]
    inputs: [existing Bash script]
    outputs: [bats-core test suite]
    topics: [script testing]
    environments: [bats-core]
  use_when: [an existing shell script needs bats-core tests]
  not_for: [creating the Bash implementation]
class: operation
---

# Build Bash Test Suites

## Normalize Input

Map invocation context to one internal input object with these required fields:

- **Script name** — Kebab-case name supplied in the invocation context.
  Verify it against an existing entry point under `scripts/shell/src/`. In every
  `<name>` and `<script-name>` pattern below, substitute that exact value before
  using the path, command, message, or Makefile target.
- **Module structure** — The `lib/` modules and functions to test.
- **CLI interface** — `getopts` argument definitions, options, and exit code
  conventions for integration tests.
- **Known edge cases** — Empty input, malformed input, boundary conditions,
  and missing dependencies relevant to this script.

`BLOCKED: Source script <name> not found at
scripts/shell/src/<name>.sh — run skill-script-bash-writer first.`
`BLOCKED: Lib module <name> not found under
scripts/shell/lib/<name>/ — create it first.`
`BLOCKED: Shell scripts directory not found at scripts/shell/.`
`BLOCKED: bats-core not installed — install via apt (linux), brew (macOS),
or npm (cross-platform).`

## Procedure

Keep each numbered step focused on one outcome; treat subordinate
requirements as part of that action.
Do not delegate sub-tasks.

Resolve `src/`, `tests/`, and `fixtures/` paths relative to `scripts/shell/`.
`make -C scripts/shell test` runs Bats from that directory. From the repository
root, run Makefile checks with `make -C scripts/shell ...`; run the standalone
help check from `scripts/shell/`.

1. **Parse input** — Read the source script at `src/<script-name>.sh` and lib
   modules under `lib/<script-name>/`.
   Extract function signatures, CLI argument parsing (`getopts`), exit code
   constants, and known edge cases.
   Identify shared lib dependencies sourced through `${SCRIPT_DIR}/../lib/shared/`.
   Read `scripts/shell/Makefile` for existing `.PHONY` targets and test conventions.

2. **Generate bats test file** — Write `tests/<script-name>.bats` with:
   `#!/usr/bin/env bats` shebang.
   `setup()` function loading `bats-support/load` and `bats-assert/load` from
   system-installed paths.
   `teardown()` function cleaning up temporary directories with `rm -rf`.
   One `@test` block per behavior:
    - **`--help` output test** — Invoke
      `run --separate-stderr bash src/<script-name>.sh --help`. Assert `$status`
      is exactly `2` and check `[[ "$stderr" == *'Usage:'* ]]` without `Error:`.
    - **Success path test** — Invoke with valid arguments; assert `assert_success`
      and expected stdout/stderr content.
    - **Failure path test** — Invoke with missing or invalid arguments using
      `run --separate-stderr`; assert `assert_failure 2` for usage errors and
      check `[[ "$stderr" == *'Error:'* ]]`.
    - **Argument validation tests** — Test each option (`-h`, `-o`, `-v`) and
      the required positional argument.
      Use `run bash src/<script-name>.sh ...args` for CLI invocation tests.
      Create writable test fixtures with `mktemp -d` inside `setup()`.
      Reference those fixtures through the `TEST_TEMP` variable.
      Use `BATS_TEST_DIRNAME` for fixture-relative paths to
      `../fixtures/<script-name>/`.
      Use the Bats `run` helper for all CLI invocations. Capture exit codes via
      `$status`, stdout via `$output`, and stderr via `$stderr` when using
      `--separate-stderr` (Bats 1.10+).
      For file-based scripts, isolate external commands with executable mocks
      in a temporary directory prepended to `PATH`.

3. **Register in Makefile** — Add entries to
   `scripts/shell/Makefile`:
   Skip the `run-<script-name>` target and help text; skill-script-bash-writer
   step 4 already registers them.
   Add a `.PHONY` target `test-<script-name>` that runs
   `"$(BATS)" tests/<script-name>.bats`.
   Add help text line for `test-<script-name>` to the `help` target.
   Add `test-<script-name>` to the `.PHONY` list if it is not already present.
   Place the target after `deps-check` and before `clean`, alphabetically by
   script name.

4. **Run validation** — From the repository root, run
   `make -C scripts/shell check`. This runs lint, format-check, all Bats tests
   (including the new file), and the 100% bashcov coverage gate.
   From `scripts/shell/`, run `bash src/<script-name>.sh --help` and verify
   status 2, usage on stderr, and no `Error:` diagnostic.

   On test failure, retry once with expanded edge-case tests for the failing scenario.
   On second failure, return `PARTIAL` with failing test names and coverage gaps.

## Self-Validation

Each check is a yes/no assertion.

- All generated tests pass (`bats tests/<script-name>.bats` exits zero).
- No `.skip` modifier exists on any `@test` in the generated file.
- Lint passes (`make -C scripts/shell lint` exits zero).
- Format check passes (`make -C scripts/shell format-check` exits zero).
- Coverage passes (`make -C scripts/shell coverage` meets the 100% gate).
- Makefile `.PHONY` target and help text are present for the new script.

## Expected Output

Test file under `scripts/shell/tests/`:

- `tests/<script-name>.bats` — bats-core test file covering `--help`, success
  path, failure path, and argument validation. Load `bats-support` and
  `bats-assert` in `setup()`.

Update `scripts/shell/Makefile` with the `.PHONY` target and help text for the
new script.

All tests pass, no skipped tests, lint and format checks pass, and the coverage
gate passes.

## Shared Conventions

Load the `skill-bash-conventions` documentation skill through the skill tool
for shared Bash guidance.
Its references remain within that skill.
Do not load `skill-script-bash-writer` as a second operation owner; inspect the existing
script and any writer conventions already supplied as read-only task context.
All generated tests must conform to the applicable conventions.

- **Exit codes (`skill-bash-conventions`)** — Standard
  exit codes: 0 success, 1 runtime error, 2 usage error, and 3 environment error.
- **JSON output (`skill-bash-conventions`)** — stdout
  JSON contract and stderr diagnostic conventions for test assertions.
- **ShellCheck (`skill-bash-conventions`)** — Adopted
  ShellCheck rule policies enforced by lint.
- **Testing conventions (supplied writer context)** — bats-core setup/teardown,
  assertion libraries, PATH-based mocks, fixtures under
  `fixtures/<script-name>/`, coverage, and validation.
- **CLI conventions (inspected source)** — `getopts` parsing, CLI behavior,
  and exit codes to test.

## Docs

This skill has no local references.
Load the documentation skill named below when its shared guidance is relevant.
Do not use a relative Markdown link into another skill's directory.

### Bash Conventions

- Load `skill-bash-conventions` and consult its **Exit codes**, **JSON output
  conventions**, and **ShellCheck rules** references.

### Script Structure (Bash Writer)

The `skill-script-bash-writer` operation owns the generated script's structure.
Use its conventions only when the task already supplies them as read-only
context; do not load a second operation owner.
