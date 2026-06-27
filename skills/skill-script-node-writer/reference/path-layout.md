# Path Layout

Generated Node scripts live under `scripts/node/` within either the global or project-local root.
Both roots follow the same directory layout; the difference is their filesystem location and resolution priority.

## Platform Selection: Node vs Python

Use Node scripts only when the task requires Node-specific capabilities:

- **remark ecosystem** — Markdown parsing, linting, and transformation.
- **Node filesystem APIs** — `node:fs`, `node:path`, `node:child_process` for operations where Python equivalents are less ergonomic.
- **npm ecosystem tools** — Libraries unavailable or poorly supported in Python.
- **Bun runtime features** — Built-in TypeScript execution, test runner, or package manager integration.

Default to Python (via `skill-script-python-writer`) for general-purpose scripting.
Node is the secondary platform, chosen when a capability gap makes Python impractical.

## Directory Layout (Both Roots)

```
scripts/node/
  src/
    cli/<script_name>.ts          # cleye CLI (main entry point)
    lib/
      <script_name>/              # library package (one per script)
        core.ts                   # core logic
        rules.ts                  # rule definitions (if needed)
      shared/                     # shared utilities (cross-script)
        exit-codes.ts             # ExitCode enum
        format.ts                 # stdout/stderr formatting
        path.ts                   # path resolution utilities
```

## Import Conventions

Use relative imports with `.ts` extensions throughout.
This is required by Bun's TypeScript resolver.

**Import from a CLI entry point** (`src/cli/<script-name>.ts`):

```typescript
import { resolveTarget, isExempted } from '../lib/shared/path.ts'
import { lintFile } from '../lib/<script-name>/core.ts'
import { formatViolation, die } from '../lib/shared/format.ts'
import { ExitCode } from '../lib/shared/exit-codes.ts'
```

**Import from a per-script lib module** (`src/lib/<script-name>/core.ts`):

```typescript
import { existsSync } from 'node:fs'
import { resolve } from 'node:path'
```

## Shared Lib Pattern

Shared utility modules live in `src/lib/shared/` and are imported by multiple scripts.
Three shared modules exist:

- `exit-codes.ts` — Const enum `ExitCode` with `CLEAN`, `VIOLATIONS`, `CONFIG_ERROR`, `INVALID_INPUT`.
- `format.ts` — `formatViolation()` and `die()` helpers for stdout/stderr output.
- `path.ts` — `resolveTarget()` and `isExempted()` for argv parsing.

### Extraction Rule

Keep utility code in a per-script lib package until a second script needs it.
Extract to `src/lib/shared/` only when the function or class is imported by two or more scripts.
Premature extraction is discouraged — a single consumer does not justify shared placement.