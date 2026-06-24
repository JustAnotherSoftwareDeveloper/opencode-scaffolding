# Update Workflow Reference

Reference material for the UPDATE path when editing existing skill directories.

### Mode Determination

- **CREATE**: `skills/<name>/` does not exist.
  Produce a new skill directory from scratch.
- **UPDATE**: `skills/<name>/` exists.
  Edit one or more files in the existing directory.

### Determining What Changed

- Compare the user request against the current state of every file under `skills/<name>/`.
- Read full current content of each targeted file before applying edits — never assume content.
- Identify the minimal set of sections, paragraphs, or lines that the request affects.
- If the request is open-ended ("update to match new conventions"), audit every section against the latest SKILL.md structure and any applicable reference files before editing.

### Preserving Existing Content During Targeted Edits

- Keep frontmatter, structure, and prose outside the edit scope intact.
- Only modify sections that the request explicitly targets.
- When updating SKILL.md, do not rewrite internal reference files unless they are listed as targets.
- Preserve user additions to reference files (gotchas, custom conventions) when updating core files.
- If a request targets a single file, leave all other files untouched.

### Partial Update Scope Boundaries

A request can target only a subset of the skill directory:

- **SKILL.md only** — Update procedure, quality rules, validation checklist.
  Leave reference files untouched.
- **Reference files only** — Update internal reference files (e.g., `gotchas.md`, `migration-guide.md`).
  Leave SKILL.md untouched.
- **Full directory update** — Update all files.
  In this case, still preserve existing content that the request does not address.

When scope is ambiguous, ask: "Update only SKILL.md? Only reference files? Entire skill directory?"

### Content Integrity Rules

- Never silently delete content — every removal must be intentional and justified by the request.
- Preserve user customizations in reference files when updating SKILL.md.
- When adding new reference sections, do not duplicate content already in SKILL.md.
- If the request requires removing content, state the removal explicitly in the edit.
- Verify after each edit that unchanged sections still render as expected.

### Update-Mode Decision Prompts

When in UPDATE mode, decide scope before editing:

- **Request targets only SKILL.md procedure or structure?** → Edit SKILL.md only.
  Do not touch reference files.
- **Request targets only reference content?** → Edit only reference files.
  Leave SKILL.md untouched.
- **Request is ambiguous about scope?** → Clarify before editing.
  Do not assume full directory scope.