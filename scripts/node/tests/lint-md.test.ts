import { describe, expect, test } from 'bun:test'
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { lintFile } from '../src/lib/lint-md/core.ts'

async function withTempDir(fn: (dir: string) => Promise<void>): Promise<void> {
  const dir = mkdtempSync(join(tmpdir(), 'lint-md-test-'))
  try {
    await fn(dir)
  } finally {
    rmSync(dir, { recursive: true, force: true })
  }
}

describe('lintFile', () => {
  test('clean markdown returns empty violations', async () => {
    await withTempDir(async (dir) => {
      const filePath = join(dir, 'clean.md')
      writeFileSync(filePath, '# Heading\n\nSome paragraph text.\n\n## Subheading\n\nMore text.\n')
      const result = await lintFile(filePath)
      expect(result.violations).toHaveLength(0)
      expect(result.filePath).toBe(filePath)
    })
  })

  test('detects duplicate headings as violations', async () => {
    await withTempDir(async (dir) => {
      const filePath = join(dir, 'duplicate.md')
      writeFileSync(filePath, '# Heading\n\nContent\n\n# Heading\n\nMore content\n')
      const result = await lintFile(filePath)
      expect(result.violations.length).toBeGreaterThan(0)
      expect(result.violations.some((v) => v.ruleId.includes('duplicate'))).toBe(true)
    })
  })

  test('detects heading punctuation as violations', async () => {
    await withTempDir(async (dir) => {
      const filePath = join(dir, 'punctuation.md')
      writeFileSync(filePath, '# Heading!\n\nContent\n')
      const result = await lintFile(filePath)
      expect(result.violations.length).toBeGreaterThan(0)
      expect(result.violations.some((v) => v.ruleId.includes('punctuation'))).toBe(true)
    })
  })

  test('detects tables as violations', async () => {
    await withTempDir(async (dir) => {
      const filePath = join(dir, 'tables.md')
      writeFileSync(filePath, '# Heading\n\n| Col1 | Col2 |\n|------|------|\n| A    | B    |\n')
      const result = await lintFile(filePath)
      expect(result.violations.length).toBeGreaterThan(0)
      expect(result.violations.some((v) => v.ruleId === 'no-tables')).toBe(true)
    })
  })

  test('empty file returns no violations', async () => {
    await withTempDir(async (dir) => {
      const filePath = join(dir, 'empty.md')
      writeFileSync(filePath, '')
      const result = await lintFile(filePath)
      expect(result.violations).toHaveLength(0)
    })
  })

  test('throws on nonexistent file', async () => {
    expect(lintFile('/nonexistent/path/file.md')).rejects.toThrow()
  })
})