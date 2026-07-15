# Analysis Only

`analysis-only` - `generic-analysis` - Produces an evidence-calibrated assessment without creating a decision or plan workspace.

**Use when:** The requested outcome is a bounded conclusion, comparison, recommendation, or set of next actions.

## Purpose

This workflow resolves uncertainty without committing to a decision artifact or executable plan.
The analysis result distinguishes observations, inferences, assumptions, uncertainties, and recommendations.

## Sequence

1. A question, problem, artifact, or decision enters analysis.
2. Relevant evidence and material uncertainty shape the assessment.
3. The assessment supplies a conclusion and prioritized next actions.
4. The planning lifecycle ends unless a later request requires a decision record or plan.

## Artifacts

- Analysis response containing the assessment, conclusion, and next actions.
- Source artifacts examined during the assessment.

## Notes

- This workflow does not create a proposal workspace.
- This workflow does not create a plan workspace.
- A later proposal workflow requires the analysis result to exist as an explicit source document.
