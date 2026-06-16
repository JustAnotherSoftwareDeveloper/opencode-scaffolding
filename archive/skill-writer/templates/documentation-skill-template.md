---
name: <skill-name>
description: Use when creating or researching reference material that other skills will load via delegation for knowledge sharing.
class: documentation
---

# <<Skill Name>> Skill Template (Documentation)

Replace all `<placeholder>` values before using. Match `name` to the directory name exactly.

## Class Purpose

Documentation skills are reference stores with explicit load conditions, freshness policy, citations, and context-budget controls. They provide knowledge that other skills can safely depend on.

## When to Use This Template

- You need to document conventions, policies, or shared knowledge
- Other skills will `load` this via delegation/skill-loading mechanism
  - Content is referenced by multiple workflows
    Information has a definable freshness/currency requirement

## Template Structure

```markdown
---
name: <skill-name>         # Must match directory name, lowercase with hyphens
description: Use when ...  # Trigger for loading this reference material
class: documentation      # Required class declaration
---

# <<Reference Title>>

Brief overview of the documented knowledge area.

## Load Conditions / Context Budget

Specify when and why another skill should load this file:

> **Load when**: <conditions that justify the cost of including this content>

Maximum recommended context contribution: <e.g., "20% of total prompt budget">

## Reference Index

List curated sections or linked reference files. Use when content is organized hierarchically.

- [Section Name](relative-path.md) — Purpose
  
## Freshness Policy / Update Schedule

Define how often this documentation should be reviewed/updated:

| Element | Review Cycle | Owner |
 |---------|--------------|-------|
| Core policy | Quarterly | Team X |
| External links | Monthly check | ... 

## Source Citations

Acknowledge external sources that informed this documentation.

- [Source Title](url) — Used for <specific section/concept>
  
## Gotchas & Recovery

| Problem | Solution |
|---------|----------|
| Outdated link in reference | Run monthly validation script, flag broken links |
```

## Required Frontmatter Fields

- `name` (string): Directory-matched skill identifier, lowercase with hyphens
- `description` (string): Starts with "Use when" describing the trigger condition  
- `class` (enum: documentation): Must be exactly this value for class identification

> **Warning**: This is a template file. Copy it to create actual skills; do not load `templates/documentation-skill-template.md` as an active skill.