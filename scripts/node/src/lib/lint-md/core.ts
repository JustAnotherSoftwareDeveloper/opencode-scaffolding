import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { remark } from "remark";
import remarkGfm from "remark-gfm";
import remarkLint from "remark-lint";
import remarkLintNoDuplicateHeadings from "remark-lint-no-duplicate-headings";
import remarkLintNoHeadingPunctuation from "remark-lint-no-heading-punctuation";
import { lintProposalWorkspace } from "./proposal.ts";
import type { LintProfile } from "./rules.ts";
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

function buildPipeline() {
  return remark()
    .use(remarkGfm)
    .use(remarkLint)
    .use(noTablesPlugin)
    .use(remarkLintNoDuplicateHeadings)
    .use(remarkLintNoHeadingPunctuation);
}

/**
 * Lint a markdown file using the remark ecosystem.
 * Reads the file, runs the configured remark pipeline, and collects violations.
 * Throws on read/processing errors.
 */
export async function lintFile(
  filePath: string,
  _profile: LintProfile = "generic",
): Promise<LintResult> {
  const fileContent = readFileSync(filePath, "utf-8");

  const pipeline = buildPipeline();
  const result = await pipeline.process(fileContent);

  const violations: Violation[] = result.messages.map((msg) => ({
    filePath,
    line: msg.line ?? null,
    column: msg.column ?? null,
    ruleId: typeof msg.ruleId === "string" ? msg.ruleId : "unknown",
    message: msg.message,
  }));

  return { violations, filePath };
}

/**
 * Lint a proposal workspace directory.
 * Looks for PROPOSAL.md and runs the proposal workspace validator.
 * Falls back to no violations if the directory is not a proposal workspace.
 */
export async function lintDirectory(dirPath: string): Promise<LintResult> {
  const workspaceResult = await lintProposalWorkspace(dirPath);
  const proposalPath = join(dirPath, "PROPOSAL.md");
  if (!existsSync(proposalPath)) return workspaceResult;
  const markdownResult = await lintFile(proposalPath, "proposal");
  return {
    filePath: proposalPath,
    violations: [...markdownResult.violations, ...workspaceResult.violations],
  };
}
