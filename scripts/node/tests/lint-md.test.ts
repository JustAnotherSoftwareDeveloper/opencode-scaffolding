import { describe, expect, test } from 'bun:test'
import {
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { lintDirectory, lintFile } from '../src/lib/lint-md/core.ts'

async function withTempDir(fn: (dir: string) => Promise<void>): Promise<void> {
  const dir = mkdtempSync(join(tmpdir(), 'lint-md-test-'))
  try {
    await fn(dir)
  } finally {
    rmSync(dir, { recursive: true, force: true })
  }
}

const fixturesDir = join(import.meta.dir, 'fixtures', 'proposal-workspaces')

const {
  MISSING_FRONTMATTER_FIELD,
  INVALID_READINESS,
  MISSING_STATUS,
  INVALID_H2_ORDER,
  DUPLICATE_HEADING,
  TOC_MISSING_ENTRY,
  TOC_STALE_ENTRY,
  TOC_SELF_LINK,
  TOC_WRONG_ORDER,
  SOURCE_DOC_UNSAFE_PATH,
  SOURCE_DOC_MISSING_IN_SOURCES,
  SOURCE_DOC_FILE_MISSING,
  SOURCE_DOC_DUPLICATE,
  UNRESOLVED_PLACEHOLDER,
  LEGACY_ARTIFACT,
  MISSING_PROPOSAL,
  INVALID_YAML,
  PUBLICATION_COMMENT,
  RELATIVE_LINK_BROKEN,
  SOURCE_INDEX_EXTRA,
  SOURCE_INDEX_DUPLICATE,
  SOURCE_DOC_UNSAFE_SYMLINK,
  SOURCE_DOC_NOT_REGULAR,
  PROPOSAL_UNSAFE_SYMLINK,
} = {
  MISSING_FRONTMATTER_FIELD: 'proposal/missing-frontmatter-field',
  INVALID_READINESS: 'proposal/invalid-readiness',
  MISSING_STATUS: 'proposal/missing-status',
  INVALID_H2_ORDER: 'proposal/invalid-h2-order',
  DUPLICATE_HEADING: 'proposal/duplicate-heading',
  TOC_MISSING_ENTRY: 'proposal/toc-missing-entry',
  TOC_STALE_ENTRY: 'proposal/toc-stale-entry',
  TOC_SELF_LINK: 'proposal/toc-self-link',
  TOC_WRONG_ORDER: 'proposal/toc-wrong-order',
  SOURCE_DOC_UNSAFE_PATH: 'proposal/source-document-unsafe-path',
  SOURCE_DOC_MISSING_IN_SOURCES: 'proposal/source-document-missing-in-sources',
  SOURCE_DOC_FILE_MISSING: 'proposal/source-document-file-missing',
  SOURCE_DOC_DUPLICATE: 'proposal/source-document-duplicate',
  UNRESOLVED_PLACEHOLDER: 'proposal/unresolved-placeholder',
  LEGACY_ARTIFACT: 'proposal/legacy-artifact',
  MISSING_PROPOSAL: 'proposal/missing-proposal',
  INVALID_YAML: 'proposal/invalid-yaml',
  PUBLICATION_COMMENT: 'proposal/publication-comment',
  RELATIVE_LINK_BROKEN: 'proposal/relative-link-broken',
  SOURCE_INDEX_EXTRA: 'proposal/source-index-extra',
  SOURCE_INDEX_DUPLICATE: 'proposal/source-index-duplicate',
  SOURCE_DOC_UNSAFE_SYMLINK: 'proposal/source-document-unsafe-symlink',
  SOURCE_DOC_NOT_REGULAR: 'proposal/source-document-not-regular',
  PROPOSAL_UNSAFE_SYMLINK: 'proposal/proposal-unsafe-symlink',
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

describe('lintDirectory (proposal workspace)', () => {
  test('valid-short returns no violations', async () => {
    const result = await lintDirectory(join(fixturesDir, 'valid-short'))
    expect(result.violations).toHaveLength(0)
  })

  test('valid-complex with domain H2s returns no violations', async () => {
    const result = await lintDirectory(join(fixturesDir, 'valid-complex'))
    expect(result.violations).toHaveLength(0)
  })

  test('missing-heading returns invalid-h2-order', async () => {
    const result = await lintDirectory(join(fixturesDir, 'missing-heading'))
    expect(result.violations.length).toBeGreaterThan(0)
    const missingH2s = result.violations.filter((v) =>
      v.message.includes('Missing required H2 heading'),
    )
    expect(missingH2s.length).toBeGreaterThan(0)
    expect(missingH2s.every((v) => v.ruleId === INVALID_H2_ORDER)).toBe(true)
  })

  test('invalid-toc returns toc-stale-entry and toc-self-link', async () => {
    const result = await lintDirectory(join(fixturesDir, 'invalid-toc'))
    const ruleIds = result.violations.map((v) => v.ruleId)
    expect(ruleIds).toContain(TOC_SELF_LINK)
    expect(ruleIds).toContain(TOC_STALE_ENTRY)
  })

  test('legacy-layout rejects numbered proposal files', async () => {
    const result = await lintDirectory(join(fixturesDir, 'legacy-layout'))
    expect(result.violations.some((v) => v.ruleId === LEGACY_ARTIFACT)).toBe(true)
  })

  test('invalid-frontmatter returns missing-frontmatter-field', async () => {
    const result = await lintDirectory(join(fixturesDir, 'invalid-frontmatter'))
    expect(result.violations.length).toBeGreaterThan(0)
    const fmViolations = result.violations.filter(
      (v) => v.ruleId === MISSING_FRONTMATTER_FIELD,
    )
    expect(fmViolations.length).toBeGreaterThan(0)
  })

  test('missing-source returns source-document-missing-in-sources', async () => {
    const result = await lintDirectory(join(fixturesDir, 'missing-source'))
    const ruleIds = result.violations.map((v) => v.ruleId)
    expect(ruleIds).toContain(SOURCE_DOC_MISSING_IN_SOURCES)
  })

  test('broken-link returns source-document-file-missing', async () => {
    const result = await lintDirectory(join(fixturesDir, 'broken-link'))
    const ruleIds = result.violations.map((v) => v.ruleId)
    expect(ruleIds).toContain(SOURCE_DOC_FILE_MISSING)
  })

  test('placeholder content is rejected', async () => {
    const result = await lintDirectory(join(fixturesDir, 'placeholder'))
    expect(result.violations.some((v) => v.ruleId === UNRESOLVED_PLACEHOLDER)).toBe(true)
  })

  test('duplicate-source returns source-document-duplicate', async () => {
    const result = await lintDirectory(join(fixturesDir, 'duplicate-source'))
    const ruleIds = result.violations.map((v) => v.ruleId)
    expect(ruleIds).toContain(SOURCE_DOC_DUPLICATE)
  })

  test('directory without PROPOSAL.md is rejected', async () => {
    await withTempDir(async (dir) => {
      const result = await lintDirectory(dir)
      expect(result.violations.some((v) => v.ruleId === MISSING_PROPOSAL)).toBe(true)
    })
  })

  test('malformed YAML is a stable workspace violation', async () => {
    await withTempDir(async (dir) => {
      writeFileSync(join(dir, 'PROPOSAL.md'), '---\ntitle: [broken\n---\n')
      const result = await lintDirectory(dir)
      expect(result.violations.some((v) => v.ruleId === INVALID_YAML)).toBe(true)
    })
  })

  test('publication comments are rejected', async () => {
    await withTempDir(async (dir) => {
      const content = readFileSync(join(fixturesDir, 'valid-short', 'PROPOSAL.md'), 'utf8')
      writeFileSync(join(dir, 'PROPOSAL.md'), content.replace('## Recommendation', '<!-- remove me -->\n\n## Recommendation'))
      writeFileSync(join(dir, 'source.md'), '# Source\n')
      const result = await lintDirectory(dir)
      expect(result.violations.some((v) => v.ruleId === PUBLICATION_COMMENT)).toBe(true)
    })
  })

  test('an empty Table of Contents is rejected', async () => {
    await withTempDir(async (dir) => {
      const content = readFileSync(join(fixturesDir, 'valid-short', 'PROPOSAL.md'), 'utf8')
      writeFileSync(
        join(dir, 'PROPOSAL.md'),
        content.replace(/## Table of Contents[\s\S]*?## Recommendation/, '## Table of Contents\n\n## Recommendation'),
      )
      writeFileSync(join(dir, 'source.md'), '# Source\n')
      const result = await lintDirectory(dir)
      expect(result.violations.some((v) => v.ruleId === TOC_MISSING_ENTRY)).toBe(true)
    })
  })

  test('broken non-source relative links are rejected', async () => {
    await withTempDir(async (dir) => {
      const content = readFileSync(join(fixturesDir, 'valid-short', 'PROPOSAL.md'), 'utf8')
      writeFileSync(
        join(dir, 'PROPOSAL.md'),
        content.replace(
          'Adopt the proposal workflow for all planning tasks.',
          'Adopt the [proposal workflow](./missing.md) for all planning tasks.',
        ),
      )
      writeFileSync(join(dir, 'source.md'), '# Source\n')
      const result = await lintDirectory(dir)
      expect(result.violations.some((v) => v.ruleId === RELATIVE_LINK_BROKEN)).toBe(true)
    })
  })

  test('undeclared and duplicate internal Sources entries are rejected', async () => {
    await withTempDir(async (dir) => {
      const content = readFileSync(join(fixturesDir, 'valid-short', 'PROPOSAL.md'), 'utf8')
      writeFileSync(join(dir, 'PROPOSAL.md'), `${content}\n- [Duplicate](./source.md)\n- [Extra](./extra.md)\n`)
      writeFileSync(join(dir, 'source.md'), '# Source\n')
      writeFileSync(join(dir, 'extra.md'), '# Extra\n')
      const result = await lintDirectory(dir)
      expect(result.violations.some((v) => v.ruleId === SOURCE_INDEX_DUPLICATE)).toBe(true)
      expect(result.violations.some((v) => v.ruleId === SOURCE_INDEX_EXTRA)).toBe(true)
    })
  })

  test('source symlinks escaping the workspace are rejected', async () => {
    await withTempDir(async (dir) => {
      const content = readFileSync(join(fixturesDir, 'valid-short', 'PROPOSAL.md'), 'utf8')
      writeFileSync(join(dir, 'PROPOSAL.md'), content)
      symlinkSync('/etc/hosts', join(dir, 'source.md'))
      const result = await lintDirectory(dir)
      expect(result.violations.some((v) => v.ruleId === SOURCE_DOC_UNSAFE_SYMLINK)).toBe(true)
    })
  })

  test('a symlinked PROPOSAL.md is rejected even when its target is valid', async () => {
    await withTempDir(async (dir) => {
      const fixtureProposal = join(fixturesDir, 'valid-short', 'PROPOSAL.md')
      writeFileSync(join(dir, 'source.md'), '# Source\n')
      symlinkSync(fixtureProposal, join(dir, 'PROPOSAL.md'))
      const result = await lintDirectory(dir)
      expect(result.violations.some((v) => v.ruleId === PROPOSAL_UNSAFE_SYMLINK)).toBe(true)
    })
  })

  test('inline YAML source manifests do not become Markdown headings', async () => {
    await withTempDir(async (dir) => {
      const content = readFileSync(join(fixturesDir, 'valid-short', 'PROPOSAL.md'), 'utf8')
      writeFileSync(
        join(dir, 'PROPOSAL.md'),
        content.replace('source-documents:\n  - source.md', 'source-documents: [source.md]'),
      )
      writeFileSync(join(dir, 'source.md'), '# Source\n')
      const result = await lintDirectory(dir)
      expect(result.violations).toHaveLength(0)
    })
  })

  test('an empty source-documents manifest is rejected', async () => {
    await withTempDir(async (dir) => {
      const content = readFileSync(join(fixturesDir, 'valid-short', 'PROPOSAL.md'), 'utf8')
      writeFileSync(
        join(dir, 'PROPOSAL.md'),
        content.replace('source-documents:\n  - source.md', 'source-documents: []\n'),
      )
      const result = await lintDirectory(dir)
      expect(result.violations.some((v) => v.ruleId === MISSING_FRONTMATTER_FIELD)).toBe(true)
    })
  })

  test('source paths must resolve to regular files', async () => {
    await withTempDir(async (dir) => {
      const content = readFileSync(join(fixturesDir, 'valid-short', 'PROPOSAL.md'), 'utf8')
      writeFileSync(join(dir, 'PROPOSAL.md'), content)
      mkdirSync(join(dir, 'source.md'))
      const result = await lintDirectory(dir)
      expect(result.violations.some((v) => v.ruleId === SOURCE_DOC_NOT_REGULAR)).toBe(true)
    })
  })
})
