# Set Flags

Every executable bash script must begin with:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

- **`-e`** (errexit) — Exit on command failure.
  Conditionals with `if cmd; then ... fi` are safe because the exit code is checked explicitly.
  Use `|| true` or explicit `&&` chaining to suppress failures in non-conditionals.
- **`-u`** (nounset) — Error on undefined variable.
  Use default parameter expansion (`${var:-default}`) for all optional variables.
- **`-o pipefail`** — Pipeline fails if any stage fails.
  Use `cmd | head -n 10 || true` when head receives SIGPIPE from early termination.

Library files (sourced, not executed) must not set flags.
Library functions assume the caller has set appropriate flags.