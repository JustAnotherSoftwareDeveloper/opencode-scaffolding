## Alternatives and trade-offs

### Keep all conditional detail in canonical files

- **Differentiator:** Keeps every conditional branch in its governing canonical section.
- **Benefits:** Reduces file count and avoids additional companion-file links.
- **Costs and consequences:** A complex review path can be obscured when substantial conditional detail remains in a canonical file.
- **Disposition:** Rejected for substantial conditional detail because the lower file count does not provide the expanded navigation this decision needs.
- **Evidence:** The [proposal format](../../reference/proposal-format.md) allows indexed companion files when expanded structure materially benefits navigation while preserving one file per canonical decision section.

### Indexed companion files for substantial conditional detail

- **Differentiator:** Allows a companion file only when conditional detail is substantial, while retaining one governing canonical section and links from both the section and the proposal index.
- **Benefits:** Separates material conditional branches without replacing, duplicating, or renaming canonical sections.
- **Costs and consequences:** Adds a bounded amount of file and navigation overhead and requires the governing-section and index links to remain aligned.
- **Disposition:** Selected because it improves review navigation without abandoning canonical section ownership.
- **Evidence:** The [proposal format](../../reference/proposal-format.md) permits indexed companion files for complex proposals when expanded structure materially benefits navigation, and the [workspace contract](../../reference/workspace-contract.md) requires substantial companions to be linked from both the index and their governing section.

### Unbounded companion files

- **Differentiator:** Moves conditional detail into companion files without a substantial-detail threshold or a bounded ownership rule.
- **Benefits:** Improves separation between the canonical prose and supporting branches.
- **Costs and consequences:** Can fragment the proposal and make the governing canonical section harder to identify.
- **Disposition:** Rejected because the decision covers substantial conditional companion documents, not arbitrary fragmentation.
- **Evidence:** The [workspace contract](../../reference/workspace-contract.md) limits companion files to substantial conditional detail and requires a governing canonical section; the [risks and revisit conditions](./12-risks-and-revisit-conditions.md) identify review fragmentation as the material risk.

The alternatives carry unequal caveats. Keeping all detail in canonical files minimizes file overhead but can hide a complex review path; unbounded companions maximize separation but can fragment the proposal. The selected option accepts limited file overhead only when substantial conditional detail warrants it and preserves two-way indexing. [Proposal format](../../reference/proposal-format.md); [workspace contract](../../reference/workspace-contract.md)

**Evidence Gap:** The cited format sources establish navigation and ownership rules but provide no direct measurement of reviewer effort. The expected review benefit and the fragmentation risk therefore remain format-based inferences.
