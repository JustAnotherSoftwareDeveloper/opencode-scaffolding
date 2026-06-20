# Skill Writer Style Guide

Editorial conventions for authoring OpenCode skills. This guide governs wording, formatting, structure, and enforcement of the skill-writer output. All skill-authoring work **must** follow this guide.

## How To Use This Guide

- Read this file before writing or reviewing any `SKILL.md`.
- Treat each rule as a pass/fail gate. If a rule cannot be satisfied, flag it (`BLOCKED`) and explain why.
- Refer to `./reference/frontmatter-rules.md` for class taxonomy and platform rules — this guide does not duplicate them.
- This guide applies to `SKILL.md` files only. Support files (`reference/*.md`) may use looser conventions.

## Wording And Verbiage

All rules in this section apply to all body text.

- **Imperative voice** — every sentence is a command or instruction. "Write frontmatter." not "You should write frontmatter."
- **Active voice** — "Select the template." not "The template should be selected."
- **No fluff** — omit "please", "simply", "just", "obviously", "essentially", "basically".
- **Technical precision** — use exact names: `skills/<name>/SKILL.md`, not "the skill file". Use `description` (field), not "description text".
- **Consistent terminology** — choose one term per concept and use it everywhere. Prefer "agent" over "user", "procedure" over "process", "step" over "instruction".
- **No tutorial language** — do not explain concepts, justify choices, or add background. Skill files are imperative references, not training material.

## Formatting

- **Title Case for headings** — "Skill Writer", "Quality Rules", "Validation Checklist". Not "Skill writer", "Quality rules". Applies to `H1` and `H2` headings.
- **One `H1` per file** — the filename's topic. All subsections are `H2` or deeper.
- **YAML frontmatter** — exactly three fields: `name`, `description`, `class`. No extra top-level keys. See `./reference/frontmatter-rules.md` for field rules.
- **Ordered lists for sequential steps** — use `1. 2. 3.`.
- **Bullet lists for unordered items** — use `- `.
- **Flat Markdown** — prefer flat Markdown over tables or complex structures. Use tables only for reference data that genuinely needs row/column alignment. Simple rule-to-scope mappings belong in bullet lists.
- **LLM-readable formatting** — keep Markdown simple so LLMs can parse it reliably. Limit list nesting to two levels. Use short paragraphs (under three sentences). Write one sentence per line. Avoid dense inline formatting.
- **Minimal inline formatting** — use `**bold**` only for rule labels. Use `` `backticks` `` for filenames, paths, and code. Do not bold entire sentences or combine multiple inline styles in a single line.
- **Code fences** — for file paths, YAML blocks, terminal commands, or inline code longer than one word. Use ``` with a language hint.
- **Relative links** — link to support files via `./reference/*.md`, not `/home/user/...` or `reference/*.md` alone.
- **Blank line after headings** — one blank line between a heading and its first body paragraph.
- **No trailing whitespace** — trim all lines.
- **One sentence per line** — hard-wrap after each sentence.

## Conciseness

- **Target length**: under 200 lines for `SKILL.md`. If content exceeds 200 lines, push depth into `./reference/*.md`, `./schemas/`, or `./snippets/`.
- **One idea per sentence**: do not chain clauses with "and", "or", "while".
- **Omit preamble**: start with the first actionable statement. Do not introduce the section or recap prior content.
- **No repeated information**: if a step appears earlier, reference it by number — do not restate it.
- **Prefer lists over paragraphs**: any sequence of conditions, rules, or checks belongs in a list, not a prose paragraph.
- **Delete hedging**: "should", "may", "could", "might", "try", "best", "recommend" — use "must" or omit the qualifier entirely.

## DRY And Progressive Disclosure

- Push detail into `./reference/*.md`, `./schemas/`, or `./snippets/` (prose, rules, gotchas, examples). Keep `SKILL.md` procedural only.
- In `SKILL.md`, use cross-references instead of inlining:
  - "See `./reference/frontmatter-rules.md` for class selection."
  - "See `./templates/<class>.SKILL.template.md` for structure."
- Do **not** inline content from `./reference/*.md` into `SKILL.md`. If a rule belongs in both files, place the authoritative version in a `./reference/*.md` file and reference it.
- If the same rule appears in multiple skill files, extract it into a `./reference/*.md` file.
- Do not copy archived versions — read for shape only, then write original prose.
- Avoid redundant instructions: do not repeat the same instruction across multiple sections, and do not restate one rule with slightly different wording as if it were a new rule.

## Enforcement Checklist

Before declaring a `SKILL.md` complete, verify:

- [ ] All headings use Title Case (no Sentence case, no ALL CAPS).
- [ ] Body uses imperative, active voice throughout.
- [ ] No fluff words, no hedging, no tutorial language.
- [ ] One `H1` per file; all subsections are `H2` or deeper.
- [ ] YAML frontmatter has exactly `name`, `description`, `class`.
- [ ] `description` starts with `"Use when"`.
- [ ] File is under 200 lines.
- [ ] No Examples section present.
- [ ] Reference detail is not inlined — cross-references via `./reference/*.md` instead.
- [ ] No prose copied from archived versions or templates.
- [ ] No redundant instructions — each rule appears once with consistent wording; no restating as new.
- [ ] Relative paths used for cross-file links.
- [ ] Uses plain, LLM-readable Markdown — no tables for simple rule mappings, nesting limited to two levels, minimal inline formatting.
- [ ] One sentence per line; no trailing whitespace.
- [ ] This guide (`./style-guide.md`) was consulted.

## Generated Skill Docs Section

Every generated skill must include a `## Docs` section as the last section of its SKILL.md.
This section lists all supporting files within the skill's own folder as relative links with brief descriptions.

Rules:
- Every file under the skill's folder must be listed: reference/*, templates/*, schemas/*, snippets/*, style-guide.md
- Each entry is a relative link with a one-line description of the file's purpose
- No links to files outside the skill's own folder are permitted
- The section title is exactly `## Docs` with Title Case
- Example:
  - `./reference/frontmatter-rules.md` — Class taxonomy and frontmatter field rules
  - `./templates/operation.SKILL.template.md` — Operation class template
