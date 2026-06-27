import { resolve } from "node:path";

export const EXEMPTED_PATH = "skills/display-tasks/SKILL.md";

export function resolveTarget(argv: string[]): string | null {
  const dashDashIndex = argv.indexOf("--");
  if (dashDashIndex !== -1 && dashDashIndex + 1 < argv.length) {
    return argv[dashDashIndex + 1];
  }
  for (let i = argv.length - 1; i >= 2; i--) {
    if (!argv[i].startsWith("-")) {
      return argv[i];
    }
  }
  return null;
}

export function isExempted(resolvedPath: string): boolean {
  return resolvedPath.endsWith(EXEMPTED_PATH);
}
