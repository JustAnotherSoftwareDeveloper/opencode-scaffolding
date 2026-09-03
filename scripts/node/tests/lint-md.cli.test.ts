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
const fixturesDir = join(import.meta.dir, 'fixtures', 'proposal-workspaces')

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

  test('nonexistent path exits 3 with error message', () => {
    const result = Bun.spawnSync(
      ['bun', 'run', cliPath, '--', '/nonexistent/path/file.md'],
      { env: { ...process.env } },
    )

    expect(result.exitCode).toBe(3)
    expect(result.stderr.toString()).toContain('path not found')
  })

  test('no arguments exits 1 with usage error from cleye', () => {
    const result = Bun.spawnSync(['bun', 'run', cliPath], {
      env: { ...process.env },
    })

    expect(result.exitCode).toBe(1)
    expect(result.stderr.toString()).toContain('Missing required parameter')
  })

  test('valid proposal workspace exits 0', () => {
    const result = Bun.spawnSync(
      ['bun', 'run', cliPath, '--', join(fixturesDir, 'valid-short')],
      { env: { ...process.env } },
    )

    expect(result.exitCode).toBe(0)
    expect(result.stderr.toString()).toBe('')
  })

  test('valid complex proposal workspace exits 0', () => {
    const result = Bun.spawnSync(
      ['bun', 'run', cliPath, '--', join(fixturesDir, 'valid-complex')],
      { env: { ...process.env } },
    )

    expect(result.exitCode).toBe(0)
    expect(result.stderr.toString()).toBe('')
  })

  test('proposal workspace with violations exits 1', () => {
    const result = Bun.spawnSync(
      ['bun', 'run', cliPath, '--', join(fixturesDir, 'missing-heading')],
      { env: { ...process.env } },
    )

    expect(result.exitCode).toBe(1)
    expect(result.stderr.toString()).toContain('Missing required H2 heading')
  })

  test('proposal workspace reports aggregated diagnostics on stderr', () => {
    const result = Bun.spawnSync(
      ['bun', 'run', cliPath, '--', join(fixturesDir, 'invalid-toc')],
      { env: { ...process.env } },
    )

    expect(result.exitCode).toBe(1)
    const stderr = result.stderr.toString()
    expect(stderr).toContain('TOC')
  })

  test('generic file rejects tables', () => {
    withTempDir((dir) => {
      const filePath = join(dir, 'with-table.md')
      writeFileSync(
        filePath,
        '# Heading\n\n| A | B |\n|---|---|\n| 1 | 2 |\n',
      )

      const result = Bun.spawnSync(['bun', 'run', cliPath, '--', filePath], {
        env: { ...process.env },
      })

      expect(result.exitCode).toBe(1)
      expect(result.stderr.toString()).toContain('no-tables')
    })
  })

  test('proposal workspace accepts tables', () => {
    withTempDir((dir) => {
      const proposalPath = join(dir, 'PROPOSAL.md')
      const sourcePath = join(dir, 'src.md')
      writeFileSync(
        proposalPath,
        [
          '---',
          'title: Tables Allowed',
          'slug: tables-allowed',
          'created: 2025-01-01',
          'created-at: 2025-01-01T00:00:00Z',
          'status: draft',
          'readiness: not-ready',
          'decision-owner: tester',
          'source-documents:',
          '  - src.md',
          '---',
          '',
          '## Table of Contents',
          '',
          '- [Recommendation](#recommendation)',
          '- [Technical Rationale](#technical-rationale)',
          '- [Questions](#questions)',
          '- [Options Considered](#options-considered)',
          '- [Implementation Details](#implementation-details)',
          '- [Verification Criteria](#verification-criteria)',
          '- [Sources](#sources)',
          '',
          '## Recommendation',
          '',
          '| Col A | Col B |',
          '|-------|-------|',
          '| a     | b     |',
          '',
          '## Technical Rationale',
          '',
          'Tables are fine in proposals.',
          '',
          '## Questions',
          '',
          'None.',
          '',
          '## Options Considered',
          '',
          'One option.',
          '',
          '## Implementation Details',
          '',
          'Simple.',
          '',
          '## Verification Criteria',
          '',
          'Passes.',
          '',
          '## Sources',
          '',
          '- [Source](src.md)',
        ].join('\n'),
      )
      writeFileSync(sourcePath, '# Source')

      const result = Bun.spawnSync(['bun', 'run', cliPath, '--', dir], {
        env: { ...process.env } },
      )

      expect(result.exitCode).toBe(0)
    })
  })
})