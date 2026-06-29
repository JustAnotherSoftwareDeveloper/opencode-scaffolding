# ShellCheck Rules

The `lint` target runs shellcheck on all `.sh` files.
Adopt these rule policies:

- **SC2155** (declare and local mask return values) — Policy: Error.
  Declare separately from assignment to prevent masking local exit codes.
- **SC2086** (double quote to prevent globbing) — Policy: Error.
  Enforce quoting for all variable expansions.
- **SC2206** (quote to prevent word splitting) — Policy: Error.
  Enforce arrays over string splitting.
- **SC2207** (prefer mapfile or read -a) — Policy: Error.
  Enforce safe array building to prevent glob expansion.
- **SC1090/SC1091** (can't follow sourced file) — Policy: Warning.
  Use `# shellcheck source=...` directives to document source relationships.
- **SC2034** (unused variable) — Policy: Warning.
  Use `# shellcheck disable=SC2034` with an inline reason comment.
- **SC2181** (check exit code directly) — Policy: Error.
  Prefer `if cmd; then` over `if [ $? -eq 0 ]; then`.
- **SC2312** (consider invoking pgrep/ps instead of piping to head) — Policy: Style.
  Prefer `|| true` or explicit handling.

ShellCheck directive placement:

```bash
# shellcheck source=../lib/shared/common.sh
source "${SCRIPT_DIR}/../lib/shared/common.sh"

# shellcheck disable=SC2034 # Used by consumer after sourcing
readonly SCRIPT_VERSION="1.0.0"
```