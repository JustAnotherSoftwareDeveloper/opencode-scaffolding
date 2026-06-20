# Platform Context: Where Skills Live

- **Skill root**: `./` (the skill's base directory)
- **Entry point**: `SKILL.md` — the file the agent loads
- **Support files**: `reference/*.md`, `templates/`, `schemas/`, `snippets/`
- **Archived versions**: `<archive>/<name>/SKILL.md` — read for shape only, never prose
- **Templates**: `./templates/<class>.SKILL.template.md` — e.g. `operation.SKILL.template.md`, `delegated.SKILL.template.md`, `inline.SKILL.template.md`, `orchestrated.SKILL.template.md`, `planning.SKILL.template.md`
- **Schemas**: `./schemas/class-contract.example.json` (JSON Schema) and `./schemas/class-contract.example.xsd` (XSD) — example class contract schemas

**Discovery**: The OpenCode agent selects a skill when its `description` field (in frontmatter) matches the current task context. Skill files are not auto-indexed beyond their description field — the match is string/relevance-based, not structural.
