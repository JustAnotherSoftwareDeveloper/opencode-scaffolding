## Selected direction

**Recommendation:** Select indexed section files: keep `PROPOSAL.md` as the metadata-bearing index and give each canonical decision section its own numbered file. [Workspace contract](../../reference/workspace-contract.md)

**Decisive rationale:** Per-section ownership preserves independent review and stable navigation. A monolithic document is easier to open, but its section boundaries are not file boundaries, so it cannot provide the same review boundary. [Proposal format](../../reference/proposal-format.md)

**Material consequences:**

- **Review benefit:** Reviewers can open a canonical section independently while the index remains stable. [Proposal format](../../reference/proposal-format.md)
- **File-count trade-off:** The workspace contains more files, which adds navigation surface. The decision accepts this cost because file-level section ownership enables independent review; the one-file convenience does not. [Workspace contract](../../reference/workspace-contract.md)

**Objection:** A monolithic document offers one file to open.

**Disposition:** Reject that option because its one-file convenience does not preserve independent section ownership. [Workspace contract](../../reference/workspace-contract.md)

**Evidence state:** Direct format evidence supports indexed section files: the workspace contract assigns each canonical decision section its own numbered file, and the proposal format defines one file per numbered section with an ordered index. [Workspace contract](../../reference/workspace-contract.md); [Proposal format](../../reference/proposal-format.md)

**Evidence Gap:** The cited sources provide no direct measurement of reviewer effort; the expected review benefit remains an evidence-limited, format-based inference.

**Implementation link:** See the [implementation overview](./10-implementation.md) for concrete changes. Keep that implementation detail separate from this decision record. [Implementation format](../../reference/implementation-format.md)
