import { remark } from 'remark'
import remarkGfm from 'remark-gfm'
import remarkLint from 'remark-lint'
import remarkLintNoDuplicateHeadings from 'remark-lint-no-duplicate-headings'
import remarkLintNoHeadingPunctuation from 'remark-lint-no-heading-punctuation'
import { readFileSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'
import { visit } from 'unist-util-visit'
import type { Root, Table } from 'mdast'
import type { VFile } from 'vfile'

const EXEMPTED_PATH = 'skills/display-tasks/SKILL.md'

const enum ExitCode {
  CLEAN = 0,
  VIOLATIONS = 1,
  CONFIG_ERROR = 2,
  INVALID_INPUT = 3,
}

function getTargetPath(argv: string[]): string | null {
  const dashDashIndex = argv.indexOf('--')
  if (dashDashIndex !== -1 && dashDashIndex + 1 < argv.length) {
    return argv[dashDashIndex + 1]
  }
  for (let i = argv.length - 1; i >= 2; i--) {
    if (!argv[i].startsWith('-')) {
      return argv[i]
    }
  }
  return null
}

function isExempted(resolvedPath: string): boolean {
  return resolvedPath.endsWith(EXEMPTED_PATH)
}

function formatViolation(filePath: string, line: number | null, column: number | null, ruleId: string, message: string): string {
  const location = line != null ? `:${line}` + (column != null ? `:${column}` : '') : ''
  return `${filePath}${location}  ${ruleId}  ${message}`
}

function die(message: string, code: ExitCode): never {
  process.stderr.write(message + '\n')
  process.exit(code)
}

/**
 * Inline remark-lint plugin that rejects any table nodes.
 * Replaces the unavailable npm package `remark-lint-no-tables`.
 */
function noTablesPlugin(_options: void) {
  const transformer = (tree: Root, file: VFile): void => {
    visit(tree, 'table', (node: Table) => {
      file.message('Tables are not allowed', node, 'no-tables')
    })
  }
  return transformer
}

async function main(): Promise<void> {
  const targetPath = getTargetPath(process.argv)

  if (!targetPath) {
    die('Error: no target file specified. Usage: bun src/lint-md.ts -- <target-file>', ExitCode.INVALID_INPUT)
  }

  const resolvedPath = resolve(targetPath)

  if (!existsSync(resolvedPath)) {
    die(`Error: file not found: ${resolvedPath}`, ExitCode.INVALID_INPUT)
  }

  if (isExempted(resolvedPath)) {
    process.exit(ExitCode.CLEAN)
  }

  let fileContent: string
  try {
    fileContent = readFileSync(resolvedPath, 'utf-8')
  } catch {
    die(`Error: unable to read file: ${resolvedPath}`, ExitCode.CONFIG_ERROR)
  }

  let result
  try {
    result = await remark()
      .use(remarkGfm)
      .use(remarkLint)
      .use(noTablesPlugin)
      .use(remarkLintNoDuplicateHeadings)
      .use(remarkLintNoHeadingPunctuation)
      .process(fileContent)
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    die(`Error: remark processing failed: ${message}`, ExitCode.CONFIG_ERROR)
  }

  const messages = result.messages

  if (messages.length === 0) {
    process.exit(ExitCode.CLEAN)
  }

  for (const msg of messages) {
    const ruleId = typeof msg.ruleId === 'string' ? msg.ruleId : 'unknown'
    process.stderr.write(
      formatViolation(resolvedPath, msg.line ?? null, msg.column ?? null, ruleId, msg.message) + '\n',
    )
  }

  process.exit(ExitCode.VIOLATIONS)
}

await main()