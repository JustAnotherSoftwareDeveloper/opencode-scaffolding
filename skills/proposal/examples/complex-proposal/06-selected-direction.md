## Selected direction

**Recommendation:** Permit an indexed companion file only for substantial conditional detail when expanded structure materially benefits navigation. Keep one governing canonical section, link the companion from this section and `PROPOSAL.md`, and do not replace, duplicate, or rename canonical sections. [Proposal format](../../reference/proposal-format.md); [Workspace contract](../../reference/workspace-contract.md)

**Decisive rationale:** This direction separates material conditional branches without abandoning canonical section ownership. It improves review navigation where a complex path would otherwise be obscured, while the substantial-detail threshold and two-way indexing bound fragmentation. [Proposal format](../../reference/proposal-format.md); [Workspace contract](../../reference/workspace-contract.md)

**Material consequences:**

- **Review navigation:** Reviewers can follow substantial conditional detail through a companion file while the governing decision remains in its canonical section. [Proposal format](../../reference/proposal-format.md)
- **File and link overhead:** The workspace gains a bounded amount of file and navigation overhead, and the governing section and index must remain aligned. [Workspace contract](../../reference/workspace-contract.md)
- **Ownership boundary:** A companion file may contain substantial conditional detail, but it cannot replace, duplicate, or rename a canonical section. [Workspace contract](../../reference/workspace-contract.md)

The alternatives carry unequal caveats. Keeping all conditional detail in canonical files minimizes file count and avoids additional companion-file links, but it can obscure a complex review path. Unbounded companion files maximize separation, but they can fragment the proposal and make the governing canonical section harder to identify. The selected direction accepts limited file overhead only when substantial conditional detail warrants it and preserves two-way indexing. [Proposal format](../../reference/proposal-format.md); [Workspace contract](../../reference/workspace-contract.md)

**Objection:** Keeping all conditional detail in canonical files offers the smallest file set and avoids link maintenance.

**Disposition:** Reject that option for substantial conditional detail because its lower file count does not provide the expanded navigation this decision needs. [Proposal format](../../reference/proposal-format.md)

**Objection:** Unbounded companion files provide maximum separation between canonical prose and conditional branches.

**Disposition:** Reject that option because it lacks a substantial-detail threshold and bounded ownership rule, increasing the risk of proposal fragmentation. [Workspace contract](../../reference/workspace-contract.md); [risks and revisit conditions](./12-risks-and-revisit-conditions.md)

**Evidence state:** Direct format evidence supports indexed companion files when expanded structure materially benefits navigation, and the workspace contract requires each substantial companion to be linked from both the proposal index and one governing canonical section. [Proposal format](../../reference/proposal-format.md); [Workspace contract](../../reference/workspace-contract.md)

**Evidence Gap:** The cited format sources provide no direct measurement of reviewer effort. The expected review benefit and the fragmentation risk therefore remain format-based inferences.

**Revisit condition:** Reconsider the companion-file guidance if reviewers cannot identify the governing canonical section; that result would indicate that the bounded-navigation rule is not preventing fragmentation. [Risks and revisit conditions](./12-risks-and-revisit-conditions.md)

**Implementation link:** See the [implementation overview](./10-implementation.md) for concrete changes. Keep implementation detail separate from this decision record. [Implementation format](../../reference/implementation-format.md)
