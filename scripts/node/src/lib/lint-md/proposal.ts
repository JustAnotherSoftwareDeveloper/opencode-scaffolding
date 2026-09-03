import { existsSync, lstatSync, readFileSync, readdirSync, realpathSync, statSync } from "node:fs";
import { isAbsolute, join, relative, resolve } from "node:path";
import type { Heading, Root } from "mdast";
import { remark } from "remark";
import { parse as parseYaml } from "yaml";
import type { LintResult, Violation } from "./core.ts";

export const PROPOSAL_RULE_IDS = {
  MISSING_PROPOSAL: "proposal/missing-proposal",
  PROPOSAL_UNSAFE_SYMLINK: "proposal/proposal-unsafe-symlink",
  INVALID_YAML: "proposal/invalid-yaml",
  MISSING_FRONTMATTER_FIELD: "proposal/missing-frontmatter-field",
  INVALID_READINESS: "proposal/invalid-readiness",
  MISSING_STATUS: "proposal/missing-status",
  INVALID_H2_ORDER: "proposal/invalid-h2-order",
  DUPLICATE_HEADING: "proposal/duplicate-heading",
  TOC_MISSING_ENTRY: "proposal/toc-missing-entry",
  TOC_STALE_ENTRY: "proposal/toc-stale-entry",
  TOC_SELF_LINK: "proposal/toc-self-link",
  TOC_WRONG_ORDER: "proposal/toc-wrong-order",
  TOC_DUPLICATE_ENTRY: "proposal/toc-duplicate-entry",
  SOURCE_DOC_UNSAFE_PATH: "proposal/source-document-unsafe-path",
  SOURCE_DOC_MISSING_IN_SOURCES: "proposal/source-document-missing-in-sources",
  SOURCE_DOC_FILE_MISSING: "proposal/source-document-file-missing",
  SOURCE_DOC_NOT_REGULAR: "proposal/source-document-not-regular",
  SOURCE_DOC_UNSAFE_SYMLINK: "proposal/source-document-unsafe-symlink",
  SOURCE_DOC_DUPLICATE: "proposal/source-document-duplicate",
  SOURCE_INDEX_EXTRA: "proposal/source-index-extra",
  SOURCE_INDEX_DUPLICATE: "proposal/source-index-duplicate",
  RELATIVE_LINK_BROKEN: "proposal/relative-link-broken",
  RELATIVE_LINK_UNSAFE: "proposal/relative-link-unsafe",
  UNRESOLVED_PLACEHOLDER: "proposal/unresolved-placeholder",
  PUBLICATION_COMMENT: "proposal/publication-comment",
  LEGACY_ARTIFACT: "proposal/legacy-artifact",
} as const;

const REQUIRED_FRONTMATTER_FIELDS = [
  "title",
  "slug",
  "created",
  "created-at",
  "status",
  "readiness",
  "decision-owner",
  "source-documents",
] as const;

const VALID_READINESS = ["not-ready", "review-ready", "decision-ready"] as const;
const REQUIRED_H2S = [
  "Table of Contents",
  "Recommendation",
  "Technical Rationale",
  "Questions",
  "Options Considered",
  "Implementation Details",
  "Verification Criteria",
  "Sources",
] as const;
const LEGACY_ROOT_ARTIFACT =
  /^(?:0[1-9]-.+|10-implementation\.md|11-supporting-sources\.md|implementation\.md|INDEX\.md|metadata\.md)$/i;

interface HeadingInfo {
  text: string;
  depth: number;
  line: number;
}

interface TocEntry {
  label: string;
  anchor: string;
  line: number;
}

interface MarkdownLink {
  target: string;
  line: number;
}

function violation(
  filePath: string,
  ruleId: string,
  message: string,
  line: number | null = null,
): Violation {
  return { filePath, line, column: null, ruleId, message };
}

function isInside(path: string, root: string): boolean {
  const value = relative(root, path);
  return value === "" || (!value.startsWith("..") && !isAbsolute(value));
}

function normalizeRelativePath(value: string): string | null {
  let decoded: string;
  try {
    decoded = decodeURIComponent(value.split("#", 1)[0].trim());
  } catch {
    return null;
  }
  if (!decoded || decoded.startsWith("#")) return null;
  if (/^[a-z][a-z0-9+.-]*:/i.test(decoded) || decoded.startsWith("//")) return null;
  const normalized = decoded.replace(/\\/g, "/").replace(/^\.\//, "");
  if (
    isAbsolute(normalized) ||
    /^[A-Za-z]:/.test(normalized) ||
    normalized.split("/").includes("..")
  ) {
    return "";
  }
  return normalized;
}

function nodeText(node: unknown): string {
  if (!node || typeof node !== "object") return "";
  const record = node as { value?: unknown; children?: unknown[] };
  if (typeof record.value === "string") return record.value;
  return Array.isArray(record.children) ? record.children.map(nodeText).join("") : "";
}

function extractHeadings(root: Root): HeadingInfo[] {
  return root.children
    .filter((child): child is Heading => child.type === "heading")
    .map((heading) => ({
      text: nodeText(heading).trim(),
      depth: heading.depth,
      line: heading.position?.start.line ?? 0,
    }));
}

function headingToAnchor(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

function sectionText(content: string, heading: string): { text: string; line: number } | null {
  const lines = content.split("\n");
  const start = lines.findIndex((line) => line.trim() === `## ${heading}`);
  if (start === -1) return null;
  let end = lines.length;
  for (let i = start + 1; i < lines.length; i++) {
    if (/^##\s+/.test(lines[i])) {
      end = i;
      break;
    }
  }
  return { text: lines.slice(start + 1, end).join("\n"), line: start + 1 };
}

function extractLinks(text: string, startLine = 1): MarkdownLink[] {
  const links: MarkdownLink[] = [];
  const pattern = /!?\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g;
  for (const [index, line] of text.split("\n").entries()) {
    pattern.lastIndex = 0;
    for (let match = pattern.exec(line); match; match = pattern.exec(line)) {
      links.push({ target: match[1], line: startLine + index });
    }
  }
  return links;
}

function parseFrontmatter(content: string): {
  data: Record<string, unknown> | null;
  line: number;
  error: string | null;
} {
  const lines = content.split("\n");
  if (lines[0]?.trim() !== "---") {
    return { data: null, line: 1, error: null };
  }
  const end = lines.findIndex((line, index) => index > 0 && line.trim() === "---");
  if (end === -1) return { data: null, line: 1, error: "Frontmatter has no closing delimiter" };
  try {
    const parsed = parseYaml(lines.slice(1, end).join("\n"));
    return {
      data: parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : null,
      line: 1,
      error:
        parsed && typeof parsed === "object" && !Array.isArray(parsed)
          ? null
          : "Frontmatter must be a mapping",
    };
  } catch (error) {
    return {
      data: null,
      line: 1,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

function withoutFrontmatter(content: string): string {
  const lines = content.split("\n");
  if (lines[0]?.trim() !== "---") return content;
  const end = lines.findIndex((line, index) => index > 0 && line.trim() === "---");
  if (end === -1) return content;
  return lines.map((line, index) => (index <= end ? "" : line)).join("\n");
}

function validateSourceFile(
  workspace: string,
  source: string,
  filePath: string,
  line: number,
): Violation[] {
  const violations: Violation[] = [];
  const target = resolve(workspace, source);
  if (!isInside(target, workspace)) {
    return [
      violation(
        filePath,
        PROPOSAL_RULE_IDS.SOURCE_DOC_UNSAFE_PATH,
        `source-documents entry "${source}" escapes the workspace`,
        line,
      ),
    ];
  }
  if (!existsSync(target)) {
    return [
      violation(
        filePath,
        PROPOSAL_RULE_IDS.SOURCE_DOC_FILE_MISSING,
        `source-documents entry "${source}" does not resolve to an existing file`,
        line,
      ),
    ];
  }
  const info = lstatSync(target);
  if (info.isSymbolicLink()) {
    const real = realpathSync(target);
    if (!isInside(real, workspace)) {
      violations.push(
        violation(
          filePath,
          PROPOSAL_RULE_IDS.SOURCE_DOC_UNSAFE_SYMLINK,
          `source-documents entry "${source}" resolves outside the workspace`,
          line,
        ),
      );
      return violations;
    }
  }
  if (!statSync(target).isFile()) {
    violations.push(
      violation(
        filePath,
        PROPOSAL_RULE_IDS.SOURCE_DOC_NOT_REGULAR,
        `source-documents entry "${source}" is not a regular file`,
        line,
      ),
    );
  }
  return violations;
}

export async function lintProposalWorkspace(dirPath: string): Promise<LintResult> {
  const workspace = resolve(dirPath);
  const proposalPath = join(workspace, "PROPOSAL.md");
  const violations: Violation[] = [];

  if (!existsSync(proposalPath)) {
    return {
      filePath: proposalPath,
      violations: [
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.MISSING_PROPOSAL,
          "Proposal workspace must contain a regular PROPOSAL.md file",
        ),
      ],
    };
  }
  const proposalInfo = lstatSync(proposalPath);
  if (proposalInfo.isSymbolicLink()) {
    return {
      filePath: proposalPath,
      violations: [
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.PROPOSAL_UNSAFE_SYMLINK,
          "Proposal workspace must not use a symbolic link for PROPOSAL.md",
        ),
      ],
    };
  }
  if (!proposalInfo.isFile()) {
    return {
      filePath: proposalPath,
      violations: [
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.MISSING_PROPOSAL,
          "Proposal workspace must contain a regular PROPOSAL.md file",
        ),
      ],
    };
  }

  const content = readFileSync(proposalPath, "utf-8");
  const parsedFrontmatter = parseFrontmatter(content);
  if (parsedFrontmatter.error) {
    violations.push(
      violation(
        proposalPath,
        PROPOSAL_RULE_IDS.INVALID_YAML,
        `Invalid proposal frontmatter: ${parsedFrontmatter.error}`,
        parsedFrontmatter.line,
      ),
    );
  }
  const frontmatter = parsedFrontmatter.data;
  if (!frontmatter) {
    violations.push(
      violation(
        proposalPath,
        PROPOSAL_RULE_IDS.MISSING_FRONTMATTER_FIELD,
        "Valid YAML frontmatter delimited by --- is required",
        1,
      ),
    );
  } else {
    for (const field of REQUIRED_FRONTMATTER_FIELDS) {
      const value = frontmatter[field];
      if (!(field in frontmatter) || value === null || value === "") {
        violations.push(
          violation(
            proposalPath,
            PROPOSAL_RULE_IDS.MISSING_FRONTMATTER_FIELD,
            `Missing required frontmatter field: ${field}`,
            1,
          ),
        );
      }
    }
    if (
      typeof frontmatter.readiness !== "string" ||
      !VALID_READINESS.includes(frontmatter.readiness as (typeof VALID_READINESS)[number])
    ) {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.INVALID_READINESS,
          `Readiness must be one of: ${VALID_READINESS.join(", ")}`,
          1,
        ),
      );
    }
    if (typeof frontmatter.status !== "string" || !frontmatter.status.trim()) {
      violations.push(
        violation(proposalPath, PROPOSAL_RULE_IDS.MISSING_STATUS, "Status must not be empty", 1),
      );
    }
  }

  const headings = extractHeadings(remark().parse(withoutFrontmatter(content)) as Root);
  const h2s = headings.filter((heading) => heading.depth === 2);
  const h2Names = h2s.map((heading) => heading.text);
  const seenHeadings = new Set<string>();
  for (const heading of h2s) {
    if (seenHeadings.has(heading.text)) {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.DUPLICATE_HEADING,
          `Duplicate H2 heading: "${heading.text}"`,
          heading.line,
        ),
      );
    }
    seenHeadings.add(heading.text);
  }

  for (const required of REQUIRED_H2S) {
    if (!h2Names.includes(required)) {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.INVALID_H2_ORDER,
          `Missing required H2 heading: "${required}"`,
        ),
      );
    }
  }
  const requiredPositions = REQUIRED_H2S.map((heading) => h2Names.indexOf(heading));
  if (
    requiredPositions.every((position) => position >= 0) &&
    requiredPositions.some(
      (position, index) => index > 0 && position < requiredPositions[index - 1],
    )
  ) {
    violations.push(
      violation(
        proposalPath,
        PROPOSAL_RULE_IDS.INVALID_H2_ORDER,
        "Required H2 headings are not in canonical order",
      ),
    );
  }
  const questions = h2Names.indexOf("Questions");
  const options = h2Names.indexOf("Options Considered");
  for (const heading of h2s) {
    if (!REQUIRED_H2S.includes(heading.text as (typeof REQUIRED_H2S)[number])) {
      const index = h2Names.indexOf(heading.text);
      if (questions === -1 || options === -1 || index <= questions || index >= options) {
        violations.push(
          violation(
            proposalPath,
            PROPOSAL_RULE_IDS.INVALID_H2_ORDER,
            `Optional H2 "${heading.text}" must appear between Questions and Options Considered`,
            heading.line,
          ),
        );
      }
    }
  }

  const toc = sectionText(content, "Table of Contents");
  const tocLinks = toc ? extractLinks(toc.text, toc.line + 1) : [];
  const tocEntries: TocEntry[] = tocLinks
    .filter((link) => link.target.startsWith("#"))
    .map((link) => ({ label: link.target, anchor: link.target.slice(1), line: link.line }));
  const tocSeen = new Set<string>();
  for (const entry of tocEntries) {
    if (tocSeen.has(entry.anchor)) {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.TOC_DUPLICATE_ENTRY,
          `TOC anchor "#${entry.anchor}" appears more than once`,
          entry.line,
        ),
      );
    }
    tocSeen.add(entry.anchor);
    if (entry.anchor === "table-of-contents") {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.TOC_SELF_LINK,
          "Table of Contents must not link to itself",
          entry.line,
        ),
      );
    }
    if (!headings.some((heading) => headingToAnchor(heading.text) === entry.anchor)) {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.TOC_STALE_ENTRY,
          `TOC anchor "#${entry.anchor}" does not match a heading`,
          entry.line,
        ),
      );
    }
  }
  const expectedTocAnchors = h2s
    .filter((heading) => heading.text !== "Table of Contents")
    .map((heading) => headingToAnchor(heading.text));
  for (const anchor of expectedTocAnchors) {
    if (!tocEntries.some((entry) => entry.anchor === anchor)) {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.TOC_MISSING_ENTRY,
          `H2 anchor "#${anchor}" is missing from the Table of Contents`,
          toc?.line ?? null,
        ),
      );
    }
  }
  const actualTocH2Order = tocEntries
    .map((entry) => entry.anchor)
    .filter((anchor) => expectedTocAnchors.includes(anchor));
  if (
    actualTocH2Order.length === expectedTocAnchors.length &&
    actualTocH2Order.some((anchor, index) => anchor !== expectedTocAnchors[index])
  ) {
    violations.push(
      violation(
        proposalPath,
        PROPOSAL_RULE_IDS.TOC_WRONG_ORDER,
        "Table of Contents H2 entries are not in document order",
        toc?.line ?? null,
      ),
    );
  }

  if (/\{\{[^{}]+\}\}/.test(content)) {
    violations.push(
      violation(
        proposalPath,
        PROPOSAL_RULE_IDS.UNRESOLVED_PLACEHOLDER,
        "Published proposal contains an unresolved template placeholder",
      ),
    );
  }
  if (/<!--[\s\S]*?-->/.test(content)) {
    violations.push(
      violation(
        proposalPath,
        PROPOSAL_RULE_IDS.PUBLICATION_COMMENT,
        "Published proposal contains an authoring comment",
      ),
    );
  }
  for (const entry of readdirSync(workspace, { withFileTypes: true })) {
    if (entry.isFile() && LEGACY_ROOT_ARTIFACT.test(entry.name)) {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.LEGACY_ARTIFACT,
          `Legacy authored artifact is not allowed: ${entry.name}`,
        ),
      );
    }
  }

  const sourceSection = sectionText(content, "Sources");
  const indexedSources = sourceSection
    ? extractLinks(sourceSection.text, sourceSection.line + 1)
        .map((link) => ({ ...link, normalized: normalizeRelativePath(link.target) }))
        .filter((link): link is MarkdownLink & { normalized: string } => Boolean(link.normalized))
    : [];
  const indexedCounts = new Map<string, number>();
  for (const source of indexedSources) {
    indexedCounts.set(source.normalized, (indexedCounts.get(source.normalized) ?? 0) + 1);
  }

  const declaredSources = frontmatter?.["source-documents"];
  const declared = new Set<string>();
  if (!Array.isArray(declaredSources)) {
    violations.push(
      violation(
        proposalPath,
        PROPOSAL_RULE_IDS.MISSING_FRONTMATTER_FIELD,
        "source-documents must be an array of safe relative paths",
        1,
      ),
    );
  } else {
    if (declaredSources.length === 0) {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.MISSING_FRONTMATTER_FIELD,
          "source-documents must contain at least one copied source path",
          1,
        ),
      );
    }
    for (const [index, value] of declaredSources.entries()) {
      if (typeof value !== "string") {
        violations.push(
          violation(
            proposalPath,
            PROPOSAL_RULE_IDS.SOURCE_DOC_UNSAFE_PATH,
            `source-documents entry at index ${index} is not a string`,
            1,
          ),
        );
        continue;
      }
      const normalized = normalizeRelativePath(value);
      if (!normalized) {
        violations.push(
          violation(
            proposalPath,
            PROPOSAL_RULE_IDS.SOURCE_DOC_UNSAFE_PATH,
            `source-documents entry "${value}" is not a safe relative path`,
            1,
          ),
        );
        continue;
      }
      if (declared.has(normalized)) {
        violations.push(
          violation(
            proposalPath,
            PROPOSAL_RULE_IDS.SOURCE_DOC_DUPLICATE,
            `source-documents entry "${normalized}" is duplicated`,
            1,
          ),
        );
      }
      declared.add(normalized);
      violations.push(...validateSourceFile(workspace, normalized, proposalPath, 1));
      if (!indexedCounts.has(normalized)) {
        violations.push(
          violation(
            proposalPath,
            PROPOSAL_RULE_IDS.SOURCE_DOC_MISSING_IN_SOURCES,
            `source-documents entry "${normalized}" is missing from Sources`,
            sourceSection?.line ?? null,
          ),
        );
      }
    }
  }
  for (const [source, count] of indexedCounts) {
    if (count > 1) {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.SOURCE_INDEX_DUPLICATE,
          `Sources contains duplicate internal entry "${source}"`,
          sourceSection?.line ?? null,
        ),
      );
    }
    if (!declared.has(source)) {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.SOURCE_INDEX_EXTRA,
          `Sources contains undeclared internal entry "${source}"`,
          sourceSection?.line ?? null,
        ),
      );
    }
  }

  for (const link of extractLinks(content)) {
    if (link.target.startsWith("#")) continue;
    const normalized = normalizeRelativePath(link.target);
    if (normalized === null) continue;
    if (normalized === "") {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.RELATIVE_LINK_UNSAFE,
          `Relative link "${link.target}" escapes the workspace`,
          link.line,
        ),
      );
      continue;
    }
    const target = resolve(workspace, normalized);
    if (!isInside(target, workspace) || !existsSync(target)) {
      violations.push(
        violation(
          proposalPath,
          PROPOSAL_RULE_IDS.RELATIVE_LINK_BROKEN,
          `Relative link "${link.target}" does not resolve inside the workspace`,
          link.line,
        ),
      );
    }
  }

  return { violations, filePath: proposalPath };
}
