# Proposal Only

`proposal-only` - `proposal` - Produces an evidence-based decision workspace from explicit source documents.

**Use when:** Existing evidence requires a durable decision record, approval request, or structured feedback without additional analysis or task planning.

## Purpose

This workflow records a decision from a defined source set.
The proposal workspace preserves the source documents, decision rationale, requirements, open engineering decisions, and implementation details.

## Sequence

1. Existing source documents establish the decision context.
2. The source set forms the basis for a proposal workspace.
3. The proposal workspace records the requested decision and its evidence.
4. The planning lifecycle ends unless executable planning is required later.

## Artifacts

- Supporting source documents.
- Proposal workspace containing `PROPOSAL.md` with Implementation Details, Verification Criteria, and Questions sections, plus copied sources.

## Notes

- The source set contains explicit document paths.
- Only unresolved decisions required from the responsible engineer remain labeled as `Open Question:` in the proposal workspace.
- Researchable uncertainty remains in evidence or analysis rather than becoming a proposal open question.
- Unverified material remains labeled as `Assumption:` in the proposal workspace.
