# Update Workflow

In `skills/<name>/`, replace `<name>` with the canonical `name` of the skill being
maintained.

1. Determine whether `skills/<name>/` is new or being updated. If it already exists,
   read every file in the workspace before editing.
2. Identify the minimal scope before editing: one file (including only `SKILL.md`),
   reference files only, or the full workspace. Leave non-targeted files untouched
   and preserve user customizations in them. A full-workspace request still covers
   only content the request addresses. Keep template-library work separate. If scope
   is ambiguous, ask a focused question before editing.
3. Reconcile `SKILL.md` to the current profile contract: `name`, `description`,
   `selection`, and `class`.
4. Ensure `selection.role`, grouped tags, and any conditions describe the
   request the skill owns, not its implementation history.
5. Remove obsolete routing, registry, scoring, location, version, and compatibility
   guidance; do not translate it into new tags.
6. Run the shared validators and Markdown lint on every changed Markdown file.

Do not silently delete unrelated user content. Record intentional removals and verify
unchanged files remain intact.
