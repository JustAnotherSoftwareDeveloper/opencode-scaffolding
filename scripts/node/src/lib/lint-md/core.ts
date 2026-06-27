import { readFileSync } from "node:fs";
import { remark } from "remark";
import remarkGfm from "remark-gfm";
import remarkLint from "remark-lint";
import remarkLintNoDuplicateHeadings from "remark-lint-no-duplicate-headings";
import remarkLintNoHeadingPunctuation from "remark-lint-no-heading-punctuation";
import { noTablesPlugin } from "./rules.ts";

export interface Violation {
  filePath: string;
  line: number | null;
  column: number | null;
  ruleId: string;
  message: string;
}

export interface LintResult {
  violations: Violation[];
  filePath: string;
}

/**
 * Lint a markdown file using the remark ecosystem.
 * Reads the file, runs the configured remark pipeline, and collects violations.
 * Throws on read/processing errors.
 */
export async function lintFile(filePath: string): Promise<LintResult> {
  const fileContent = readFileSync(filePath, "utf-8");

  const result = await remark()
    .use(remarkGfm)
    .use(remarkLint)
    .use(noTablesPlugin)
    .use(remarkLintNoDuplicateHeadings)
    .use(remarkLintNoHeadingPunctuation)
    .process(fileContent);

  const violations: Violation[] = result.messages.map((msg) => ({
    filePath,
    line: msg.line ?? null,
    column: msg.column ?? null,
    ruleId: typeof msg.ruleId === "string" ? msg.ruleId : "unknown",
    message: msg.message,
  }));

  return { violations, filePath };
}
