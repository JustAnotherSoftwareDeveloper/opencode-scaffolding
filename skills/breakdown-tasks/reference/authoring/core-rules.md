# Core Rules

Load the passive `task-contract` documentation skill before using these authoring
procedures. It owns shared semantics for task identity, atomicity,
result-to-verification alignment, dependencies, coupling evidence, traceability, and
authoring metadata. This file describes the decomposition workflow and does not
restate those semantics.

## Break Down The Problem — operation-owned

- After request normalization and before skill assignment, follow the
  [Decomposition Method](decomposition-method.md). Decompose the requested outcome
  into smaller results, split any compound result again, and connect the final results
  with explicit handoffs.

## Draft Boundaries — operation-owned

During boundary drafting, apply the loaded `task-contract` documentation skill's
**Atomicity and alignment**, **Dependencies and coupling**, and **Traceability and
metadata** references (`atomicity-and-alignment.md`,
`dependencies-and-coupling.md`, and `traceability-and-metadata.md`) without restating
their shared semantics. Complete boundary drafting before skill selection; do not
include `skills` until assignment.

## Assign Skills Last — operation-owned

Stabilize the task boundaries and their draft metadata before selecting skills.
Do not merge or split work to fit an available skill. After any split or migration,
rerun the operation's coverage, boundary, dependency, and skill checks. Treat
uncertain wording as a reason to review, not evidence for a boundary or coupling
decision. Resolve that question by applying the shared contract.
