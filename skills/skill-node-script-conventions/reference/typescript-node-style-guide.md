# TypeScript / Node Style Guide

Every generated Node script and lib module must conform to the project's lint and type-check rules.
These are enforced by `biome.json` and `tsconfig.json` at `scripts/node/`.

## Biome Lint Rule Catalog

Biome replaces ESLint + Prettier. The project enables the following rule categories in `biome.json`:

- **recommended** — All enabled lint rules — Core correctness, style, and performance rules as defined by Biome's recommended set
- **organizeImports** — Auto-sort and merge — Groups and sorts imports by type (built-in, third-party, local); removes unused imports
- **formatter** — Style enforcement — Quote style (single), semicolons (asNeeded), indent (2 spaces), line width (120)

Biome's `"recommended": true` covers:

- Correctness rules (no dead code, no invalid constructs)
- Style rules (consistent naming, no unnecessary constructs)
- Performance rules (no expensive operations)
- Complexity rules (no excessive nesting, no redundant qualifiers)
- Suspicious rules (no double equals, no empty blocks)

**Line length:** 120 characters.
**Format:** Generated scripts must pass `bunx biome check src/` before submission.

### Suppressed / Opt-Out Rules

The following are intentionally **not** enabled (matching Biome defaults):

- `noConsole` — `console.log` is permitted for CLI stdout/stderr output.
- `noParameterAssign` — Mutable parameters are permitted in controlled patterns.
- `useExhaustiveDependencies` — React-specific; not relevant to Node scripts.

## TypeScript Strict-Mode Flag Breakdown

The project enables `"strict": true` plus additional opt-in flags in `tsconfig.json`.
Each flag has concrete implications for generated code:

### Strict Family (enabled by `"strict": true`)

- `strictNullChecks` — `null` and `undefined` are distinct types. Use `foo | null` / `bar | undefined` explicitly.
- `strictFunctionTypes` — Function parameter bivariance is disabled. Use `ReadonlyArray<T>` for covariant array params.
- `strictBindCallApply` — `bind`, `call`, `apply` are type-checked.
- `strictPropertyInitialization` — Class properties must be initialized or declared with `!` assertion.
- `noImplicitAny` — Type annotations required on all function parameters and return types.
- `noImplicitThis` — `this` must have an explicit type in callbacks. Use `this: void` or arrow functions.
- `alwaysStrict` — All files parsed in strict mode. Implies `"use strict"` pragma.

### Additional Opt-In Flags

- `noUncheckedIndexedAccess` — Accessing `T[K]` on an index signature returns `T | undefined` — Always. Add explicit undefined checks after bracket access: `const item = arr[i]; if (item !== undefined) { ... }`
- `verbatimModuleSyntax` — Forces `import type` / `export type` for type-only imports/exports — Always. Use `import type { Foo }` instead of `import { Foo }`.
- `exactOptionalPropertyTypes` — Optional properties cannot be set to `undefined` unless explicitly allowed — Always. Use `prop?: string | undefined` if undefined assignment is needed.
- `noImplicitOverride` — `override` keyword required when overriding a base class method — Always. Use `override` on subclass method implementations.
- `noFallthroughCasesInSwitch` — Fallthrough between `case` blocks is an error — Always. Add `break` or `return` after every `case` body.
- `skipLibCheck` — Skip type checking of `.d.ts` files — Always. Speeds up type checking; Bun handles lib resolution.

## Import Ordering Convention

All imports must follow a three-group convention separated by blank lines.
Within each group, imports are alphabetically sorted.

1. **Node built-ins** — `node:fs`, `node:path`, `node:os`, `node:child_process`, etc.
2. **Third-party** — `cleye`, `remark`, `remark-gfm`, etc.
3. **Local** — `../lib/shared/*`, `../lib/<script-name>/*`

```typescript
import { existsSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

import { cli } from 'cleye'

import { resolveTarget, isExempted } from '../lib/shared/path.ts'
import { lintFile } from '../lib/lint-md/core.ts'
import { formatViolation, die } from '../lib/shared/format.ts'
import { ExitCode } from '../lib/shared/exit-codes.ts'
```

**Key rules:**

- `node:` prefix is required for all Node.js built-in imports.
- `.ts` extension is required in all local relative imports (Bun requirement).
- `import type` is required for type-only imports when `verbatimModuleSyntax` is enabled.
- No barrel files (`index.ts`) — import directly from source modules.

## Naming Conventions

- **Script names (package.json)** — kebab-case — `<script-name>` — `lint-md`, `format-json`
- **CLI entry point files** — kebab-case `.ts` — `src/cli/<script-name>.ts` — `src/cli/lint-md.ts`
- **Lib module files** — kebab-case `.ts` — `src/lib/<script-name>/<module>.ts` — `src/lib/lint-md/core.ts`
- **Shared lib files** — kebab-case `.ts` — `src/lib/shared/<module>.ts` — `src/lib/shared/exit-codes.ts`
- **Test files (unit)** — kebab-case `.test.ts` — `tests/<script-name>.test.ts` — `tests/lint-md.test.ts`
- **Test files (CLI)** — kebab-case `.cli.test.ts` — `tests/<script-name>.cli.test.ts` — `tests/lint-md.cli.test.ts`
- **Functions** — camelCase — `verbNoun()` — `lintFile()`, `resolveTarget()`
- **Const enums / constants** — PascalCase — `EnumName` — `ExitCode`, `ExitCode.CLEAN`
- **Types / Interfaces** — PascalCase — `TypeName` — `type Violation`, `interface LintResult`
- **Type parameters / generics** — PascalCase — `T`, `TResult` — `map<T, U>()`
- **Private / internal members** — camelCase with `_` prefix — `_internalFn()` — `_validate()`

## Type Annotation Patterns

All function signatures in generated code must include explicit type annotations.
Use these conventions:

```typescript
// Standard annotations — explicit return types required
function countWords(text: string, encoding: string = 'utf-8'): number { ... }

// Discriminated unions for result types
type LintResult =
  | { kind: 'success'; violations: Violation[] }
  | { kind: 'error'; message: string; code: ExitCode }

// Readonly<T> for immutable parameters
function processPaths(paths: readonly string[]): ReadonlyMap<string, number> { ... }

// Branded types for type-safe identifiers
type FilePath = string & { readonly __brand: 'FilePath' }
function toFilePath(raw: string): FilePath {
  return resolve(raw) as FilePath
}

// ReadonlyArray<T> over T[] for function parameters
function findFiles(patterns: readonly string[]): string[] { ... }

// const enum for fixed constants (avoids runtime overhead)
const enum ExitCode {
  CLEAN = 0,
  VIOLATIONS = 1,
  CONFIG_ERROR = 2,
  INVALID_INPUT = 3,
}

// Promise<T> for async function return types
async function lintFile(path: string): Promise<LintResult> { ... }

// Typed catch clauses with error narrowing
try { ... }
catch (err: unknown) {
  const message = err instanceof Error ? err.message : String(err)
  die(`Error: ${message}`, ExitCode.CONFIG_ERROR)
}
```

**Key rules:**

- **Explicit return types** on all function signatures (no implicit any).
- **`const enum`** for exit codes and fixed constants (avoids runtime overhead).
- **ReadonlyArray / Readonly** prefix on parameters not intended for mutation.
- **Discriminated unions** preferred over overloaded return types for result-or-error patterns.
- **Branded types** for path-like identifiers that should not be mixed with raw strings.
- **`unknown`** in catch clauses — narrow with `instanceof` or `typeof` checks.
- **`string`** over custom wrapper types for simple values unless type safety demands branding.

## Coverage Exemption Conventions

Use coverage exemptions sparingly and only for these three categories:

### 1. Unreachable defensive code

Branches that exist only for type narrowing and cannot be triggered in practice:

```typescript
const item = arr[i]
if (item === undefined) {
  /* c8 ignore next 2 */
  throw new Error('unreachable — bounds checked above')
}
```

### 2. Type narrowing fallthroughs

Exhaustive switch statements where TypeScript cannot prove exhaustiveness:

```typescript
switch (result.kind) {
  case 'success': return result.violations
  case 'error': return []
  default:
    /* c8 ignore next 2 */
    // @ts-expect-error — exhaustive check
    throw new Error(`unhandled kind: ${result satisfies never}`)
}
```

### 3. `@ts-expect-error` suppression

Use `@ts-expect-error` when TypeScript flags a correct pattern that the runtime supports:

```typescript
// @ts-expect-error — Bun supports top-level await
await main()
```

(Note: bun:test globals like `describe`, `test`, etc. are exempt from the `@typescript-eslint/no-unused-vars` equivalent.)

### Exemption Syntax Reference

- `` `/* c8 ignore next */` `` — c8 (Bun coverage) — Suppress coverage for the next line
- `` `/* c8 ignore next <N> */` `` — c8 (Bun coverage) — Suppress coverage for the next N lines
- `` `@ts-expect-error` `` — TypeScript — Suppress the next TypeScript error
- `` `// biome-ignore lint: <reason>` `` — Biome — Suppress a specific Biome lint rule

### When NOT to Exempt

All other branches, error paths, and edge cases must be covered by tests.
If a coverage exemption appears outside the three categories above, re-examine the test generation rather than exempting coverage.

**Do not exempt:**

- `process.exit()` calls — must have corresponding `Bun.spawnSync` tests.
- Error-handling branches — must be tested with invalid input.
- Default values in parameter destructuring — test the fallback path.
