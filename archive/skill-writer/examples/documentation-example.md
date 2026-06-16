---
name: skill-hygiene-reference
description: Use when creating or researching reference material that other skills will load via delegation for knowledge sharing.
class: documentation
---

> **Note**: This is an illustrative example of a documentation-class skill that `skill-writer` can help you author. It demonstrates proper structure but is not loaded as a live runtime artifact by other skills. See the `templates/` directory for copy-and-customize templates, and the main SKILL.md for instructions on creating new skills.

# Skill Hygiene Reference Store

Reference material documenting OpenCode skill framework conventions, loaded by the `skill-writer` and related orchestration skills during artifact creation workflows.

## Load Conditions / Context Budget

> **Load when**: A skill or runbook needs guidance on creating new SKILL.md artifacts following framework hygiene standards, specifically for validation rules, frontmatter requirements, or class taxonomy selection.

Maximum recommended context contribution: 25% of total prompt budget (this document focuses on structural conventions rather than deep reference)

## Reference Index

- [Class Selection Guide](reference/class-selection.md) — Decision matrix for choosing skill class
- [Authoring Workflow Checklist](reference/authoring-workflow.md) — Step-by-step authoring process
- [Template Library](templates/) — Copy-and-customize templates for each skill class

## Freshness Policy / Update Schedule

| Element | Review Cycle | Owner |
|---------|--------------|-------|
| Frontmatter validation rules | With framework releases | skill-hygiene maintainers |
| Class taxonomy definitions | Annual or as needed | OpenCode core team |
| Template examples | Quarterly review | skill-writer maintainers |

## Source Citations

- [OpenCode Skill Framework Schema]( Skills directory) — Used for frontmatter field definitions and class enumeration values
- [.skillwriter conventions] — Adapted for atomic/orchestrated/documentation/planning taxonomy patterns

## Gotchas & Recovery

| Problem | Solution |
|---------|----------|
| Outdated link in reference | Run quarterly validation: `uv run --project scripts/python validate-links skills/skill-writer/reference/` |