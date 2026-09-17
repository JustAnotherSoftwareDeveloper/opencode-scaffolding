# Packet Drafting And Traceability Checklist

Use this checklist after the decomposition method produces final task results and
before skill assignment. The task schema controls packet structure; the loaded
`task-contract` documentation defines field meaning.

## Per-Task Checklist

1. Give the task a stable `taskId` and state one result in `purpose` and
   `expectedOutput`.
2. Put the task-specific request facts, constraints, exclusions, and required prior
   decisions in `context`.
3. List source files and predecessor file handoffs in `filesToRead`; list only the
   task's write boundary in `filesToWrite`.
4. Write concrete execution instructions that produce the one result. Keep ordinary
   checks with the result they verify.
5. Record observable completion in `verificationCoverage` and align it with the
   purpose and expected output.
6. For each dependency, identify the predecessor, supplied result, consumer use,
   and readiness condition. A dependency does not repair a compound task.
7. Use `couplingRationale` only when one result and one verification boundary require
   multiple inseparable changes.
8. Keep the boundary unchanged during skill assignment. A skill must fit the task;
   the task must not expand to fit a skill.

## Final Check

Confirm that the packet describes one result, includes every material input, and
excludes neighboring results. Return compound tasks or procedural fragments to the
decomposition method rather than hiding them in wording or metadata.
