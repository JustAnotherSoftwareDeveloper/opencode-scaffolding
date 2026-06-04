---
description: Load the proposal skill and start a deep proposal for the given topic, running delegated exploration/analysis with worker-md before drafting.
---

Load skill `proposal`, then create a proposal artifact for:

`$ARGUMENTS`

## Workflow

1. Load the `proposal` skill.
2. Classify intent and depth for the request above.
3. Run discovery (local file inventory, prior art, conventions). For `deep` proposals, run delegated exploration/analysis with `worker-md` before drafting.
4. Create `.proposals/<unix-timestamp>-slug/INDEX.md` as a table of contents only, plus `metadata.md` and the canonical section files from the proposal workspace template, including lane rationale, evidence, analysis, and clarification markers in their section files when applicable.
5. Run embedded quality check via `worker-md` with review-mode instructions.
6. Report the artifact path, status, key tradeoffs, and next user decision.

## Constraints

- Do not plan or implement. This command creates a proposal only.
- Do not migrate, rewrite, move, or split existing historical `.proposals/*.md` proposal files.
- If `$ARGUMENTS` is empty, prompt the user for the topic to propose.
