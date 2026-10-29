# Reference Index

- **[set-flags.md](set-flags.md)** — Mandatory `set -euo pipefail` with caveats for each flag and library file rules.
- **[quoting-conventions.md](quoting-conventions.md)** — Google Shell Style Guide quoting rules: variable quoting, command substitution quoting, array usage, and `$()` over backticks.
- **[shellcheck-rules.md](shellcheck-rules.md)** — Adopted ShellCheck rule policies with severity (Error/Warning/Style) and rationale for each.
- **[error-handling.md](error-handling.md)** — Unified `die()`, `err()`, `info()` helpers, trap cleanup pattern, and named exit code constants.
- **[function-naming.md](function-naming.md)** — Use lowercase `snake_case` for script-level functions and `::`-namespaced library functions; declare constants uppercase with `readonly`; prefix private functions with `_`.
- **[exit-codes.md](exit-codes.md)** — Standard exit code convention: 0 success, 1 runtime error, 2 usage error, 3 environment error.
- **[json-output-conventions.md](json-output-conventions.md)** — stdout JSON contract and stderr diagnostic message conventions.
- **[cross-platform.md](cross-platform.md)** — Bash 3.2+ target, GNU/BSD command differences, and portable path resolution using `${BASH_SOURCE[0]}`.
