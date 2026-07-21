---
description: Create an evidence-based decision proposal from a topic and explicit source-document paths.
---

Load skill `proposal`, then create a proposal workspace for:

`$ARGUMENTS`

## Workflow

1. Load the `proposal` skill.
2. Parse the topic and explicit source-document paths from the request above.
3. Follow the loaded skill without adding delegation or a separate discovery workflow.
4. Create `.proposals/<epoch-ms>-<summary-slug>/` with canonical `PROPOSAL.md`, `implementation.md`, and copied source documents.
5. Validate the workspace against the proposal workspace contract.
6. Report the proposal workspace path.

## Constraints

- Do not create an analysis or plan workspace.
- Do not implement the proposal.
- Do not migrate, rewrite, move, or split existing historical `.proposals/*.md` proposal files.
- If `$ARGUMENTS` lacks a topic or explicit source-document paths, report the applicable proposal-skill blocker.
