# Analysis To Proposal

`analysis-to-proposal` - `generic-analysis`, `proposal` - Moves from an uncertain problem to an evidence-backed decision record.

**Use when:** The request needs an assessment before approval, feedback, or a durable decision.

## Purpose

This workflow separates assessment from decision recording.
Analysis clarifies the problem, evidence, alternatives, uncertainty, and recommendation.
Proposal records the decision from explicit source documents.

## Sequence

1. An ambiguous problem enters analysis.
2. Analysis produces a conclusion, material uncertainty, and next actions.
3. The analysis result becomes a persisted source document with other relevant evidence.
4. The documented analysis and evidence form the source set for a proposal workspace.
5. The proposal workspace becomes the decision artifact.

## Artifacts

- Persisted analysis document.
- Supporting evidence documents.
- Proposal workspace containing `PROPOSAL.md` and `implementation.md`.

## Notes

- A conversational analysis response is not a proposal source path until it is preserved as a document.
- Unresolved material remains labeled as `Open Question:` in the proposal workspace.
- Unverified material remains labeled as `Assumption:` in the proposal workspace.
- This workflow ends after decision recording unless executable planning is required.
