# Shared Library Rules

Shared utility modules live in `src/lib/shared/` and are imported by multiple scripts.
This follows the "Scripts plus lib" pattern where cross-script utilities are organized by domain rather than by consumer script.

## Five Shared Module Rules

Every shared module must follow these conventions:

### 1. No CLI Entry Points

Shared modules are library code only.
They are imported, never invoked via `bun run` or registered in `package.json` scripts.
No `src/cli/` entry point exists for a shared module.

### 2. 100% Test Coverage Required

Shared modules must meet the same `fail_under = 100` coverage target as per-script packages.
Tests live in `tests/<shared-module>.test.ts` (e.g., `tests/exit-codes.test.ts`).

Every function, branch, and error path in a shared module must be covered.

### 3. Consumer Documentation in Module-Level JSDoc

Each shared module must declare its consumer scripts in a module-level JSDoc comment:

```typescript
/**
 * File/path utilities shared by: lint-md, format-json, collect-skills.
 */
```

This prevents accidental deletion — a maintainer can see which scripts depend on the module without searching imports.

### 4. Domain-Based Naming

Module names describe the utility domain (`exit-codes.ts`, `format.ts`, `path.ts`), not the consuming script.
This prevents rename churn when new scripts import the same module.

**Good** (domain-based): `exit-codes.ts`, `format.ts`, `path.ts`, `schema.ts`
**Bad** (consumer-based): `lint-md-utils.ts`, `shared-by-lint-md.ts`

### 5. Extraction Rule

Keep utility code in a per-script lib package until a second script needs it.
Extract to `src/lib/shared/` only when the function or class is imported by two or more scripts.
Premature extraction is discouraged — a single consumer does not justify shared placement.

## File Layout

```
scripts/node/
  src/
    cli/                          # CLI entry points (cleye)
    lib/
      <script-name>/              # per-script lib packages
        core.ts
        rules.ts                  # (if needed)
      shared/                     # shared utilities (cross-script)
        exit-codes.ts             # ExitCode const enum
        format.ts                 # stdout/stderr formatting helpers
        path.ts                   # path resolution utilities
  tests/
    exit-codes.test.ts
    format.test.ts
    path.test.ts
```

Modules are organized by domain (`exit-codes.ts`, `format.ts`, `path.ts`) not by consumer script.
This prevents duplication when multiple scripts need the same utility.

## Import Convention

Shared modules are imported using relative paths with `.ts` extensions (Bun requirement):

```typescript
import { resolveTarget, isExempted } from '../lib/shared/path.ts'
import { formatViolation, die } from '../lib/shared/format.ts'
import { ExitCode } from '../lib/shared/exit-codes.ts'
```

This convention works identically in CLI entry points, per-script lib modules, and tests because all use the same relative path resolution from `src/`.

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
import { ExitCode } from '../shared/exit-codes.ts'
```

**Import in a test file** (`tests/<script-name>.test.ts`):

```typescript
import { lintFile } from '../src/lib/lint-md/core.ts'
import { ExitCode } from '../src/lib/shared/exit-codes.ts'
```