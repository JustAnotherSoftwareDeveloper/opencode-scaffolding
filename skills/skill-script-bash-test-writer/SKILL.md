---
name: skill-script-bash-test-writer
description: "Use when generating bats-core test files for existing bash scripts under scripts/shell/."
tags: [bash-testing, bats, test-generation, shell-testing, bats-core]
class: operation
---

# Skill Script Bash Test Writer

## Normalize Input

Map invocation context to one internal input object with these required fields:

- **Script name** — Kebab-case entry point name that must already exist under `scripts/shell/src/`.
- **Module structure** — The `src/lib/` package modules and functions to test.
- **CLI interface** — `getopts` argument definitions, options, and exit code conventions for integration tests.
- **Known edge cases** — Empty input, malformed input, boundary conditions, missing dependencies relevant to this script.

`BLOCKED: Source script <name> not found at scripts/shell/src/<name>.sh — run skill-script-bash-writer first.`
`BLOCKED: Lib module <name> not found under scripts/shell/src/lib/<name>/ — create it first.`
`BLOCKED: Shell scripts directory not found at scripts/shell/.`
`BLOCKED: bats-core not installed — install via apt (linux), brew (macOS), or npm (cross-platform).`

## Procedure

Each step is one imperative action.
Do not delegate sub-tasks.

1. **Parse input** — Read the source script at `src/<script-name>.sh` and lib modules under `src/lib/<script-name>/`.
   Extract function signatures, CLI argument parsing (getopts), exit code constants, and known edge cases.
   Identify shared lib dependencies (`source '../lib/shared/*'`) for path resolution.
   Read `scripts/shell/Makefile` for existing `.PHONY` targets and test conventions.

2. **Generate bats test file** — Write `tests/<script-name>.bats` with:
   `#!/usr/bin/env bats` shebang.
   `setup()` function loading `bats-support/load` and `bats-assert/load` from system-installed paths.
   `teardown()` function cleaning up temporary directories with `rm -rf`.
   One `@test` block per behavior:
   - **`--help` output test** — Invoke `run bash src/<script-name>.sh --help`; assert `assert_success` and `assert_output --partial 'Usage:'`.
   - **Success path test** — Invoke with valid arguments; assert `assert_success` and expected stdout/stderr content.
   - **Failure path test** — Invoke with missing or invalid arguments; assert `assert_failure` and `assert_stderr --partial 'Error:'`.
   - **Argument validation tests** — Test each option (`-h`, `-o`, `-v`) and required positional argument.
     Use `run bash src/<script-name>.sh ...args` pattern for CLI invocation tests.
     Use `mktemp -d` inside `setup()` for writable test fixtures; reference via `TEST_TEMP` variable.
     Use `BATS_TEST_DIRNAME` for fixture-relative paths to `../fixtures/<script-name>/`.
     Use `run` helper for all CLI invocations; capture exit code via `$status` and output via `$output`.
     For file-based scripts, use the mock PATH pattern from skill-bash-conventions (testing-conventions / Mock Patterns) to isolate external command dependencies.

3. **Register in Makefile** — Add entries to `scripts/shell/Makefile`:
   Skip `run-<script-name>` target and help text — already registered by skill-script-bash-writer step 4.
   Add a `.PHONY` target `test-<script-name>` that runs `"$(BATS)" tests/<script-name>.bats`.
   Add help text line for `test-<script-name>` to the `help` target.
   Add `test-<script-name>` to the `.PHONY` list if not already present.
   Target added after `deps-check` and before `clean` (alphabetical by script name).

4. **Run validation** — Execute the full validation suite:
   `make -C scripts/shell lint` — shellcheck must pass on all files.
   `make -C scripts/shell format-check` — shfmt formatting check must pass.
   `make -C scripts/shell test` — bats must run all tests (including the new file) and exit zero.
   `bash src/<script-name>.sh --help` — entry point works and prints usage.

   On test failure, retry once with expanded edge-case tests for the failing scenario.
   On second failure, return `PARTIAL` with failing test names and coverage gaps.

## Self-Validation

Each check is a yes/no assertion.

- All generated tests pass (`bats tests/<script-name>.bats` exits zero).
- No `.skip` modifier exists on any `@test` in the generated file.
- Lint passes (`make -C scripts/shell lint` exits zero).
- Format check passes (`make -C scripts/shell format-check` exits zero).
- Makefile `.PHONY` target and help text are present for the new script.

## Expected Output

Test file under `scripts/shell/tests/`:

- `tests/<script-name>.bats` — bats-core test file covering `--help`, success path, failure path, and argument validation, using `bats-support` and `bats-assert` loaded in `setup()`.

`scripts/shell/Makefile` updated with `.PHONY` target and help text for the new script.

All tests pass, no skipped tests, lint is clean, and format check passes.

## Shared Conventions

This skill consumes shared reference documentation from `skill-bash-conventions` and `skill-script-bash-writer`. All generated test files must conform to these conventions.

- **`skill-bash-conventions` (exit-codes)** — Standard exit code convention: 0 success, 1 runtime error, 2 usage error, 3 environment error.
- **`skill-bash-conventions` (json-output-conventions)** — stdout JSON contract and stderr diagnostic message conventions for test assertions.
- **`skill-bash-conventions` (shellcheck-rules)** — Adopted ShellCheck rule policies that lint enforces.
- **`skill-script-bash-writer` (testing-conventions)** — bats-core setup/teardown conventions, assertion library installation and loading, PATH-based mock patterns, fixture management under `fixtures/<script-name>/`, test coverage expectations, and the local validation workflow.
- **`skill-script-bash-writer` (cli-conventions)** — CLI entry point structure, getopts argument parsing, and exit code conventions to test against.

## Docs

This skill has no standalone reference directory.
See the following shared convention skills for reference documentation:

### Bash Conventions

The `skill-bash-conventions` skill holds shared reference documentation for all bash script conventions including set-flags, quoting-conventions, shellcheck-rules, error-handling, function-naming, exit-codes, json-output-conventions, and cross-platform patterns. Load it via the skill tool for authoritative guidance on testing-relevant conventions (exit-codes, json-output-conventions, shellcheck-rules).

### Script Structure (Bash Writer)

See `skill-script-bash-writer` (reference/path-layout.md, reference/testing-conventions.md) for the directory layout, script structure, and the testing conventions the writer generates tests for.
