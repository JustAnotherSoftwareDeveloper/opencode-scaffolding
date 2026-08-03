# Validation Checklist

- `name` matches the skill directory and is a canonical lowercase hyphenated name.
- `description` is a trimmed single-line trigger statement.
- Required top-level metadata is exactly `name`, `description`, `selection`, and
  `class`, unless a supported optional profile field is explicitly needed.
- `selection.role` is valid and `selection.tags` has at least one non-empty
  supported group.
- Tag arrays and condition arrays are unique, trimmed, bounded strings;
  `supports` contains canonical names and excludes the current skill.
- No `schema_version`, `cues`, `relationships`, `facets`, `routing`, `location`,
  `score`, `rank`, or `threshold` remains in active metadata.
- The profile distinguishes owned, neighboring, paraphrased, unrelated, and
  low-overlap requests without ranking or scoring instructions.
- Run both shared validators on each changed active skill:

```sh
node scripts/validate-skills.js skills/<name>/SKILL.md
uv run --directory scripts/python python -m cli.validate_skill_md skills/<name>/SKILL.md
```

- Run Markdown lint on every changed Markdown file and validate the full active
  inventory before release.
