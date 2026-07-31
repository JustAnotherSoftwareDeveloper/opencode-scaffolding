---
name: planning-pipeline-architecture
description: "Use as planning reference for the analysis, proposal, and plan lifecycle."
schema_version: "1.0"
cues:
  - facet: subject
    value: planning lifecycle
  - facet: outcome
    value: pipeline stage guidance
  - facet: constraint
    value: planning reference
relationships:
  - role: reference
    rationale: provides passive planning lifecycle context
class: planning
---

# Planning Pipeline Architecture — Domain Planning Reference

Use the planning lifecycle to distinguish analysis, proposal, and plan work.

## Routing Cues

- Select analysis for assessment, conclusions, comparisons, or recommendations.
- Select proposal for a durable decision record, approval, or feedback.
- Select plan for executable task planning from source documents.
- Preserve assumptions and source evidence through later stages.
- Select stages independently; do not require the full lifecycle.

## Tag Contract

Identify the tasks this reference owns and its nearest planning competitors before adding cues.
Keep only task-grounded, discriminative, atomic, stable, discoverable, non-redundant, scoped cues.
Use repository namespaces for planning vocabulary that the built-in facets do not express.
Require only the primary operation for owner skills.

## References

- `./reference/analysis-only.md`
- `./reference/proposal-only.md`
- `./reference/plan-only.md`
- `./reference/analysis-to-proposal.md`
- `./reference/analysis-to-plan.md`
- `./reference/proposal-to-plan.md`
- `./reference/analysis-to-proposal-to-plan.md`

## Self-Validation

- Confirm the description uses `Use as planning reference`.
- Confirm local registry declarations resolve without core changes.
- Confirm no execution or side-effect instructions appear.
