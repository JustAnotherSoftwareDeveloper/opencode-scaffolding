---
name: planning-pipeline-architecture
description: "Use as planning reference for the analysis, proposal, and plan lifecycle."
selection:
  role: reference
  tags:
    inputs: [planning workflow question]
    outputs: [lifecycle and handoff guidance]
    topics: [analysis proposal plan lifecycle]
    constraints: [planning reference]
  use_when: [planning work needs lifecycle or handoff guidance]
  not_for: [performing analysis, proposals, or plans directly]
class: planning
---

# Planning Pipeline Architecture — Domain Planning Reference

Use the planning lifecycle to distinguish analysis, proposal, and plan work.

## Direct Selection Guidance

- Select analysis for assessment, conclusions, comparisons, or recommendations.
- Select proposal for a durable decision record, approval, or feedback.
- Select plan for executable task planning from source documents.
- Preserve assumptions and source evidence through later stages.
- Select stages independently; do not require the full lifecycle.

## Profile Contract

Describe the lifecycle with grouped tags, aliases, `use_when`, and `not_for` values
that distinguish planning references from executable neighbors.
Keep values task-grounded, discriminative, concise, stable, discoverable,
non-redundant, and scoped.

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
- Confirm the profile uses the current `selection.role` and grouped-tag contract.
- Confirm no execution or side-effect instructions appear.
