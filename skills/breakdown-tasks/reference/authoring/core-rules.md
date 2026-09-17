# Core Rules

Load the passive `task-contract` documentation skill before using these authoring
procedures. The shared owner defines task identity, atomicity, result and
verification alignment, dependency meaning, coupling evidence, traceability, and
authoring metadata. This file does not restate those invariants.

## Break Down The Problem — operation-owned

- After request normalization and before skill assignment, follow the
  [Decomposition Method](decomposition-method.md). Break the requested outcome into
  smaller results, split compound results again, and connect the final pieces with
  explicit handoffs.

## Draft Boundaries — operation-owned

The method applies the loaded documentation skill's named **Atomicity and
alignment**, **Dependencies and coupling**, and **Traceability and metadata**
references, exposed there as `atomicity-and-alignment.md`,
`dependencies-and-coupling.md`, and `traceability-and-metadata.md`, without
redefining them. It completes before selection; do not include `skills` until
assignment.

## Assign Skills Last — operation-owned

Stabilize the task boundaries and their draft metadata before selecting skills.
Do not merge or split work to fit an available skill. After any split or migration,
rerun the operation's coverage, boundary, dependency, and skill checks. Treat
uncertain language as a review prompt and apply the shared contract explicitly;
it is not proof of a boundary or coupling decision.
