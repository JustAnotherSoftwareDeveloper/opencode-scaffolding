---
name: <<skill-name>>
description: "Use as planning reference for <<domain>>."
class: planning
---

# `<<Skill Name>>` — Domain Planning Reference

> **Editorial constraint:** Do not use Markdown tables when filling this template. Use bullet lists, definition lists, or subsection headings for structured data.

Replace all `<<placeholder>>` items below.
This template captures planning context for a single domain.
It is a **reference context**, not a procedure runner.
Planning skills must not produce side effects, modify files, invoke tools, or define execution steps.

## Domain Context

<<Capture structural knowledge about the domain: API architecture, testing setup, code architecture, data flow, deployment topology. Use 2-5 bullet points or short paragraphs.>>

## Key Considerations

<<Capture domain-specific constraints, assumptions, trade-offs, non-goals, and known limitations. Use 2-5 bullet points.>>
`<<Explain what the domain boundary does not include and why.>>`

## Common Workflows

For each common planning workflow in this domain, create a workflow file using the common-workflow template, then list it below using the format: name - optional skill - description:

- `<<workflow-name>>` - `<<optional skill>>` - `<<quick description>>`
- `<<workflow-name>>` - `<<optional skill>>` - `<<quick description>>`
- `<<workflow-name>>` - `<<optional skill>>` - `<<quick description>>`
  When the workflow involves deterministic processing, note the Python script that handles it:
  `scripts/python/<entry-point>`.

## Related Skills

- `<<skill-name>>`: `<<one-sentence description of when to use this skill>>`
- `<<skill-name>>`: `<<one-sentence description of when to use this skill>>`
This is for quick reference during planning.

## Self-Validation

- [ ] No Markdown tables in filled content (use bullet lists instead).

## Cross-References

- `./common-workflow.md` — Workflow file template used by the Common Workflows section.
- Load `skill-template-library` for the canonical template set and its documentation.

## Docs

See the [Common Workflows](#common-workflows) section for workflow definitions.
Base directory for this skill: `file:///<<path-to-skill-directory>>`
