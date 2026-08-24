## Alternatives and trade-offs

### Monolithic document

- **Differentiator:** Keeps the proposal in one file.
- **Benefits:** One file to open.
- **Costs and consequences:** Section boundaries are not file boundaries.
- **Disposition:** Rejected because the single-file structure does not preserve independent section ownership.
- **Evidence:** The [workspace contract](../../reference/workspace-contract.md) assigns each canonical decision section its own numbered file.

### Indexed section files

- **Differentiator:** Gives each canonical decision section its own indexed file.
- **Benefits:** Independent review and stable navigation.
- **Costs and consequences:** More files.
- **Disposition:** Selected because per-section files preserve independent review and stable navigation.
- **Evidence:** The [proposal format](../../reference/proposal-format.md) defines one file per numbered canonical section and an ordered index.

The indexed option accepts the unequal file-count cost because file-level section ownership is the basis for independent review; the monolithic option's one-file convenience does not provide that boundary.
