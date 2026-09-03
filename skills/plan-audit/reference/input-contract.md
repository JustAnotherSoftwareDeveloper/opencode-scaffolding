# Input Contract

## Normalized Object

The operation accepts one object with these fields:

- `planWorkspace` — resolved directory containing the plan brief or summary,
  `tasks.json`, `tasks.md` when present, copied sources, and declared metadata.
- `proposalBaseline` — an object with `mode` and `root`. `mode` is
  `authoritative` or `copied-snapshot`.
- `assignmentInventory` — an optional path or object containing a persisted skill
  inventory. It is historical comparison evidence only.
- `auditOutput` — a new caller-declared Markdown path.

An authoritative baseline must contain `PROPOSAL.md` with valid YAML frontmatter
(`title`, `slug`, `status`, `readiness`, `decision-owner`, `source-documents`),
the required H2 sections (`Recommendation`, `Technical Rationale`, `Questions`,
`Options Considered`, `Implementation Details`, `Verification Criteria`,
`Sources`), and every frontmatter-declared copied source file. The audit records
status, readiness, and declared sources as evidence facts; none is treated as
approval.

The copied-snapshot exception additionally requires an explicit unavailable or
unreadable reason, `originIdentity`, `captureTime`, and a manifest covering every
snapshot file. It must pass the same PROPOSAL.md section, frontmatter, and
source-documents index checks. When both baselines are supplied, the authoritative
tree remains the comparison baseline and any difference is a proposal-compliance
source-drift finding.

## Boundary

The report parent must already exist and the target must not exist. The resolved
report is under the workspace root and outside every plan, proposal, copied snapshot,
persisted inventory, and selected skill tree. No alternate destination is chosen.

The operation snapshots all readable regular files before checks and verifies their
SHA-256 digest and byte length again before writing. A changed file blocks the check
that depends on it. The report is the only write.
