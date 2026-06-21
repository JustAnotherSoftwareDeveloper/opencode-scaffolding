# Skill Writer — Reference Documents

Reference documents organized by domain module.
Each file covers one topic for progressive disclosure from SKILL.md.

## Authoring

Files related to skill authoring conventions, frontmatter rules, and content structure.

- [authoring-style.md](./authoring/authoring-style.md) — Editorial conventions and pass/fail gates for writing SKILL.md files.
- [frontmatter-rules.md](./authoring/frontmatter-rules.md) — Frontmatter field rules, class taxonomy, and platform-level constraints for skill files.
- [progressive-disclosure.md](./authoring/progressive-disclosure.md) — Principle of keeping SKILL.md compact and pushing depth into reference files.
- [trigger-eval.md](./authoring/trigger-eval.md) — Guidance on composing skill descriptions for accurate positive and near-miss trigger matching.

## Orchestration

Files related to orchestrated skills, worker dispatch, and result collation.

- [orchestrated-usage.md](./orchestration/orchestrated-usage.md) — Reference for authors filling the 7-section orchestrated skill template.
- [worker-patterns.md](./orchestration/worker-patterns.md) — Contract and design patterns for delegated workers dispatched by orchestrated skills.
- [collation-reference.md](./orchestration/collation-reference.md) — Default JSON collation format for aggregating worker results in orchestrated skills.

## Platform

Files related to the platform context and skill discovery.

- [platform-context.md](./platform/platform-context.md) — Where skills live in the filesystem and how the agent discovers and loads them.

## Maintenance

Files related to maintenance workflows, migrations, validation, and common pitfalls.

- [update-workflow.md](./maintenance/update-workflow.md) — Reference material for the UPDATE path, including mode determination and change detection.
- [migration-from-old-template.md](./maintenance/migration-from-old-template.md) — Section mapping guide for converting orchestrated skills to the canonical 7-section layout.
- [validation-checklist.md](./maintenance/validation-checklist.md) — Manual checklist for verifying every authored skill before declaring it done.
- [gotchas.md](./maintenance/gotchas.md) — Common pitfalls and anti-patterns encountered when authoring OpenCode skills.
