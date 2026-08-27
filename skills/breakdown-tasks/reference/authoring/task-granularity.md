# Task Granularity

Choose boundaries from independent work, not file count or workflow stages. The
shared [atomicity and alignment contract](../../../task-contract/reference/atomicity-and-alignment.md)
owns the split test and the one-result boundary; the shared
[dependencies and coupling contract](../../../task-contract/reference/dependencies-and-coupling.md)
owns ordering and coupling evidence. Do not redefine either contract here.

## Start With An Inventory — operation-owned

List each requested question, change, operation, decision, and deliverable. Include
concealed concerns that appear inside broad phrases such as “finish the migration”
or “update the feature.” Name the result for each concern before selecting skills.

## Apply The Shared Boundary Review

For every pair of concerns, apply the split test in the shared task-contract
reference. Split independently actionable concerns into separate draft tasks and
represent required order with the shared dependency semantics. Prefer an explicit
dependency over an implicit compound task and review coupling with the linked shared
reference.

## Recheck The Boundary — operation-owned

After each split or migration, use the shared contract to review identity, result,
verification, dependencies, coupling evidence, traceability, and metadata. Then
confirm that the operation's assigned skills match the final boundary. Do not use
punctuation, lifecycle order, or skill availability as proof, and do not introduce
universal task, file, step, or skill limits.
