# Proposal To Plan

`proposal-to-plan` - `proposal`, `plan` - Moves from a decision record to executable planning.

**Use when:** A decision record and its supporting evidence require a source-preserving task plan.

## Purpose

This workflow converts decision evidence into an executable planning artifact.
The proposal workspace provides decision context, scope boundaries, requirements, and unresolved material for plan authoring.

## Sequence

1. A proposal workspace captures the decision and supporting evidence.
2. The proposal workspace and relevant source documents form the source set for planning.
3. The plan workspace produces validated task JSON and rendered task Markdown.
4. The planning lifecycle ends with an executable plan artifact.

## Artifacts

- Proposal workspace.
- Proposal source documents and any additional planning evidence.
- Plan workspace containing `tasks.json` and `tasks.md`.

## Notes

- Plan source documents remain preserved within the plan workspace.
- Source-derived constraints remain present in task context.
- Unresolved material remains labeled as `Open Question:` in task context.
- Unverified material remains labeled as `Assumption:` in task context.
