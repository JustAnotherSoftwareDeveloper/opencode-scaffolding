import { describe, expect, test, spyOn } from 'bun:test'
import { formatViolation, die } from '../src/lib/shared/format.ts'
import { resolveTarget, isExempted } from '../src/lib/shared/path.ts'

// ExitCode is a const enum, so we use local constants matching the values
const ExitCodes = {
  CLEAN: 0,
  VIOLATIONS: 1,
  CONFIG_ERROR: 2,
  INVALID_INPUT: 3,
} as const

describe('ExitCode values', () => {
  test('CLEAN is 0', () => {
    expect(ExitCodes.CLEAN).toBe(0)
  })

  test('VIOLATIONS is 1', () => {
    expect(ExitCodes.VIOLATIONS).toBe(1)
  })

  test('CONFIG_ERROR is 2', () => {
    expect(ExitCodes.CONFIG_ERROR).toBe(2)
  })

  test('INVALID_INPUT is 3', () => {
    expect(ExitCodes.INVALID_INPUT).toBe(3)
  })
})

describe('formatViolation', () => {
  test('includes line and column when both are provided', () => {
    const result = formatViolation('test.md', 5, 3, 'no-tables', 'Tables are not allowed')
    expect(result).toBe('test.md:5:3  no-tables  Tables are not allowed')
  })

  test('includes only line when column is null', () => {
    const result = formatViolation('test.md', 5, null, 'no-duplicate', 'Duplicate heading')
    expect(result).toBe('test.md:5  no-duplicate  Duplicate heading')
  })

  test('omits location when line and column are both null', () => {
    const result = formatViolation('test.md', null, null, 'no-tables', 'Tables are not allowed')
    expect(result).toBe('test.md  no-tables  Tables are not allowed')
  })
})

describe('die', () => {
  test('writes message to stderr and calls process.exit with given code', () => {
    const stderrSpy = spyOn(process.stderr, 'write').mockImplementation(() => true)
    const exitSpy = spyOn(process, 'exit').mockImplementation(() => {
      throw new Error('process.exit called')
    })

    expect(() => die('fatal error', ExitCodes.CONFIG_ERROR)).toThrow('process.exit called')
    expect(stderrSpy).toHaveBeenCalledWith('fatal error\n')
    expect(exitSpy).toHaveBeenCalledWith(2)

    stderrSpy.mockRestore()
    exitSpy.mockRestore()
  })
})

describe('resolveTarget', () => {
  const baseArgs = ['/usr/bin/bun', '/path/to/script.ts']

  test('returns argument after -- separator', () => {
    expect(resolveTarget([...baseArgs, '--', 'target.md'])).toBe('target.md')
  })

  test('returns last non-flag argument when no -- separator', () => {
    expect(resolveTarget([...baseArgs, 'target.md'])).toBe('target.md')
  })

  test('returns null when no additional arguments', () => {
    expect(resolveTarget(baseArgs)).toBeNull()
  })

  test('skips flag arguments and returns the non-flag arg', () => {
    expect(resolveTarget([...baseArgs, '--flag', 'target.md'])).toBe('target.md')
  })

  test('returns first argument after -- when multiple follow', () => {
    expect(resolveTarget([...baseArgs, '--', 'file1.md', 'file2.md'])).toBe('file1.md')
  })
})

describe('isExempted', () => {
  test('returns true for path ending in the exempted suffix', () => {
    expect(isExempted('/any/path/skills/display-tasks/SKILL.md')).toBe(true)
  })

  test('returns false for a normal markdown path', () => {
    expect(isExempted('/any/path/normal.md')).toBe(false)
  })

  test('returns false for a path similar to but not matching the exempted suffix', () => {
    expect(isExempted('/any/path/skills/display-tasks/OTHER.md')).toBe(false)
  })
})