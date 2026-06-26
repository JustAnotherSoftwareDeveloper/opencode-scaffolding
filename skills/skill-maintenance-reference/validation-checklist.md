# Validation / Manual Checklist Guidance

Every authored skill must be verified against this checklist before declaring done:

- **Name match**: `name` in frontmatter matches directory under `skills/`.
- **Description prefix**: Starts with `"Use when"`, is specific, and captures trigger intent.
- **Class validity**: One of the six allowed values (planning, documentation, operation, orchestrated, delegated, inline).
- **Original prose**: No text copied from templates or reference files.
- **Body is procedural**: Steps, conditions, decisions.
  Not a tutorial, not a reference (unless class is `documentation`).
- **No examples**: Do not add an examples section or inline example commands.
- **Reference links**: If internal reference files are referenced, they are linked by relative path but their content is not inlined.
- **Valid YAML**: Frontmatter parses without errors.
- **7-section layout (orchestrated only)**: Orchestrated skills use the canonical 7-section layout.
  Verify all seven sections are present and in order.
- **No stale Inline Skills section**: Orchestrated skills must not contain a standalone Inline Skills section.
  Inline work goes into Execution Steps as `Inline:` steps.
- **No Exit Criteria section**: Exit Criteria has been replaced by Verification Checklist.
  Orchestrated skills must not contain an Exit Criteria section.
- **No general breakdown instructions**: Breakdown logic belongs only in `Decompose` step types.
  Do not add free-standing breakdown instructions elsewhere.
- **Operation class**: If class is `operation`, "Normalize Input" is the first procedural step after the H1 intro.
- **Documentation class**: If class is `documentation`, no execution steps or side effects; body is structured reference data only.
- **No Markdown tables in supporting documentation files** (reference/ docs, guides, examples). Tables are only permitted in SKILL.md Output Format sections when the skill's deliverable is a table.

## Planning-Specific Checks

Apply these additional checks when the skill class is `planning`:

- **Frontmatter has `class: planning`** — Must be exactly `planning`.
- **Description starts with `"Use when planning or architecting"`** — Planning descriptions follow this prefix pattern.
- **Minimum sections exist** — At minimum, When to Use and Verification Criteria sections are present.
- **No procedure steps** — Planning skills describe structure, not execution; no imperative procedural steps.
- **No tool invocation instructions** — Planning skills are read-only references; they must not invoke tools.
- **Domain-specific content** — Every section contains domain-specific content, not template scaffolding or placeholder text.
- **Cross-references exist** — If internal reference files are referenced, those files must exist.