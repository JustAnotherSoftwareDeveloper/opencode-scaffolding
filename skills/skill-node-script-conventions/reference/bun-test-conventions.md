# Bun Test Conventions

## Naming Conventions

### Test Files

| Pattern | File | Purpose |
|---------|------|---------|
| `tests/<script-name>.test.ts` | Unit tests | Test `lib/` modules with direct imports |
| `tests/<script-name>.cli.test.ts` | CLI integration | Test CLI with `Bun.spawnSync` |
| `tests/<shared-module>.test.ts` | Shared lib tests | Test `src/lib/shared/` modules |

### Test Structure

- **describe blocks** — Group by module, feature, or scenario.
- **test / it names** — Verb phrase describing the expected behavior: `'exits with clean code on valid input'`, `'processes an empty file'`.
- **No `.skip` or `.todo`** in generated test files — every test runs.

## bun:test Globals

Import from `bun:test`:

```typescript
import {
  describe,
  expect,
  test,
  it,
  beforeAll,
  afterAll,
  beforeEach,
  afterEach,
  mock,
  spyOn,
} from 'bun:test'
```

### Core Functions

| Function | Purpose |
|----------|---------|
| `describe(name, fn)` | Group related tests |
| `test(name, fn)` / `it(name, fn)` | Define a test case |
| `expect(value)` | Assertion entry point |
| `beforeAll(fn)` | Run once before all tests in describe block |
| `afterAll(fn)` | Run once after all tests in describe block |
| `beforeEach(fn)` | Run before each test in describe block |
| `afterEach(fn)` | Run after each test in describe block |
| `mock(fn?)` | Create a mock function |
| `spyOn(obj, method)` | Wrap a method to track calls |

### Test Modifiers

- `test.skip()` — Skip a test (not used in generated tests).
- `test.todo()` — Mark as todo (not used in generated tests).
- `test.only()` — Run only this test (requires `bun test --only`).
- `test.if(condition)` — Conditional execution.
- `test.skipIf(condition)` — Conditional skip.
- `test.failing()` — Invert result (expected failure).
- `test.concurrent()` — Run in parallel.
- `test.serial()` — Force sequential execution.

## CLI Integration Tests with Bun.spawnSync

`Bun.spawnSync` is the recommended synchronous API for testing CLI scripts.
It returns a `SyncSubprocess` object.

```typescript
import { describe, expect, test } from 'bun:test'

describe('CLI integration', () => {
  test('exits with clean code on valid input', () => {
    const result = Bun.spawnSync(['bun', 'src/cli/lint-md.ts', '--', 'test-file.md'])

    expect(result.exitCode).toBe(0)
    expect(result.stdout.toString()).toContain('expected output')
  })

  test('exits with error on missing file', () => {
    const result = Bun.spawnSync(['bun', 'src/cli/lint-md.ts', '--', 'nonexistent.md'])

    expect(result.exitCode).toBe(3) // INVALID_INPUT
    expect(result.stderr.toString()).toContain('Error:')
  })
})
```

### SyncSubprocess Properties

| Property | Type | Description |
|----------|------|-------------|
| `exitCode` | `number` | The process exit code |
| `success` | `boolean` | Shorthand for `exitCode === 0` |
| `stdout` | `Buffer` | Stdout contents (call `.toString()`) |
| `stderr` | `Buffer` | Stderr contents |

## Fixture Setup Pattern (mkdtempSync / rmSync)

Use `mkdtempSync` + `beforeAll` for temporary directory creation and `rmSync` + `afterAll` for cleanup.

```typescript
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { describe, expect, test, beforeAll, afterAll } from 'bun:test'

let tmpDir: string

beforeAll(() => {
  tmpDir = mkdtempSync(join(tmpdir(), 'test-'))
})

afterAll(() => {
  rmSync(tmpDir, { recursive: true, force: true })
})

test('processes a fixture file', () => {
  const fixturePath = join(tmpDir, 'test.md')
  writeFileSync(fixturePath, '# Test content')

  const result = Bun.spawnSync(['bun', 'src/cli/lint-md.ts', '--', fixturePath])
  expect(result.exitCode).toBe(0)
})
```

## Parameterized Tests

Use `test.each` and `describe.each` for data-driven testing.

### test.each for Input Variations

```typescript
const cases = [
  ['', 0],
  ['hello', 1],
  ['hello world', 2],
  ['hello   world', 2],
] as const

test.each(cases)('countTokens("%s") -> %d', (input, expected) => {
  expect(countTokens(input)).toBe(expected)
})
```

### describe.each for Error Paths

```typescript
const errorCases = [
  { args: ['nonexistent.md'], exitCode: 3, stderrContains: 'file not found' },
  { args: ['--format', 'bogus', 'test.md'], exitCode: 3, stderrContains: 'invalid format' },
] as const

describe.each(errorCases)('error path: $args', ({ args, exitCode, stderrContains }) => {
  test(`exits with code ${exitCode}`, () => {
    const result = Bun.spawnSync(['bun', 'src/cli/lint-md.ts', ...args])
    expect(result.exitCode).toBe(exitCode)
    expect(result.stderr.toString()).toContain(stderrContains)
  })
})
```

## Test Isolation Conventions

Each test is independent and shares no state with other tests.

- **Temp directories** — Create a new temp directory per `describe` block (or per test if mutable state).
- **No module-level mutable state** — Use `beforeAll` / `beforeEach` to reset state.
- **Mock restoration** — Use `afterEach` to restore all mocks:

```typescript
import { afterEach, mock } from 'bun:test'

afterEach(() => {
  mock.restore()       // Restore all mocks to original implementations
  mock.clearAllMocks() // Clear call history
})
```

- **File fixtures** — Write fixture files inside the temp directory; never modify files outside it.
- **Cleanup** — Always clean up temp directories in `afterAll` with `rmSync(path, { recursive: true, force: true })`.

## Paired Source-to-Test File Mapping

The test writer reads generated source files to determine module structure and generates corresponding tests.

| Source File | Test File |
|-------------|-----------|
| `src/cli/<name>.ts` | `tests/<name>.cli.test.ts` |
| `src/lib/<name>/core.ts` | `tests/<name>.test.ts` |
| `src/lib/<name>/rules.ts` | Coverage included in `tests/<name>.test.ts` |
| `src/lib/shared/<module>.ts` | `tests/<module>.test.ts` |

### Unit Test Imports (Direct)

```typescript
// tests/lint-md.test.ts
import { lintFile } from '../src/lib/lint-md/core.ts'
import { ExitCode } from '../src/lib/shared/exit-codes.ts'
```

### CLI Test Imports (Minimal)

```typescript
// tests/lint-md.cli.test.ts
import { describe, expect, test, beforeAll, afterAll } from 'bun:test'
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
```

## Mocking Patterns

### mock.module() for Module-Level Mocks

```typescript
import { mock } from 'bun:test'

mock.module('../src/lib/api-client.ts', () => ({
  fetchUser: mock(async (id: string) => ({ id, name: `User ${id}` })),
}))
```

### spyOn() for Method Tracking

```typescript
const obj = { method() { return 42 } }
const spy = spyOn(obj, 'method')

obj.method()
expect(spy).toHaveBeenCalledTimes(1)
```

### Mock Function API

```typescript
const fn = mock(() => 'default')
fn.mockImplementationOnce(() => 'first')
fn.mockReturnValue('value')
fn.mockResolvedValue('async value')

expect(fn()).toBe('first')
expect(fn()).toBe('value')
```

## Assertion Best Practices

- **`expect(result.exitCode).toBe(0)`** — Preferred for CLI tests.
- **`expect(result.stdout.toString()).toContain(...)`** — Assert on output content.
- **`expect(result.stderr.toString()).toContain(...)`** — Assert on error output.
- **`expect(fn).toHaveBeenCalledTimes(n)`** — Assert on mock call counts.
- **`expect(fn).toHaveBeenCalledWith(...)`** — Assert on mock arguments.
- **`expect(() => fn()).toThrow()`** — Assert on synchronous throws.
- **`expect(promise).rejects.toThrow()`** — Assert on async rejections.
- Use `expect.hasAssertions()` in async tests to verify assertions ran.