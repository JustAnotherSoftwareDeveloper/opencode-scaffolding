import type { ExitCode } from "./exit-codes.ts";

export function formatViolation(
  filePath: string,
  line: number | null,
  column: number | null,
  ruleId: string,
  message: string,
): string {
  const location = line != null ? `:${line}${column != null ? `:${column}` : ""}` : "";
  return `${filePath}${location}  ${ruleId}  ${message}`;
}

export function die(message: string, code: ExitCode): never {
  process.stderr.write(`${message}\n`);
  return process.exit(code);
}
