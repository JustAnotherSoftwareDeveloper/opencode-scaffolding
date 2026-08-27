---
name: planning-pipeline-architecture
description: "Use as planning reference for analysis, proposal, plan, and audit handoffs."
selection:
  role: reference
  tags:
    inputs: [planning workflow question]
    outputs: [lifecycle and handoff guidance]
    topics: [analysis proposal plan audit lifecycle]
    constraints: [passive planning reference, non-transitive]
  use_when: [planning work needs lifecycle, audit, or handoff guidance]
  not_for: [performing analysis, proposals, plans, audits, or fixes directly]
class: planning
---

# Planning Pipeline Architecture — Domain Planning Reference

This reference describes planning states, artifacts, owners, and handoffs across
analysis, proposal, plan, and audit work.

## Owners And Boundaries

- `proposal` owns the recorded decision, its source evidence, and the authoritative
  proposal baseline.
- `plan-writer` owns proposal-derived plan publication, bounded finding fixes, and
  revised plan publication.
- `plan-audit` owns the independent external audit report for an immutable
  proposal-derived plan snapshot. It does not repair findings or approve work.
- This planning reference is passive and non-transitive. It grants no execution,
  tool, write, delegation, skill-loading, approval, or completion authority.

## Direct Selection Guidance

- Analysis concerns assessment, conclusions, comparisons, recommendations, and
  uncertainty resolution.
- Proposal concerns a durable decision record and its evidence.
- `plan-writer` concerns executable task planning from source documents.
- `plan-audit` concerns an independent audit report for a proposal-derived plan
  snapshot.
- Assumptions, evidence gaps, open questions, and source evidence remain labeled
  through later stages.
- Stages remain independently selectable; the full lifecycle is not required.

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
- `./reference/proposal-derived-audit-lifecycle.md`

## Self-Validation

- Confirm the description uses `Use as planning reference`.
- Confirm the profile uses the current `selection.role` and grouped-tag contract.
- Confirm the proposal-derived audit lifecycle and direct plan-only boundary remain
  represented in the references.
- Confirm no execution or side-effect authority appears.
