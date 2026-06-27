# Path Layout

Generated Node scripts live under `scripts/node/` within either the global or project-local root.
Both roots follow the same directory layout; the difference is their filesystem location and resolution priority.

> **Platform selection guidance** — See `skill-architect` (class-decision-flow) for the formal decision framework on choosing Node vs Python.
> **Resolution order** — See `skill-architect` (platform-layout-context) for script-root resolution precedence (env var → project-local → global).
> **Shared lib rules** — See `shared-lib-rules.md` for shared module conventions.
> **Tooling configuration** — See `tooling-config.md` for biome, tsc, and package.json config.

## Directory Layout (Both Roots)

```text
scripts/node/
  src/
    cli/<script-name>.ts          # cleye CLI entry point
    lib/
      <script-name>/              # per-script library package
        core.ts                   # core logic
        rules.ts                  # rule definitions (if needed)
      shared/                     # shared utilities (cross-script)
        exit-codes.ts             # ExitCode const enum
        format.ts                 # stdout/stderr formatting helpers
        path.ts                   # path resolution utilities
  tests/
    <script-name>.test.ts         # unit tests
    <script-name>.cli.test.ts     # CLI integration tests
  package.json
  tsconfig.json
  biome.json
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
import { ExitCode } from '../shared/exit-codes.ts'
```

**Import in a test file** (`tests/<script-name>.test.ts`):

```typescript
import { lintFile } from '../src/lib/lint-md/core.ts'
import { ExitCode } from '../src/lib/shared/exit-codes.ts'
```

**Import in a CLI test file** (`tests/<script-name>.cli.test.ts`):

```typescript
import { describe, expect, test, beforeAll, afterAll } from 'bun:test'
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
```

## Module Organization Principles

- **Single responsibility per module** — One `.ts` file per concern.
- **No barrel files** — Import from the exact path, not `index.ts`.
- **Flat-ish lib structure** — Per-script `lib/<script-name>/` directory, not deeply nested.
- **CLI entry points are thin** — Parse args, call lib functions, handle errors. Business logic lives in `lib/`.
