# CLI Conventions

Every generated Node script must follow these CLI design patterns.

## Cleye CLI Pattern

Use `cleye` for CLI argument parsing.
Define the CLI with a typed parameters array and flags object.

- **Parameters**: Required positional arguments declared as strings in the `parameters` array using angle brackets (e.g., `['<input-path>']`).
- **Flags**: Optional named options defined inline with type annotations (e.g., `--format`).
- **Version flag**: Include `version` in the cleye options object.

```typescript
import cli from 'cleye'

cli({
  name: '<script-name>',
  version: '<version>',
  parameters: ['<required-arg>'],
})

async function main(): Promise<void> {
  // Parse process.argv via utility functions
  const target = resolveTarget(process.argv)
  // ...
}

await main()
```

Cleye does not automatically stop execution after parsing.
The script must handle its own `process.exit()` and `process.stderr.write()` for errors.

## Output Format Standards

- **Primary result**: `process.stdout.write(JSON.stringify(result) + '\n')` — JSON on stdout.
  Output consumed by another skill (default).
- **Human-readable**: `process.stdout.write(`Found ${n} files\n`)` — plain text on stdout.
  Output displayed directly to user.
- **Progress/info**: `process.stderr.write(message + '\n')` — stderr.
  Status messages when stdout is structured data.
- **Errors**: `process.stderr.write(`Error: ${msg}\n`)` + `process.exit(code)` — All failure paths.

When output is consumed by another skill, emit a single JSON object or array to stdout.
Use `JSON.stringify()` with a replacer for non-serializable types.

## Exit Code Conventions

Use the `ExitCode` const enum from `src/lib/shared/exit-codes.ts`.

- Exit code `0` (`CLEAN`) — Normal completion, output on stdout.
- Exit code `1` (`VIOLATIONS`) — Unacceptable condition found.
- Exit code `2` (`CONFIG_ERROR`) — Configuration or environment issue.
- Exit code `3` (`INVALID_INPUT`) — Invalid arguments or input.

```typescript
const enum ExitCode {
  CLEAN = 0,
  VIOLATIONS = 1,
  CONFIG_ERROR = 2,
  INVALID_INPUT = 3,
}
```

Generated scripts call `process.exit(code)` explicitly.
Do not catch `process.exit` — it is a legitimate termination path.

## Error Message Formatting

Error messages follow a consistent pattern: `Error: <human-readable description>`.
Write to stderr via `process.stderr.write()`.
Start with `"Error: "` prefix (capital E, colon, space).
Include the specific cause when available (file name, invalid value).
Do not include TypeScript stack traces in user-facing output.

Use the `die` helper from `src/lib/shared/format.ts`:

```typescript
export function die(message: string, code: ExitCode): never {
  process.stderr.write(message + '\n')
  process.exit(code)
}
```

Callers use `die("Error: file not found: /path/to/file", ExitCode.INVALID_INPUT)`.

## Complete Real-World Example: `lint-md`

The following example demonstrates all CLI conventions.

```typescript
import cli from 'cleye'
import { resolveTarget, isExempted } from '../lib/shared/path.ts'
import { lintFile } from '../lib/lint-md/core.ts'
import { formatViolation, die } from '../lib/shared/format.ts'
import { ExitCode } from '../lib/shared/exit-codes.ts'
import { existsSync } from 'node:fs'
import { resolve } from 'node:path'

cli({
  name: 'lint-md',
  version: '1.0.0',
  parameters: ['<input-path>'],
})

async function main(): Promise<void> {
  const targetPath = resolveTarget(process.argv)

  if (!targetPath) {
    die('Error: no target file specified. Usage: bun run --cwd scripts/node lint:md -- <target-file>', ExitCode.INVALID_INPUT)
  }

  const resolvedPath = resolve(targetPath)

  if (!existsSync(resolvedPath)) {
    die(`Error: file not found: ${resolvedPath}`, ExitCode.INVALID_INPUT)
  }

  let result
  try {
    result = await lintFile(resolvedPath)
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    die(`Error: lint processing failed: ${message}`, ExitCode.CONFIG_ERROR)
  }

  const { violations } = result

  if (violations.length === 0) {
    process.exit(ExitCode.CLEAN)
  }

  for (const v of violations) {
    process.stderr.write(
      formatViolation(v.filePath, v.line, v.column, v.ruleId, v.message) + '\n',
    )
  }

  process.exit(ExitCode.VIOLATIONS)
}

await main()
```

This example illustrates: cleye name/version/parameters declaration, type annotations on every function signature, `node:fs` and `node:path` imports for filesystem operations, separate error classes caught with friendly messages to stderr and non-zero exit, JSON or structured output via process.stdout/process.stderr, core logic delegated to lib modules, top-level `await main()` pattern for async scripts, and explicit `process.exit()` calls on all exit paths.