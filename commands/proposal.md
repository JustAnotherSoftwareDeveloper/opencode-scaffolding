---
description: Create a one-document engineering proposal from a topic and explicit source paths
---

Load `proposal` and create one proposal workspace from the topic, decision owner, and explicit source-document paths in `$ARGUMENTS`. Use the conditional persisted-research intake below before authoring whenever material external or comparative evidence is not already covered by the supplied sources.

`$ARGUMENTS`

## Workflow

1. Parse the topic, decision owner, and explicit source-document paths from `$ARGUMENTS`; load the `proposal` skill.
2. Decide before authoring whether the recommendation materially depends on external, comparative, or prior-art evidence that is not covered by the supplied sources. If it does not, or the supplied sources already suffice, preserve the existing explicit-source workflow and do not require or create a research packet.
3. If material research is needed and absent or incomplete, stop before creating a workspace or drafting a proposal. Return a blocker identifying the missing or incomplete research and tell the caller to complete and persist the research separately, then rerun this command with explicit paths to the packet files. Do not research, delegate, draft from an unpersisted summary, or treat search-result snippets as completed evidence within this operation.
4. When persisted research is supplied for a material research need, require a complete packet with its scope and limitations (`README.md`), findings and synthesis (`answer.md`), source register and discovery record (`sources.md`), and decision-driving claim record (`claims.md`). Check completeness before authoring; if any required component is missing or inadequately documented, block as in step 3. A documented unresolved or unavailable finding is a valid research result, not by itself an incomplete packet; carry it forward as an `Evidence Gap:`. Include each supplied packet file as an explicit source path alongside the other declared sources.
5. Follow the proposal skill's source-safety, evidence, Questions, readiness, and historical-boundary rules without adding delegation. Establish readiness from the supplied and persisted evidence; retain blocking unavailable evidence as `Evidence Gap:` and do not present the proposal as decision-ready.
6. Create `.proposals/<epoch-ms>-<summary-slug>/PROPOSAL.md` as the only authored proposal document and copy each declared source into its category directory.
7. Validate the complete workspace with proposal-directory Markdown lint and the proposal self-validation contract.
8. Report the workspace path, lifecycle status, readiness fact, copied-source manifest, and validation result.

## Constraints

- Do not create numbered proposal files, `implementation.md`, a separate source index, an analysis workspace, or a plan workspace.
- Do not implement, approve, accept, or infer authority for the proposal.
- Treat `status` and `readiness` as independent facts; `review-ready` and `decision-ready` are not approval.
- Do not mutate or rewrite historical `.proposals/` workspaces.
- If the topic, decision owner, or explicit source paths are absent, return the applicable proposal-skill blocker.
- Do not create a proposal workspace or begin proposal authoring while material research is missing or its supplied persisted packet is incomplete.
- Do not perform research, create research artifacts, or delegate research or proposal drafting within this operation; accept material research only through explicit paths to a complete persisted packet.
