# Test Examples

## Example 1: Bun.spawnSync CLI Integration Test with Temp Fixture

```typescript
/**
 * CLI integration tests for lint-md.
 * Tests the full pipeline from argument parsing to exit code.
 */

import { describe, expect, test, beforeAll, afterAll } from 'bun:test'
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

let tmpDir: string
const cliEntry = ['bun', 'src/cli/lint-md.ts']

beforeAll(() => {
  tmpDir = mkdtempSync(join(tmpdir(), 'lint-md-test-'))
})

afterAll(() => {
  rmSync(tmpDir, { recursive: true, force: true })
})

function runLintMd(...args: string[]) {
  return Bun.spawnSync([...cliEntry, '--', ...args])
}

describe('lint-md CLI', () => {
  test('exits with code 0 on valid markdown file', () => {
    const filePath = join(tmpDir, 'valid.md')
    writeFileSync(filePath, '# Hello World\n\nThis is valid.\n')

    const result = runLintMd(filePath)
    expect(result.exitCode).toBe(0)
    expect(result.stdout.toString()).toContain('violations')
  })

  test('exits with code 3 on nonexistent file', () => {
    const result = runLintMd(join(tmpDir, 'nonexistent.md'))
    expect(result.exitCode).toBe(3)
    expect(result.stderr.toString()).toContain('file not found')
  })

  test('exits with code 3 on missing argument', () => {
    const result = runLintMd()
    expect(result.exitCode).toBe(3)
    expect(result.stderr.toString()).toContain('no target file')
  })
})
```

## Example 2: mkdtempSync / rmSync File-Based Unit Test

```typescript
/**
 * Unit tests for lint-md lib module.
 * Tests core logic with temp directory fixtures.
 */

import { describe, expect, test, beforeAll, afterAll } from 'bun:test'
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

import { lintFile } from '../src/lib/lint-md/core.ts'

let tmpDir: string

beforeAll(() => {
  tmpDir = mkdtempSync(join(tmpdir(), 'lint-md-lib-'))
})

afterAll(() => {
  rmSync(tmpDir, { recursive: true, force: true })
})

describe('lintFile()', () => {
  test('returns no violations for valid markdown', async () => {
    const filePath = join(tmpDir, 'valid.md')
    writeFileSync(filePath, '# Valid\n\nContent here.\n')

    const result = await lintFile(filePath)
    expect(result.kind).toBe('success')
    if (result.kind === 'success') {
      expect(result.violations).toHaveLength(0)
    }
  })

  test('throws on nonexistent file', async () => {
    expect(lintFile(join(tmpDir, 'missing.md'))).rejects.toThrow()
  })
})
```

## Example 3: mock.module() Module Mocking

```typescript
/**
 * Tests for lint-md with module-level mocking.
 * Demonstrates mocking a file-system dependency.
 */

import { describe, expect, test, mock } from 'bun:test'

// Mock the path resolution module before any imports
mock.module('../src/lib/shared/path.ts', () => ({
  resolveTarget: mock((args: string[]) => args[2] ?? null),
  isExempted: mock((_path: string) => false),
}))

// Now import AFTER the mock is registered
import { lintFile } from '../src/lib/lint-md/core.ts'

describe('lintFile with mocked dependencies', () => {
  test('processes a mock file path', async () => {
    // The mock resolveTarget will return the third argument
    // isExempted always returns false
    const result = await lintFile('/mock/path.md')
    expect(result).toBeDefined()
  })
})
```

## Example 4: spyOn() Spy Example

```typescript
/**
 * Demonstrates spyOn for tracking method calls.
 */

import { describe, expect, test, spyOn } from 'bun:test'

const logger = {
  info(message: string) {
    process.stdout.write(message + '\n')
  },
  error(message: string) {
    process.stderr.write(message + '\n')
  },
}

describe('logger', () => {
  test('info writes to stdout', () => {
    const spy = spyOn(process.stdout, 'write')
    logger.info('hello')
    expect(spy).toHaveBeenCalledTimes(1)
    expect(spy).toHaveBeenCalledWith('hello\n')
    spy.mockRestore()
  })
})
```

## Example 5: test.each Parameterized Input Test

```typescript
/**
 * Parameterized unit tests for a token counting function.
 * Tests various input patterns with a single test definition.
 */

import { describe, expect, test } from 'bun:test'

// Function under test
function countTokens(text: string): number {
  if (text.trim().length === 0) return 0
  return text.trim().split(/\s+/).length
}

const testCases = [
  { input: '', expected: 0 },
  { input: '   ', expected: 0 },
  { input: 'hello', expected: 1 },
  { input: 'hello world', expected: 2 },
  { input: 'hello   world', expected: 2 },
  { input: 'a b c d e', expected: 5 },
  { input: 'line1\nline2\nline3', expected: 3 },
  { input: '\n\n\n', expected: 0 },
] as const

test.each(testCases)('countTokens($input) -> $expected', ({ input, expected }) => {
  expect(countTokens(input)).toBe(expected)
})
```

## Example 6: describe.each Parameterized Error-Path Test

```typescript
/**
 * Parameterized error-path tests for CLI.
 * Covers every non-zero exit code with a single describe block.
 */

import { describe, expect, test } from 'bun:test'

const errorCases = [
  { args: [] as string[], exitCode: 3, stderrContains: 'no target file' },
  { args: ['nonexistent.md'], exitCode: 3, stderrContains: 'file not found' },
  { args: ['--format', 'bogus', 'test.md'], exitCode: 3, stderrContains: 'invalid format' },
] as const

describe.each(errorCases)('error: $args', ({ args, exitCode, stderrContains }) => {
  test(`exits with code ${exitCode}`, () => {
    const result = Bun.spawnSync(['bun', 'src/cli/lint-md.ts', ...args])
    expect(result.exitCode).toBe(exitCode)
    expect(result.stderr.toString()).toContain(stderrContains)
  })
})
```

## Example 7: beforeAll Shared Fixture Helper Extraction Pattern

```typescript
/**
 * Demonstrates shared fixture helper extraction.
 * The createTempDir / cleanupTempDir helpers can be reused across test files.
 */

import { mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { describe, expect, test, beforeAll, afterAll } from 'bun:test'

import { lintFile } from '../src/lib/lint-md/core.ts'

// Shared fixture helpers
class TempDirFixture {
  path: string

  constructor(prefix: string) {
    this.path = mkdtempSync(join(tmpdir(), prefix))
  }

  writeFile(name: string, content: string): string {
    const filePath = join(this.path, name)
    writeFileSync(filePath, content)
    return filePath
  }

  cleanup(): void {
    rmSync(this.path, { recursive: true, force: true })
  }
}

describe('lintFile with helper fixture', () => {
  let fixture: TempDirFixture

  beforeAll(() => {
    fixture = new TempDirFixture('lint-md-helper-')
  })

  afterAll(() => {
    fixture.cleanup()
  })

  test('processes a valid markdown file', async () => {
    const filePath = fixture.writeFile('valid.md', '# Title\n\nBody.\n')
    const result = await lintFile(filePath)
    expect(result.kind).toBe('success')
  })

  test('processes an empty markdown file', async () => {
    const filePath = fixture.writeFile('empty.md', '')
    const result = await lintFile(filePath)
    expect(result.kind).toBe('success')
  })

  test('processes a file with violations', async () => {
    const filePath = fixture.writeFile('bad.md', '# No space after heading\n')
    const result = await lintFile(filePath)
    expect(result.kind).toBe('success')
  })
})
```