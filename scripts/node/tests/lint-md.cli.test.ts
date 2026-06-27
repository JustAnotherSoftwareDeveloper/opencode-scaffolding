import { describe, expect, test } from 'bun:test'
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'

function withTempDir(fn: (dir: string) => void): void {
  const dir = mkdtempSync(join(tmpdir(), 'lint-md-cli-test-'))
  try {
    fn(dir)
  } finally {
    rmSync(dir, { recursive: true, force: true })
  }
}

const cliPath = join(import.meta.dir, '../src/cli/lint-md.ts')

describe('lint-md CLI', () => {
  test('valid markdown file exits 0 with no stderr output', () => {
    withTempDir((dir) => {
      const filePath = join(dir, 'valid.md')
      writeFileSync(filePath, '# Valid Heading\n\nSome content.\n')

      const result = Bun.spawnSync(['bun', 'run', cliPath, '--', filePath], {
        env: { ...process.env },
      })

      expect(result.exitCode).toBe(0)
      expect(result.stderr.toString()).toBe('')
    })
  })

  test('file with violations exits 1 with violations on stderr', () => {
    withTempDir((dir) => {
      const filePath = join(dir, 'violations.md')
      writeFileSync(filePath, '# Duplicate\n\nContent\n\n# Duplicate\n')

      const result = Bun.spawnSync(['bun', 'run', cliPath, '--', filePath], {
        env: { ...process.env },
      })

      expect(result.exitCode).toBe(1)
      expect(result.stderr.toString()).not.toBe('')
      expect(result.stderr.toString()).toContain('duplicate')
    })
  })

  test('nonexistent file exits 3 with error message', () => {
    const result = Bun.spawnSync(
      ['bun', 'run', cliPath, '--', '/nonexistent/path/file.md'],
      { env: { ...process.env } },
    )

    expect(result.exitCode).toBe(3)
    expect(result.stderr.toString()).toContain('file not found')
  })

  test('no arguments exits 1 with usage error from cleye', () => {
    const result = Bun.spawnSync(['bun', 'run', cliPath], {
      env: { ...process.env },
    })

    expect(result.exitCode).toBe(1)
    expect(result.stderr.toString()).toContain('Missing required parameter')
  })
})