# Update Workflow

1. Determine whether the target `skills/<name>/` workspace is being created or
   updated, then read every existing target file.
2. Identify the minimal affected scope before editing: a single file (including
   `SKILL.md` only), reference files only, or the full workspace. Leave non-targeted
   files untouched and preserve user customizations in them; a full-workspace request
   still covers only content the request addresses. Keep template-library work
   separate. If scope is ambiguous, ask a focused question before editing.
3. Reconcile `SKILL.md` to the current profile contract: `name`, `description`,
   `selection`, and `class`.
4. Ensure `selection.role`, grouped tags, and any conditions describe the owned
   request rather than implementation history.
5. Remove obsolete routing, registry, scoring, location, version, and
   compatibility guidance instead of translating it into new tags.
6. Run the shared validators and Markdown lint on every changed Markdown file.

Do not silently delete unrelated user content. Record intentional removals and
verify unchanged files remain intact.
