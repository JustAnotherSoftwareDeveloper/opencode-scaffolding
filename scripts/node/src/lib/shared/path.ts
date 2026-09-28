import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

export const EXEMPTED_PATH = "skills/display-tasks/SKILL.md";

const REPOSITORY_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../../../..");

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
  return resolve(resolvedPath) === resolve(REPOSITORY_ROOT, EXEMPTED_PATH);
}
