---
description: Load the proposal skill and start a deep proposal for the given topic, selecting appropriate worker lanes and running delegated exploration/analysis before drafting.
---

Load skill `proposal`, then create a proposal artifact for:

`$ARGUMENTS`

## Workflow

1. Load the `proposal` skill.
2. Classify intent and depth for the request above.
3. Run discovery (local file inventory, prior art, conventions). For `deep` proposals, select the appropriate worker lanes from the proposal skill's depth-tier lane matrix and run delegated exploration/analysis before drafting.
4. Create `.proposals/<unix-timestamp>-slug.md` from the proposal template, including lane rationale, evidence, analysis, and clarification markers when applicable.
5. Run embedded quality check via `worker-*` with review-mode instructions.
6. Report the artifact path, status, key tradeoffs, and next user decision.

## Constraints

- Do not plan or implement. This command creates a proposal only.
- If `$ARGUMENTS` is empty, prompt the user for the topic to propose.
