import { describe, expect, test } from 'bun:test'
import { join } from 'node:path'

const cliPath = join(import.meta.dir, '../src/cli/example.ts')

describe('example CLI', () => {
  test('prints greeting to stdout and exits 0', () => {
    const result = Bun.spawnSync(['bun', 'run', cliPath, 'World'], {
      env: { ...process.env },
    })

    expect(result.exitCode).toBe(0)
    expect(result.stdout.toString().trim()).toBe('Hello from Node scripts, World!')
  })

  test('exits 1 with error message when no name is provided (cleye validation)', () => {
    const result = Bun.spawnSync(['bun', 'run', cliPath], {
      env: { ...process.env },
    })

    expect(result.exitCode).toBe(1)
    expect(result.stderr.toString()).toContain('Missing required parameter')
  })
})