---
name: <skill-name>
description: Use when <trigger condition for this single bounded procedure>.
class: atomic
---

# <<Skill Name>> Skill Template (Atomic)

Replace all `<placeholder>` values before using. Match `name` to the directory name exactly.

## Class Purpose

Atomic skills are small, single-objective procedures with bounded inputs, bounded outputs, and independent validation. Each performs one thing well and can be validated in isolation.

## When to Use This Template

- You need a reusable procedure that fits all of:
  - Single objective (one main outcome)
  - Bounded scope (clear start and end states)
  - Independent validation possible

## Template Structure

```markdown
---
name: <skill-name>          # Must match directory name, lowercase alphanumeric with hyphens
description: Use when ...   # Trigger condition for this procedure
class: atomic               # Required class declaration
---

# <<Concrete Skill Name>>

A brief (1-2 sentence) description of what this skill accomplishes.

## When to Use This Skill

Describe the specific circumstances that trigger loading this skill. Start with action-oriented language like "Run this skill when you need to..." or "Use this skill for...".

## Key Steps / Workflow

1. First step...
2. Second step...
3. Final step...

## Validation

Define how success is verified:
- Check that ...
- Verify the output contains ...
- Confirm state matches expected pattern

## Gotchas & Recovery

| Problem | Solution |
|---------|----------|
| Common failure mode 1 | Resolution steps |
```

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: atomic): Must be exactly this value for class identification

> **Warning**: This is a template file. Copy it to create actual skills; do not load `templates/atomic-skill-template.md` as an active skill.