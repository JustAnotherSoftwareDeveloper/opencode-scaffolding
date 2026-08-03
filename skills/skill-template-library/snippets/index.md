# Snippets

Store reusable, class-neutral blocks in `snippets/` for use by templates and
generated skills.

- The required profile skeleton uses `name`, `description`, `selection`, and `class`.
- Grouped tags answer what the skill does, consumes, produces, concerns, runs in,
  and refuses.
- `use_when`, `not_for`, and `supports` are semantic profile fields, not
  dispatch instructions or execution steps.
- `snippet-script-invocation.md` and `snippet-node-script-invocation.md` document
  deterministic script invocation for procedure templates.

Class-specific frontmatter examples live in `templates/*.SKILL.template.md`.
The profile contract is indexed in `schemas/index.md`.
- `snippet-script-invocation.md` — Reusable Markdown block for invoking a Python script from a skill.
  Usage: a skill procedure references this snippet when it needs to call a script step.
- `snippet-node-script-invocation.md` — Reusable Markdown block for invoking a Node script (bun run --cwd) from a skill.
  Usage: a skill procedure references this snippet when it needs to call a Node script step.

No external links.
Entries are plain text or code blocks.
