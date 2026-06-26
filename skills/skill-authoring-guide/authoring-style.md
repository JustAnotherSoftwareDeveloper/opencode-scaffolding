# Skill Authoring Guide Style

Editorial conventions for authoring OpenCode skill documentation.
This guide governs wording, formatting, structure, and enforcement of the skill-authoring-guide output.
All skill-authoring documentation work **must** follow this guide.

## How To Use This Guide

- Read this file before writing or reviewing any `SKILL.md`.
- Treat each rule as a pass/fail gate.
  If a rule cannot be satisfied, flag it (`BLOCKED`).
  Explain why.
- Refer to `./frontmatter-rules.md` for frontmatter field definitions.
  This guide does not duplicate them.
- This guide applies to ALL markdown files under the `skills/skill-authoring-guide/` directory tree.
- **Named exceptions**: No exceptions apply.
  All files in this skill are strict.
  Within reference files, sentences that define facts (rule definitions, format specifications, file inventories — not procedures) may use declarative voice.
  All other content remains strict imperative.

## Wording And Verbiage

All rules in this section apply to all body text.

- **Imperative voice** — every sentence is a command or instruction (except factual definitions in reference files, which may use declarative voice). "Write frontmatter." not "You should write frontmatter."
- **Active voice** — "Select the template." not "The template should be selected."
- **No fluff** — omit "please", "simply", "just", "obviously", "essentially", "basically".
- **Technical precision** — use exact names: `skills/<name>/SKILL.md`, not "the skill file".
  Use `description` (field), not "description text".
- **Consistent terminology** — choose one term per concept and use it everywhere.
  Prefer "agent" over "user", "procedure" over "process", "step" over "instruction".
- **No tutorial language** — do not explain concepts, justify choices, or add background.
  Skill files are imperative references, not training material.

## Formatting

- **Title Case for headings** — "Skill Authoring Guide", "Quality Rules", "Validation Checklist".
  Not "Skill authoring guide", "Quality rules".
  Applies to `H1` and `H2` headings.
- **One `H1` per file** — the filename's topic.
  All subsections are `H2` or deeper.
- **YAML frontmatter** — exactly three fields: `name`, `description`, `class`.
  No extra top-level keys.
  See `./frontmatter-rules.md` for field rules.
- **Ordered lists for sequential steps** — use `1. 2. 3.`.
- **Bullet lists for unordered items** — use `- `.
- **Flat Markdown** — Do not use Markdown tables in skill supporting documentation (reference files, READMEs, guides, examples).
  Use bullet lists, definition lists, or subsection headings instead.
  **Exception:** Tables are permitted only in SKILL.md Output Format sections where the skill's deliverable is itself a table (e.g., display-tasks).
  Tables in reference/ and other supporting docs are never permitted.
- **LLM-readable formatting** — keep Markdown simple so LLMs can parse it reliably.
  Limit list nesting to two levels.
  Use short paragraphs (under three sentences).
  Write one sentence per line.
  Avoid dense inline formatting.
- **Minimal inline formatting** — use `**bold**` only for rule labels.
  Use `` `backticks` `` for filenames, paths, and code.
  Do not bold entire sentences or combine multiple inline styles in a single line.
- **Code fences** — for file paths, YAML blocks, terminal commands, or inline code longer than one word.
  Use ``` with a language hint.
- **Relative links** — link to support files via `./<file>.md`, not `/home/user/...` or `<file>.md` alone.
- **Blank line after headings** — one blank line between a heading and its first body paragraph.
- **No trailing whitespace** — trim all lines.
- **One sentence per line** — hard-wrap after each sentence.

## Conciseness

- **Target length**: under 200 lines for `SKILL.md`.
  If content exceeds 200 lines, push depth into standalone reference files.
- **One idea per sentence**: do not chain clauses with "and", "or", "while".
- **Omit preamble**: start with the first actionable statement.
  Do not introduce the section or recap prior content.
- **No repeated information**: if a step appears earlier, reference it by number — do not restate it.
- **Prefer lists over paragraphs**: any sequence of conditions, rules, or checks belongs in a list, not a prose paragraph.
- **Delete hedging**: "should", "may", "could", "might", "try", "best", "recommend" — use "must" or omit the qualifier entirely.

## DRY And Progressive Disclosure

- Push detail into standalone reference files (prose, rules, gotchas, examples).
  Keep `SKILL.md` an index only.
- In `SKILL.md`, use cross-references instead of inlining:
  - "See `./frontmatter-rules.md` for frontmatter field definitions."
  - "See `./trigger-evaluation.md` for trigger evaluation rules."
- Do **not** inline content from reference files into `SKILL.md`.
  If a rule belongs in both files, place the authoritative version in a reference file and reference it.
- Inline authoring hints are permitted when they improve readability without bloating SKILL.md.
  The rule against inlining reference detail still applies to substantial content, but brief inline guidance (1-2 sentences) may remain in SKILL.md.
- If the same rule appears in multiple skill files, extract it into a reference file.
- Avoid redundant instructions.
  Do not repeat the same instruction across multiple sections.
  Do not restate one rule with slightly different wording as if it were a new rule.

## Enforcement Checklist

Before declaring any skill-authoring-guide markdown file complete, verify these checks.

**Headings:**
- [ ] All headings use Title Case (no Sentence case, no ALL CAPS)
- [ ] One `H1` per file; all subsections are `H2` or deeper

**Voice:**
- [ ] Step descriptions begin with an imperative verb
- [ ] No passive-voice constructions in step bodies ("is used", "should be", "must be done")
- [ ] Sentences are commands, not observations (except factual definitions in reference files, which may use declarative voice)

**Word choice:**
- [ ] No hedging words ("should", "may", "could", "might", "try", "best", "recommend") in instructions — use "must" or omit the qualifier
- [ ] No fluff words ("please", "simply", "just", "obviously", "essentially", "basically")
- [ ] No tutorial language — no concept explanations, no background justifications, no choice rationales

**Reference discipline:**
- [ ] Reference detail is not inlined — cross-references via `./<file>.md` instead
- [ ] Relative paths used for cross-file links

**Formatting:**
- [ ] One sentence per line
- [ ] No trailing whitespace
- [ ] Do not use Markdown tables in supporting documentation — only permitted in SKILL.md Output Format sections where deliverable is a table
- [ ] List nesting limited to two levels
- [ ] Minimal inline formatting — no bold entire sentences, no combined inline styles on one line

**Conciseness:**
- [ ] File is under 200 lines

**Cross-reference:**
- [ ] This guide (`./authoring-style.md`) was consulted