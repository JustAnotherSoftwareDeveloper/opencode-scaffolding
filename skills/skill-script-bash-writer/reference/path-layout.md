# Path Layout

Follow conventions in `skill-bash-conventions` (set-flags, quoting-conventions, shellcheck-rules, error-handling, function-naming, cross-platform) for set flags, quoting, shellcheck directives, error handling, function naming, and portability.

## Directory Layout

Every bash script project under `scripts/shell/` follows this structure:

```text
scripts/shell/
├── Makefile              # Unified entrypoint — .PHONY targets for all scripts
├── README.md             # Workspace documentation
├── src/                  # Executable CLI entry points (one file per script)
│   ├── main.sh
│   └── <script-name>.sh
├── lib/                  # Sourced function libraries (no standalone execution)
│   ├── utils.sh          # Shared helpers
│   ├── <script-name>/
│   │   └── core.sh       # Per-script library functions
│   └── shared/           # Sharable across all scripts
│       ├── common.sh     # die(), err(), info(), require(), SCRIPT_DIR pattern
│       └── io.sh         # read_json(), write_json(), filter_json()
├── tests/                # bats-core test files (mirrors src/ layout)
│   └── <script-name>.bats
├── fixtures/             # Test fixture files
│   └── <script-name>/
└── tmp/                  # Ignored by git; runtime output directory
```

## Resolution Order

Following the three-tier resolution pattern established in the platform layout context:

1. `$OPENCODE_SCRIPTS_SHELL` — Environment variable override (optional, highest priority)
2. `<project-root>/.opencode/scripts/shell` — Project-local root
3. `~/.config/opencode/scripts/shell` — Global root (fallback)

Makefile targets should reference a resolved path:

```makefile
SCRIPTS_SHELL ?= $(or $(OPENCODE_SCRIPTS_SHELL),$(PWD)/.opencode/scripts/shell,$(HOME)/.config/opencode/scripts/shell)
```

## Sourcing Rules

### Script-to-Library Sourcing

CLI entry points in `src/` source shared libraries via a `SCRIPT_DIR`-relative path:

```bash
readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../lib/shared/common.sh"
```

Per-script libraries are sourced with a `# shellcheck source=` directive:

```bash
# shellcheck source=../lib/<script-name>/core.sh
source "${SCRIPT_DIR}/../lib/<script-name>/core.sh"
```

### Library Sourcing (not self-executing)

Library files under `lib/`:
- Must **not** have `set -euo pipefail` at the top (the caller sets these flags).
- Must **not** execute any logic at load time; only define functions.
- May define constants with `readonly` at the top for shared use.

### Shared Library Contracts

- `lib/shared/common.sh` — Always available. Provides: `die()`, `err()`, `info()`, `require()`, cleanup trap pattern.
- `lib/shared/io.sh` — Optional. Provides: `read_json_field()`, `write_json()`, `ensure_temp_dir()`.

Library functions use a namespace prefix convention:

```bash
# common.sh
die() { ... }
err() { ... }
info() { ... }
require() { ... }

# io.sh
io::read_json_field() { ... }
io::write_json() { ... }
io::ensure_temp_dir() { ... }
```
