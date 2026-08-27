# Core Rules

Load the passive [task-contract reference](../../../task-contract/SKILL.md) before
using these authoring procedures. The shared owner defines task identity, atomicity,
result and verification alignment, dependency meaning, coupling evidence,
traceability, and authoring metadata. This file does not restate those invariants.

## Inventory Concerns — operation-owned

- List every question, change, operation, decision, and deliverable.
- Name the result produced by each concern.
- Do not use a workflow phase, shared topic, or desired packet size as a boundary.

## Draft Boundaries — operation-owned

Use the shared [atomicity and alignment](../../../task-contract/reference/atomicity-and-alignment.md),
[dependencies and coupling](../../../task-contract/reference/dependencies-and-coupling.md),
and [traceability and metadata](../../../task-contract/reference/traceability-and-metadata.md)
references when turning the inventory into candidate tasks. Establish boundaries
before selecting skills, and keep the task count derived from the inventory rather
than from a capacity target.

The operation adds the draft fields required by the input schema (`taskId`,
`verificationCoverage`, `dependencies`, `antiPatternSignals`,
`purposeOutputAlignment`, and any justified `couplingRationale`) without changing
the shared meaning of those fields. Do not include `skills` until assignment.

## Assign Skills Last — operation-owned

Stabilize the candidate boundaries and their draft metadata before selecting skills.
Do not merge or split work to fit an available skill. After any split or migration,
rerun the operation's boundary, mapping, dependency, and skill checks. Treat
uncertain language as a review prompt and apply the shared contract explicitly; it
is not proof of a boundary or coupling decision.
