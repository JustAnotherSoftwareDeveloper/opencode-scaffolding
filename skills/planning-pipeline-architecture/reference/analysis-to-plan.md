# Analysis To Plan

`analysis-to-plan` - `generic-analysis`, `plan` - Moves from documented assessment to executable planning without a decision workspace.

**Use when:** An assessment resolves the planning question and no durable decision record or approval gate is required.

## Purpose

This workflow converts analysis evidence into executable planning.
The persisted analysis document supplies planning context alongside any other relevant source documents.

## Sequence

1. A question, problem, or artifact enters analysis.
2. Analysis produces a conclusion, material uncertainty, and next actions.
3. The analysis result becomes a persisted source document with other relevant evidence.
4. The documented analysis and evidence form the source set for a plan workspace.
5. The plan workspace records executable task JSON and rendered task documentation.

## Artifacts

- Persisted analysis document.
- Supporting evidence documents.
- Plan workspace containing `tasks.json` and `tasks.md`.

## Notes

- A conversational analysis response is not a plan source path until it is preserved as a document.
- This workflow does not create a proposal workspace.
- Unresolved material remains labeled as `Open Question:` in task context.
- Unverified material remains labeled as `Assumption:` in task context.
