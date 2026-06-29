# Bash Script Conventions — Reference Index

- **`set-flags.md`** — Mandatory `set -euo pipefail` with caveats for each flag and library file rules.
- **`quoting-conventions.md`** — Google Shell Style Guide quoting rules: variable quoting, command substitution quoting, array usage, and `$()` over backticks.
- **`shellcheck-rules.md`** — Adopted ShellCheck rule policies with severity (Error/Warning/Style) and rationale for each.
- **`error-handling.md`** — Unified `die()`, `err()`, `info()` helpers, trap cleanup pattern, and named exit code constants.
- **`function-naming.md`** — snake_case script-level functions, `::` namespace-prefixed library functions, uppercase constants, and private underscore prefix.
- **`exit-codes.md`** — Standard exit code convention: 0 success, 1 runtime error, 2 usage error, 3 environment error.
- **`json-output-conventions.md`** — stdout JSON contract and stderr diagnostic message conventions.
- **`cross-platform.md`** — Bash 3.2+ target, GNU/BSD command differences, and portable path resolution using `${BASH_SOURCE[0]}`.