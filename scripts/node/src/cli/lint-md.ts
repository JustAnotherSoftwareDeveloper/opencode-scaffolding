import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { cli } from "cleye";
import { type LintResult, lintFile } from "../lib/lint-md/core.ts";
import { ExitCode } from "../lib/shared/exit-codes.ts";
import { die, formatViolation } from "../lib/shared/format.ts";
import { isExempted, resolveTarget } from "../lib/shared/path.ts";

cli({
  name: "lint-md",
  version: "1.0.0",
  parameters: ["<input-path>"],
});

async function main(): Promise<void> {
  const targetPath = resolveTarget(process.argv);

  if (!targetPath) {
    die(
      "Error: no target file specified. Usage: bun run --cwd scripts/node lint:md -- <target-file>",
      ExitCode.INVALID_INPUT,
    );
  }

  const resolvedPath = resolve(targetPath);

  if (!existsSync(resolvedPath)) {
    die(`Error: file not found: ${resolvedPath}`, ExitCode.INVALID_INPUT);
  }

  if (isExempted(resolvedPath)) {
    process.exit(ExitCode.CLEAN);
  }

  let result: LintResult;
  try {
    result = await lintFile(resolvedPath);
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    die(`Error: lint processing failed: ${message}`, ExitCode.CONFIG_ERROR);
  }

  const { violations } = result;

  if (violations.length === 0) {
    process.exit(ExitCode.CLEAN);
  }

  for (const v of violations) {
    process.stderr.write(`${formatViolation(v.filePath, v.line, v.column, v.ruleId, v.message)}\n`);
  }

  process.exit(ExitCode.VIOLATIONS);
}

await main();
