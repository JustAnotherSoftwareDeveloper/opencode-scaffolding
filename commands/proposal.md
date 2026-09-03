---
description: Create a one-document engineering proposal from a topic and explicit source paths
---

Load `proposal`, then create a proposal workspace for:

`$ARGUMENTS`

## Workflow

1. Parse the topic, decision owner, and explicit source-document paths from `$ARGUMENTS`.
2. Load the `proposal` skill.
3. Follow its source-safety, evidence, Questions, readiness, and historical-boundary rules without adding delegation.
4. Create `.proposals/<epoch-ms>-<summary-slug>/PROPOSAL.md` as the only authored proposal document and copy each declared source into its category directory.
5. Validate the complete workspace with proposal-directory Markdown lint and the proposal self-validation contract.
6. Report the workspace path, lifecycle status, readiness fact, copied-source manifest, and validation result.

## Constraints

- Do not create numbered proposal files, `implementation.md`, a separate source index, an analysis workspace, or a plan workspace.
- Do not implement, approve, accept, or infer authority for the proposal.
- Treat `status` and `readiness` as independent facts; `review-ready` and `decision-ready` are not approval.
- Do not mutate or rewrite historical `.proposals/` workspaces.
- If the topic, decision owner, or explicit source paths are absent, return the applicable proposal-skill blocker.
