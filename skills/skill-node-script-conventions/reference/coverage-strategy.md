# Coverage Strategy

## Measurement Tool

Coverage is measured via Bun's built-in coverage tooling.

**Run coverage:**
```bash
bun test --coverage
```

**Options:**
| Flag | Purpose |
|------|---------|
| `--coverage` | Enable coverage measurement |
| `--coverage-reporter text` | Console output (default) |
| `--coverage-reporter lcov` | LCOV format for CI integration |
| `--coverage-dir <path>` | Output directory (default: `coverage/`) |

Coverage is measured at the **line level** via c8 (Bun's integrated coverage engine).
The `text` reporter prints specific uncovered lines on failure.

## Source Coverage Boundaries

Coverage is measured against these source paths:

| Source Path | Tested By |
|-------------|-----------|
| `src/cli/*.ts` | CLI entry points tested via `Bun.spawnSync` in `<name>.cli.test.ts` files |
| `src/lib/<script-name>/*.ts` | Per-script library modules tested via direct function calls in `<name>.test.ts` files |
| `src/lib/shared/*.ts` | Shared library modules tested via `<module>.test.ts` files |

Only `src/` is measured. The `tests/` directory and `node_modules/` are excluded by convention.

## Threshold Policy

### fail_under = 100 (Recommended)

Every generated test suite must achieve 100% line coverage.
If coverage drops below 100, the test generation retries once with expanded edge-case tests.
On second failure, return `PARTIAL` with the failing test names and specific coverage gaps.

### Execution

Without a `bunfig.toml` threshold config, coverage is run with:
```bash
bun test --coverage --coverage-reporter text
```

The exit code is non-zero if any uncovered lines exist.
If a `bunfig.toml` is desired for CI:

```toml
[test]
coverage = true
coverageReporter = "lcov"
coverageDir = "coverage"
```

## Edge Case Identification Checklist

To achieve 100% coverage, every test suite must include tests for the following edge cases:

### 1. Input
- Empty input (empty file, empty string, empty list)
- Whitespace-only input
- Maximum-size input / large input
- Single-element input
- Null / undefined values (where applicable)

### 2. File I/O
- Nonexistent file path
- Directory passed where file expected
- Unreadable file (permission denied)
- File with unusual encoding (UTF-8 with BOM, Latin-1)
- Symlink to file
- File with trailing newline or no trailing newline

### 3. CLI Arguments
- Missing required argument
- Invalid option value (`--format bogus`)
- Extra positional arguments
- `--help` flag produces output
- `--` separator before file path

### 4. Error Handling
- Exception thrown in lib module
- Malformed input data
- Dependency failure (e.g., YAML parse error, JSON parse error)
- Timeout or resource exhaustion
- `process.exit()` called with each `ExitCode` value

### 5. Output
- Zero-result output
- Single-result output
- Multi-result output
- Output with special characters
- Output exceeding typical size

### 6. Boundary Values
- Minimum input (0, empty)
- Maximum values (large file, many items)
- Type boundaries (`undefined` vs empty string vs blank string)
- Edge of allowed character ranges

## Error Path Testing

Every non-zero `process.exit(code)` path must have a corresponding `Bun.spawnSync` test.
Use `describe.each` or `test.each` to cover multiple error conditions compactly:

```typescript
import { describe, expect, test } from 'bun:test'

const errorCases = [
  { args: ['nonexistent.md'], exitCode: 3, stderrContains: 'file not found' },
  { args: ['--format', 'bogus', 'test.md'], exitCode: 3, stderrContains: 'invalid format' },
  { args: [], exitCode: 3, stderrContains: 'no target file' },
] as const

describe.each(errorCases)('error path: $args', ({ args, exitCode, stderrContains }) => {
  test(`exits with code ${exitCode}`, () => {
    const result = Bun.spawnSync(['bun', 'src/cli/lint-md.ts', ...args])
    expect(result.exitCode).toBe(exitCode)
    expect(result.stderr.toString()).toContain(stderrContains)
  })
})
```

### Exit Code Mapping

| Exit Code | Constant | When Used |
|-----------|----------|-----------|
| `0` | `ExitCode.CLEAN` | Normal completion |
| `1` | `ExitCode.VIOLATIONS` | Unacceptable condition found |
| `2` | `ExitCode.CONFIG_ERROR` | Configuration or environment issue |
| `3` | `ExitCode.INVALID_INPUT` | Invalid arguments or input |

## Coverage Exemption Conventions

Use coverage exemptions sparingly and only for these three categories:

### 1. Unreachable Defensive Code

Branches that exist only for type narrowing and cannot be triggered in practice:

```typescript
const item = arr[i]
if (item === undefined) {
  /* c8 ignore next 2 */
  throw new Error('unreachable — bounds checked above')
}
```

### 2. Type Narrowing Fallthroughs

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

### 3. `@ts-expect-error` Suppression

Use `@ts-expect-error` when TypeScript flags a correct pattern that the runtime supports:

```typescript
// @ts-expect-error — Bun supports top-level await
await main()
```

### Exemption Syntax Reference

| Syntax | Tool | Purpose |
|--------|------|---------|
| `/* c8 ignore next */` | c8 (Bun coverage) | Suppress coverage for the next line |
| `/* c8 ignore next <N> */` | c8 (Bun coverage) | Suppress coverage for the next N lines |
| `/* c8 ignore start` / `/* c8 ignore stop */` | c8 | Suppress coverage for a block |
| `@ts-expect-error` | TypeScript | Suppress the next TypeScript error |
| `// biome-ignore lint: <reason>` | Biome | Suppress a specific Biome lint rule |
| `// istanbul ignore next` | Istanbul (legacy) | Legacy syntax; prefer `/* c8 ignore */` |

### When NOT to Exempt

All other branches, error paths, and edge cases must be covered by tests.
If a coverage exemption appears outside the three categories above, re-examine the test generation rather than exempting coverage.

**Do not exempt:**
- `process.exit()` calls — must have corresponding `Bun.spawnSync` tests.
- Error-handling branches — must be tested with invalid input.
- Default values in parameter destructuring — test the fallback path.