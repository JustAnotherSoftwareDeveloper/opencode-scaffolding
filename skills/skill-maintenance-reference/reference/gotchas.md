# Gotchas

- **Obsolete frontmatter is retained** — Replace it with the current `name`,
  `description`, `selection`, and `class` fields; do not preserve the old shape as
  compatibility data.
- **Tags describe implementation** — Rewrite them as request-facing actions,
  inputs, outputs, topics, environments, or constraints.
- **Conditions become a second tag list** — Keep `use_when` and `not_for` concise
  and conditional.
- **Template work is mixed into maintenance** — Send template-library changes to
  the separate template workflow.
- **Historical material is treated as active guidance** — Preserve it when
  required, but exclude it from active inventory validation.
- **Only one file is validated** — Validate every changed active skill, lint every
  changed Markdown file, and then validate the full active inventory.
