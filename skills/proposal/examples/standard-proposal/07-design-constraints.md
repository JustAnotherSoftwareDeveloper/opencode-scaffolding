## Design constraints

- **Constraint:** Preserve the workspace's canonical ownership boundaries.
  - **Required boundary:** `PROPOSAL.md` remains the metadata owner, and each canonical section owns exactly one file.
  - **Consequence:** The workspace keeps metadata ownership in the index and section ownership in distinct, independently reviewable files.
  - **Evidence:** [Workspace contract](../../reference/workspace-contract.md)

These boundaries are coupled rather than interchangeable: `PROPOSAL.md` remains the stable metadata-bearing index, while each numbered section file owns its decision content. That split preserves file-level review without making the index duplicate canonical section prose. [Workspace contract](../../reference/workspace-contract.md)
