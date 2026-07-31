---
name: skill-script-bash-writer
description: "Use when generating deterministic bash scripts from skill requirements, including CLI entry points, library modules, test files, and Makefile registration."
schema_version: "1.0"
cues:
  - {facet: operation, value: "generate-bash-script", primary: true}
  - {facet: subject, value: "Bash scripts"}
  - {facet: interface, value: "CLI entry point"}
  - {facet: outcome, value: "tested shell implementation"}
relationships:
  - {role: owner, rationale: "owns deterministic Bash script generation"}
class: operation
---

# Skill Script Bash Writer

## Normalize Input

Map invocation context to one internal input object.
Define these required fields:

- **Script name** — kebab-case entry point name (e.g., `count-tokens`, `validate-json`). Corresponding file: `src/<script-name>.sh`.
- **Purpose** — What the script computes, processes, or orchestrates.
- **Input contract** — CLI arguments, stdin format, or file paths the script reads.
- **Output contract** — stdout format (JSON preferred), exit codes, stderr behavior.
- **Dependencies** — External CLI tools required (e.g., `jq`, `git`, `curl`). Not shellcheck/shfmt/bats (those are infrastructure).
- **Skill consumers** — Which skills will invoke this script.
- **Makefile target name** — kebab-case target in the Makefile (defaults to script name).

`BLOCKED: Missing script name — provide a kebab-case entry point name.`
`BLOCKED: Missing purpose — describe what the script computes or processes.`
`BLOCKED: Missing input contract — define CLI arguments, stdin format, or file paths.`
`BLOCKED: Missing output contract — define stdout format, exit codes, and stderr behavior.`

## Procedure

Each step is one imperative action.
Do not delegate sub-tasks.

1. **Parse requirements** — Extract script name, purpose, input/output contracts, dependencies, and skill consumers from the normalized input.
   Validate script name is kebab-case.
   Validate dependencies are external CLI tools (not shellcheck/shfmt/bats — those are infrastructure, not per-script deps).

2. **Generate CLI entry point** — Write `src/<script-name>.sh` with `#!/usr/bin/env bash` and `set -euo pipefail`, `SCRIPT_DIR` resolution via `${BASH_SOURCE[0]}`, sourcing `../lib/shared/common.sh` for `die()`, `err()`, `info()`, `require()`, `parse_args()` function with getopts, `usage()` function with full help text, `main()` function as the entry point, JSON stdout format, `Error:` prefix on stderr, standard exit codes (0, 1, 2, 3), and `main "$@"` at the bottom.
   Follow conventions in `skill-bash-conventions` (cli-conventions, exit-codes, json-output-conventions, error-handling).
   See `templates/cli-template.sh` for the canonical structure.

3. **Generate lib modules** — Write `src/lib/<script-name>/core.sh` with sourced functions, bash-specific features (`[[ ]]`, arrays), argument validation with `${1:?error_msg}`, stdout output and stderr errors, and no side-effect execution at load time.
   Follow conventions in `./reference/path-layout.md` and `skill-bash-conventions` (set-flags, quoting-conventions, shellcheck-rules, function-naming, cross-platform).

4. **Register in Makefile** — Add a `.PHONY` target `run-<script-name>` that invokes `"$(SCRIPT_DIR)src/<script-name>.sh" [args]`. Add help text line to the `help` target. Target added after `deps-check` and before `clean` (alphabetical order).

5. **Generate test file** — Write `tests/<script-name>.bats` with `setup()` loading bats-assert and bats-support, `teardown()` cleanup, tests for `--help` output, success path, failure path, and argument validation. Use `run bash ...` pattern for CLI invocation tests and temp directories for file-based tests.
   Follow conventions in `./reference/testing-conventions.md`.

6. **Run validation** — Execute `make -C scripts/shell lint` (shellcheck), `make -C scripts/shell format-check` (shfmt), `make -C scripts/shell test` (bats), and `bash src/<script-name>.sh --help` (entry point works).
   Report `BLOCKED: <step> failed — <details>` on any failure.

## Self-Validation

Each check is a yes/no assertion.

- Lint passes — `make -C scripts/shell lint` exits zero.
- Format check passes — `make -C scripts/shell format-check` exits zero.
- Tests pass — `make -C scripts/shell test` exits zero, with all tests passing.
- Coverage passes — `make -C scripts/shell coverage` exits zero with >=100% coverage (bashcov, `fail_under=100`).
- Entry point `--help` works — `bash src/<script-name>.sh --help` exits zero and prints usage.
- Entry point errors on missing required arg — `bash src/<script-name>.sh` exits 2 with error on stderr.

## Expected Output

One or more files under `scripts/shell/`:

- `src/<script-name>.sh` — CLI entry point with getopts, JSON output, error handling, and help text.
- `src/lib/<script-name>/core.sh` — Core logic module with sourced functions.
- `tests/<script-name>.bats` — bats-core test file with coverage of success, failure, and edge cases.

`Makefile` updated with `.PHONY` target and help text.

## Shared Conventions

This skill consumes shared reference documentation from the `skill-bash-conventions` skill. All generated scripts must conform to these conventions.

- **`skill-bash-conventions` (set-flags)** — Mandatory `set -euo pipefail` with caveats for each flag and library file rules.
- **`skill-bash-conventions` (quoting-conventions)** — Google Shell Style Guide quoting rules: variable quoting, command substitution quoting, array usage, and `$()` over backticks.
- **`skill-bash-conventions` (shellcheck-rules)** — Adopted ShellCheck rule policies with severity (Error/Warning/Style) and rationale for each.
- **`skill-bash-conventions` (error-handling)** — Unified `die()`, `err()`, `info()` helpers, trap cleanup pattern, and named exit code constants.
- **`skill-bash-conventions` (function-naming)** — snake_case script-level functions, `::` namespace-prefixed library functions, uppercase constants, and private underscore prefix.
- **`skill-bash-conventions` (exit-codes)** — Standard exit code convention: 0 success, 1 runtime error, 2 usage error, 3 environment error.
- **`skill-bash-conventions` (json-output-conventions)** — stdout JSON contract and stderr diagnostic message conventions.
- **`skill-bash-conventions` (cross-platform)** — Bash 3.2+ target, GNU/BSD command differences, and portable path resolution using `${BASH_SOURCE[0]}`.

## Docs

See `./reference/` for this skill's reference files:

- `path-layout.md` — Directory layout, resolution order, lib/shared sourcing rules.
- `testing-conventions.md` — bats-core setup, assertion libraries, mock patterns, fixtures.

See `skill-bash-conventions` (reference-README) for the shared conventions reference file index.
