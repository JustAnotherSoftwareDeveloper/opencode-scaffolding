# Skill Factory Create And Update Workflow

Use this workflow for the current direct-selection profile only. Template-library
content is maintained separately and is not part of this operation.

## Create

1. Identify the skill name, owned request, class, inputs, outputs, and nearest
   neighboring skills.
2. Write frontmatter with exactly the required profile fields: `name`,
   `description`, `selection`, and `class`.
3. Set `selection.role` to `owner`, `support`, or `reference`, then add only the
   grouped tags that change a selection decision.
4. Add `use_when`, `not_for`, and `supports` only when they express request-facing
   conditions or a directional support relationship.
5. Write the body for the selected class. Keep implementation instructions in the
   body, not in profile tags.
6. Validate the completed file with the shared validator and Markdown checks.

## Update

1. Read every existing file in the target skill directory before editing.
2. Preserve content outside the requested change.
3. Re-derive the affected profile from the owned request and nearest neighbors.
4. Replace obsolete metadata with the current profile shape; do not carry forward
   routing, registry, scoring, location, version, or compatibility migration data.
5. Update affected examples and evaluation cases together with the profile.
6. Run the shared validator on every changed `SKILL.md`, then run Markdown lint.

## Current profile contract

- Required top-level fields are `name`, `description`, `selection`, and `class`.
- `selection` requires `role` and at least one non-empty grouped tag list.
- Supported tag groups are `actions`, `inputs`, `outputs`, `topics`,
  `environments`, and `constraints`.
- `use_when`, `not_for`, and `supports` are optional; arrays contain unique,
  trimmed strings, and `supports` contains canonical skill names other than the
  current skill.
- Do not add `schema_version`, `cues`, `relationships`, `facets`, `routing`,
  `location`, `score`, `rank`, or `threshold`.

## Validation checkpoint

Run the repository's shared validators against each changed skill file:

```sh
node scripts/validate-skills.js skills/<name>/SKILL.md
uv run --project scripts/python python -m cli.validate_skill_md skills/<name>/SKILL.md
```

Both validators must pass. The active skill class must have numbered execution
steps; planning and documentation classes must not.
