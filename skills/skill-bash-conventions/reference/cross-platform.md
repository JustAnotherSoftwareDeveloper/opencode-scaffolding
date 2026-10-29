# Cross-Platform Patterns

## Bash version compatibility

For compatibility with macOS's system Bash, target Bash 3.2 or later. Avoid features unavailable in Bash 3.2:

- `**` globstar
- `declare -A` associative arrays
- `[[ -v var]]` variable existence check
- `$EPOCHSECONDS`

Scripts that require Bash 4+ features must declare `# Requires: bash >= 4.0` and fall back gracefully.

## GNU/BSD command differences

- **`sed -i`** — Use `sed -i.bak 's/foo/bar/' file` for a portable two-step that works on both GNU and BSD.
  Remove the `.bak` backup afterward.
- **`date`** — Detect via `date --version 2>/dev/null || true`, then branch:
  - GNU: `date -d 'yesterday'` for relative dates.
  - BSD: `date -v-1d` for relative arithmetic.
- **`find -exec`** — Use `-exec ... +` (POSIX, works on both).
  For null-delimited output, use `find ... -exec cmd {} +` directly instead of `-print0 | xargs`.
- **`stat`** — Detect and branch.
  GNU: `stat -c '%Y' file`.
  BSD: `stat -f '%m' file`.
  For timestamp display, prefer `date -r "$file"` on BSD or `date -d "@$(stat -c '%Y' file)"` on GNU.
- **`readlink -f`** — Linux-only.
  Use the portable `${BASH_SOURCE[0]}`-based pattern instead.

## Path resolution

For script-relative paths, use `${BASH_SOURCE[0]}`. Avoid `readlink -f` (Linux-only).

Portable pattern:

```bash
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
```
