---
name: validate-skill-framework
description: Use when validating OpenCode skill artifacts against the skill-hygiene framework schema requirements.
class: operation
---

# Validate Skill Framework Skill (Operation)

Validates a SKILL.md file for proper frontmatter structure, required fields, and basic syntax compliance with the skill-hygiene conventions.

## When to Use This Skill

Run this skill when you need to verify that an OpenCode skill artifact follows framework requirements before committing or sharing it with other practitioners. This is typically done after authoring a new `SKILL.md` file at `skills/<name>/SKILL.md`.

## Key Steps / Workflow

1. **Identify target skill**: Determine the path to the SKILL.md file (e.g., `skills/my-skill/SKILL.md`)
2. **Execute validation**: Run `uv run --project scripts/python validate-skill-framework <path-to-skill>`
3. **Review output**: Check for frontmatter errors, missing required fields, or schema violations
4. **Fix issues**: Correct any flagged problems in the SKILL.md file (name must match directory, description must start with "Use when", class must be valid)
5. **Re-validate**: Run validation again to confirm all issues are resolved

## Validation Checklist

- [ ] Frontmatter YAML block is present and properly formatted
- [ ] `name` field matches the skill's parent directory name exactly (lowercase, hyphens)
- [ ] `description` starts with "Use when" followed by trigger condition
- [ ] `class` value is one of: operation, delegated, or planning
- [ ] No tabs found in YAML frontmatter block

## Example Usage

```bash
uv run --project scripts/python validate-skill-framework skills/skill-writer/SKILL.md
# Expected output: "Validation passed for skills/skill-writer/SKILL.md"
```

## Gotchas & Recovery

| Problem | Solution |
|---------|----------|
| Validation fails on name mismatch | Rename file or adjust frontmatter `name` to match directory exactly |
| YAML parsing error | Ensure no tabs in the frontmatter block; use spaces for indentation only |
