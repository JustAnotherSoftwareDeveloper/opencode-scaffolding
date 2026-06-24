---
name: skill-architect
description: "Use as planning reference for skill class taxonomy, class decision flow, class boundary rules, and platform layout/context."
class: planning
---

# Skill Architect — Skill Architecture Planning Reference

This is a **reference context**, not a procedure runner.
Planning skills must not produce side effects, modify files, invoke tools, or define execution steps.
It answers "what skill classes exist, how to choose one, what boundaries separate them, and how the skills platform is structured."

## Domain Context

- Six skill classes govern all OpenCode skills: `operation`, `delegated`, `inline`, `orchestrated`, `planning`, and `documentation`.
  Each class has a distinct contract for side effects, delegation, and output shape.
- The `planning` and `documentation` classes are passive reference sources.
  They produce no side effects, modify no files, and invoke no tools.
- The `operation`, `delegated`, `inline`, and `orchestrated` classes are active procedure classes.
  They produce side effects and define execution steps.
- Skill selection is driven by the `description` field in frontmatter.
  The `class` field further constrains behavior.
- Skills are stored under `skills/<name>/` with `SKILL.md` as the entry point and supporting files in subdirectories.

## Key Considerations

- Each skill must belong to exactly one class.
  No hybrid classes are supported.
- If the boundary between classes is unclear, trace the proposed skill's contract: does it produce side effects, does it delegate, does it run in a single pass?
- The default class is `operation`.
  Only choose another class when a specific condition clearly applies.
- Cross-skill interaction is represented exclusively through skill loading.
  No skill file may contain a literal path to a file in another skill's directory.
- Scripts are the sole exception to directory confinement.

## Files

- `class-taxonomy.md` — Defines all six skill classes with their contracts, side-effect rules, and template mappings.
- `class-decision-flow.md` — Documents the decision flow for selecting a skill class, from the default `operation` choice through specific alternative conditions.
- `class-boundary-rules.md` — Documents the boundary rules between skill classes and how to disambiguate when a skill's behavior spans multiple classes.
- `platform-layout-context.md` — Documents the filesystem layout for skills, the discovery mechanism, and platform-level rules organized by class.

## Related Skills

- skill-writer: Use when creating or updating all OpenCode skill files under `skills/<name>/` from user requirements and source material.
- skill-factory: Use when executing the actual CREATE/UPDATE workflow for skill directories.
- skill-authoring-guide: Use as documentation reference for authoring style, frontmatter field rules, and progressive disclosure.
- skill-orchestration-reference: Use as documentation reference for orchestrated and delegated worker patterns, collation format, and orchestration usage.
- skill-maintenance-reference: Use as documentation reference for update workflows, migration guides, and validation checklists.
- skill-template-library: Use as documentation reference for all skill templates, schemas, and snippets.

## Cross-References

- `./class-taxonomy.md` — Full definitions of all six skill classes.
- `./class-decision-flow.md` — Decision flow for selecting a skill class.
- `./class-boundary-rules.md` — Boundary disambiguation rules between classes.
- `./platform-layout-context.md` — Platform filesystem layout and discovery rules.

## Docs

This skill is self-contained.
All reference files are listed in the Files section above and reside directly under `skills/skill-architect/`.
No separate `reference/` subdirectory exists.