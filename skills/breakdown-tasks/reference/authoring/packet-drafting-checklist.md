# Packet Drafting And Traceability Checklist

Use this checklist after decomposition produces the final task results and before
skill assignment. The task schema defines packet structure; the loaded
`task-contract` documentation defines shared task semantics.

## Per-Task Checklist

- Give the task a stable `taskId`; state the same single result in `purpose` and
  `expectedOutput`.
- In `context`, include task-specific request facts, constraints, exclusions, and
  required prior decisions.
- In `filesToRead`, list source files and predecessor handoffs; in `filesToWrite`,
  list only the task's write boundary.
- Write concrete execution instructions for producing the one immediate result. Put
  independently executable checks in a dependent verification task.
- Record observable completion in `verificationCoverage`; align it with `purpose`
  and `expectedOutput`.
- For each dependency, identify the predecessor, supplied result, consumer use, and
  readiness condition. A dependency does not make a compound task atomic.
- Use `couplingRationale` only when multiple changes share one result and one
  verification boundary, and separating them would cause concrete harm.
- Keep the task boundary unchanged during skill assignment. Choose a skill to fit the
  task; do not expand the task to fit the skill.

## Final Check

Confirm that the packet describes the smallest useful result, includes every material
input, and excludes neighboring lifecycle stages. Split every uncertain boundary;
do not hide compound work in wording or metadata.
