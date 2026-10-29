# Set Flags

Every executable Bash script must begin with this shebang and flag declaration:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

- **`-e`** (errexit) — Exit when a command fails, subject to Bash's `errexit` exceptions.
  Commands tested by `if cmd; then ... fi` are safe because the condition checks the command's exit status.
  For intentionally ignored failures outside conditionals, use `|| true` or place the command before `&&` in an explicit chain. A failing final command in the chain is not suppressed.
- **`-u`** (nounset) — Error on undefined variable.
  Use default parameter expansion (`${var:-default}`) for all optional variables.
- **`-o pipefail`** — Pipeline fails if any stage fails.
  Use `cmd | head -n 10 || true` when head receives SIGPIPE from early termination.

Library files (sourced, not executed) must not set flags.
Library functions assume the caller has set appropriate flags.