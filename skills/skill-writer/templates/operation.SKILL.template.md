---
name: <<skill-name>>
description: "Use when <<trigger-condition>>."
class: operation
---

## Normalize Input

Map invocation context to one internal input object. Define required fields, defaults, and `BLOCKED: <reason>` conditions for missing required input.

## Procedure

Each step is one imperative action. Do not delegate sub-tasks.

1. <<step>>.
2. <<step>>.
3. <<step>>.
4. <<step>>.

## Self-Validation

Each check is a yes/no assertion.

- <<yes/no check>>.
- <<yes/no check>>.
- <<yes/no check>>.

## Expected Output

Specify: artifact path/location, format, contents, and completeness criteria.
- `## Docs` section present at bottom with links and descriptions for all supporting files.

## Docs

See the generated skill's `reference/`, `templates/`, `schemas/`, and `snippets/` directories for supporting documentation.
- `./reference/frontmatter-rules.md` — Class taxonomy and frontmatter field rules
- `./reference/platform-context.md` — Platform context where skills live
- `./reference/progressive-disclosure.md` — Pushing detail to reference files
- `./reference/trigger-eval.md` — Description composition eval
- `./reference/validation-checklist.md` — Skill verification checklist
- `./reference/gotchas.md` — Common pitfalls
- `./reference/update-workflow.md` — UPDATE mode reference
- `./templates/operation.SKILL.template.md` — This template
- `./schemas/class-contract.example.json` — Example JSON Schema for class contracts
- `./schemas/class-contract.example.xsd` — Example XSD for class contracts
- `./snippets/README.md` — Reusable code snippets
- `./style-guide.md` — Editorial conventions