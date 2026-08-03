# Gotchas

- **Obsolete frontmatter retained** — Replace the old shape; do not alias it into
  the current profile.
- **Tags describe implementation** — Rewrite them as request-facing actions,
  inputs, outputs, topics, environments, or constraints.
- **Conditions become a second tag list** — Keep `use_when` and `not_for` concise
  and conditional.
- **Template work is mixed into maintenance** — Send template-library changes to
  the separate template workflow.
- **Historical material is treated as active guidance** — Preserve it when
  required, but exclude it from active inventory validation.
- **Only one file is validated** — Validate every active changed file and then the
  full inventory.
