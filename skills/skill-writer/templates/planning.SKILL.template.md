---
name: <<skill-name>>
description: "Use as planning reference for <<domain>>."
class: planning
---

# <<Skill Name>> — Domain Planning Reference

Replace all `<<placeholder>>` items below.
This template captures planning context for a single domain.
It is a **reference context**, not a procedure runner.
Planning skills must not produce side effects, modify files, invoke tools, or define execution steps.
See `./reference/authoring/frontmatter-rules.md` for class rules and frontmatter requirements.

## Domain Context

<<Capture structural knowledge about the domain: API architecture, testing setup, code architecture, data flow, deployment topology. Use 2-5 bullet points or short paragraphs.>>

## Key Considerations

<<Capture domain-specific constraints, assumptions, trade-offs, non-goals, and known limitations. Use 2-5 bullet points.>>
<<Explain what the domain boundary does not include and why.>>

## Common Workflows

For each common planning workflow in this domain, create a workflow file using [`./common-workflow.md`](./common-workflow.md), then list it below using the format: name - optional skill - description:

- <<workflow-name>> - <<optional skill>> - <<quick description>>
- <<workflow-name>> - <<optional skill>> - <<quick description>>
- <<workflow-name>> - <<optional skill>> - <<quick description>>

## Related Skills

- <<skill-name>>: <<one-sentence description of when to use this skill>>
- <<skill-name>>: <<one-sentence description of when to use this skill>>
This is for quick reference during planning.

## Cross-References

- `./reference/authoring/frontmatter-rules.md` — Frontmatter rules and class selection for planning skills.
- `./common-workflow.md` — Workflow file template used by the Common Workflows section.
- `./reference/authoring/authoring-style.md` — Authoring conventions and cross-reference guidelines.
- `./orchestration/orchestrated-usage.md` — Orchestration patterns relevant to planning multi-step workflows.