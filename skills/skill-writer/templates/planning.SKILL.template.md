---
name: <<skill-name>>
description: "Use when planning or architecting <<domain>>."
class: planning
---

# <<Skill Name>> — Domain Planning Reference

Replace all `<<placeholder>>` items below.
This template captures planning context for a single domain — not cross-cutting architecture, test strategy, external services, or framework conventions.
See `./reference/frontmatter-rules.md` for class rules and frontmatter requirements.

## When to Use

<<Describe trigger conditions for loading this reference: planning or design discussion within the domain, code review affecting domain code, or onboarding to the domain.>>

## Decision Records

<<Record key decisions within this domain with rationale and trade-offs.>>
<<Link to ADR files if they exist.>>
<<Explain why past domain choices were made and what alternatives were considered.>>

## Constraints & Assumptions

<<List domain-specific preconditions, invariants, non-goals, and known limitations.>>
<<Explain what the domain boundary does not include and why.>>

## Verification Criteria

- <<gate check the domain planning artifact must pass before handoff>>.
- <<gate check the domain planning artifact must pass before handoff>>.

## Docs

See the generated skill's `reference/`, `templates/`, `schemas/`, and `snippets/` directories for supporting documentation.
- `./reference/frontmatter-rules.md` — Class taxonomy and frontmatter field rules
- `./reference/platform-context.md` — Platform context where skills live
- `./reference/progressive-disclosure.md` — Pushing detail to reference files
- `./reference/trigger-eval.md` — Description composition eval
- `./reference/validation-checklist.md` — Skill verification checklist
- `./reference/gotchas.md` — Common pitfalls
- `./reference/update-workflow.md` — UPDATE mode reference
- `./templates/planning.SKILL.template.md` — This template
- `./schemas/class-contract.example.json` — Example JSON Schema for class contracts
- `./schemas/class-contract.example.xsd` — Example XSD for class contracts
- `./snippets/README.md` — Reusable code snippets
- `./style-guide.md` — Editorial conventions
