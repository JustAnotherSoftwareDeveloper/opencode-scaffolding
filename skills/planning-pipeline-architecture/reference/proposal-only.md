# Proposal Only

`proposal-only` - `proposal` - Produces an evidence-based decision workspace from explicit source documents.

**Use when:** Existing evidence requires a durable decision record, approval request, or structured feedback without additional analysis or task planning.

## Purpose

Use this workflow to record a decision from an explicit set of source documents.
The proposal workspace contains copies of those documents and records the decision rationale, requirements, open engineering decisions, and implementation details.

## Sequence

1. Use existing source documents to establish the decision context.
2. Build a proposal workspace from that source set.
3. Record the requested decision and supporting evidence in the workspace.
4. End the planning lifecycle here unless executable planning is required later.

## Artifacts

- Supporting source documents.
- Proposal workspace containing `PROPOSAL.md` with Implementation Details, Verification Criteria, and Questions sections, plus copied sources.

## Notes

- The source set contains explicit document paths.
- Only unresolved decisions required from the responsible engineer remain labeled as `Open Question:` in the proposal workspace.
- Researchable uncertainty remains in evidence or analysis rather than becoming a proposal open question.
- Unverified material remains labeled as `Assumption:` in the proposal workspace.
