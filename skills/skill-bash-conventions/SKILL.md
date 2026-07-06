---
name: skill-bash-conventions
description: "Use when referencing shared bash script conventions for the OpenCode platform, covering set flags, quoting, shellcheck rules, error handling, function naming, exit codes, JSON output format, and cross-platform portability."
tags: [skill-authoring, reference, bash, shell, shellcheck, error-handling, portability]
class: documentation
---

# Bash Script Conventions — Documentation Store

This skill is a passive data store for shared bash script convention documentation on the OpenCode platform.
It does not auto-read any files when loaded.
Downstream operation-class skills (skill-script-bash-writer, skill-script-bash-test-writer) load this skill via the skill tool and reference its files by relative path.

## Reference Files

Read the documentation files listed below as needed for your current task.
The bulleted list provides the mapping of files to their purpose.

- **`reference/set-flags.md`** — Mandatory `set -euo pipefail` with caveats for each flag and library file rules.
- **`reference/quoting-conventions.md`** — Google Shell Style Guide quoting rules: variable quoting, command substitution quoting, array usage, and `$()` over backticks.
- **`reference/shellcheck-rules.md`** — Adopted ShellCheck rule policies with severity (Error/Warning/Style) and rationale for each.
- **`reference/error-handling.md`** — Unified `die()`, `err()`, `info()` helpers, trap cleanup pattern, and named exit code constants.
- **`reference/function-naming.md`** — snake_case script-level functions, `::` namespace-prefixed library functions, uppercase constants, and private underscore prefix.
- **`reference/exit-codes.md`** — Standard exit code convention: 0 success, 1 runtime error, 2 usage error, 3 environment error.
- **`reference/json-output-conventions.md`** — stdout JSON contract and stderr diagnostic message conventions.
- **`reference/cross-platform.md`** — Bash 3.2+ target, GNU/BSD command differences, and portable path resolution using `${BASH_SOURCE[0]}`.

Choose the relevant files based on what you need to reference.
Read only those files.
Do not read every file — read as needed.

## Contents

- `reference/` — Shared bash script convention documentation organized by domain.

## Conventions Summary

The bash conventions cover eight domains: script-level set flags (`set -euo pipefail`) for strict error handling, Google Shell Style Guide quoting rules to prevent word splitting and globbing, a curated ShellCheck rule policy table (SC2155, SC2086, SC2206, SC2207, SC1090/1091, SC2034, SC2181, SC2312), unified error handling via `die()`/`err()`/`info()` helpers with EXIT trap cleanup, snake_case and `::` namespace function naming, standardized exit codes (0–3), JSON stdout/stderr output contract, and cross-platform patterns targeting bash 3.2+ with GNU/BSD portability workarounds.

## Docs

See `reference/README.md` for the full index of reference files.
Base directory for this skill: `file:///home/michael/.config/opencode/skills/skill-bash-conventions`
