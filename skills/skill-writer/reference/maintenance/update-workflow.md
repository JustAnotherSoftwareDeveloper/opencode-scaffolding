# Update Workflow Reference

Reference material for the UPDATE path. Complements the procedural UPDATE steps in `SKILL.md`.

### Mode Determination

- **CREATE**: `skills/<name>/` does not exist. Produce a new skill directory from scratch.
- **UPDATE**: `skills/<name>/` exists. Edit one or more files in the existing directory.

### Determining What Changed

- Compare the user request against the current state of every file under `skills/<name>/`.
- Read full current content of each targeted file before applying edits — never assume content.
- Identify the minimal set of sections, paragraphs, or lines that the request affects.
- If the request is open-ended ("update to match new conventions"), audit every section against the latest `SKILL.md` structure before editing.

### Preserving Existing Content During Targeted Edits

- Keep frontmatter, structure, and prose outside the edit scope intact.
- Only modify sections that the request explicitly targets.
- When updating `SKILL.md`, do not rewrite reference files under `reference/` or `reference/authoring/authoring-style.md` unless they are listed as targets.
- Preserve user additions to reference files (gotchas, custom conventions) when updating core files.
- If a request targets a single file, leave all other files untouched.

### Partial Update Scope Boundaries

A request may target only a subset of the skill directory:

- **SKILL.md only** — Update procedure, quality rules, validation checklist. Leave reference files and reference/authoring/authoring-style.md untouched.
- **Reference files only** — Update files under `reference/`. Leave SKILL.md and templates untouched.
- **Templates only** — Update template files. Leave other files untouched.
- **Full directory update** — Update all files. In this case, still preserve existing content that the request does not address.

When scope is ambiguous, ask: "Update only SKILL.md? Only reference files? Entire skill directory?"

### Content Integrity Rules

- Never silently delete content — every removal must be intentional and justified by the request.
- Preserve user customizations in reference/ files and reference/authoring/authoring-style.md when updating SKILL.md.
- When adding new reference sections, do not duplicate content already in SKILL.md.
- If the request requires removing content, state the removal explicitly in the edit.
- Verify after each edit that unchanged sections still render as expected.

### Update-Mode Decision Prompts

When in UPDATE mode, decide scope before editing:

- **Request targets only SKILL.md procedure or structure?** → Edit SKILL.md only. Do not touch reference files, reference/authoring/authoring-style.md, or templates.
- **Request targets only reference content (reference/*)?** → Edit only reference files. Leave SKILL.md and templates untouched.
- **Request adds or modifies templates?** → Edit only template files. Leave other files untouched.
- **Request is a full directory rework?** → Update all files, but preserve any content the request does not explicitly address.
- **Request is ambiguous about scope?** → Clarify before editing. Do not assume full directory scope.
