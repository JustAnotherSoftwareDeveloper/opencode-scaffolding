# Task Granularity

Choose boundaries by repeatedly making the requested problem smaller. The loaded
`task-contract` documentation skill's
[atomicity rule](../../../task-contract/reference/atomicity-and-alignment.md) owns
the split and stopping tests. Its
[dependency rule](../../../task-contract/reference/dependencies-and-coupling.md)
owns handoffs and coupling.

## Make The Problem Smaller

1. Name the requested outcome.
2. List the smaller results needed to reach it.
3. Create separate candidates for discovery, research, analysis, decisions,
   authoring, changes, verification, and reporting.
4. Split candidates that still contain more than one immediate result.
5. Repeat until each piece is the smallest useful assignment.
6. Add dependencies and handoffs after the pieces are clear.

Do not stop because all work contributes to one final deliverable. Prefer a fine task
with a short handoff over a broad task with hidden stages. When uncertain, split.

## Recheck After Changes

After a split, merge, or dependency change, review the complete set again. Ensure
every result is covered once, each dependent task receives a usable input, and the
assigned skills still fit without changing the boundaries.
