---
description: Load the proposal skill and start a proposal for the given topic
---

Load skill `proposal`, then create a proposal artifact for:

`$ARGUMENTS`

## Workflow

1. Load the `proposal` skill.
2. Classify intent and depth for the request above.
3. Run discovery (local file inventory, prior art, conventions).
4. Create `.proposals/<unix-timestamp>-slug.md` from the proposal template.
5. Run embedded quality check via `analysis-*` worker.
6. Report the artifact path, status, key tradeoffs, and next user decision.

## Constraints

- Do not plan or implement. This command creates a proposal only.
- If `$ARGUMENTS` is empty, prompt the user for the topic to propose.
