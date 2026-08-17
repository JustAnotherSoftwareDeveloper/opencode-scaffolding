# Task Granularity

Choose boundaries from independent work, not file count or workflow stages.

## Start With An Inventory

List each requested question, change, operation, decision, and deliverable. Include
concealed concerns that appear inside broad phrases such as “finish the migration”
or “update the feature.”

## Apply The Split Test

For every pair of concerns, ask whether either can be:

- assigned to a different worker;
- rejected without rejecting the other;
- retried without repeating the other;
- completed without completing the other; or
- verified without verifying the other.

Split when any answer is yes. Prefer an extra explicit dependency over an implicit
compound task.

## Preserve Only One Shared Result

Keep work together only when it satisfies the coupling requirements in
[Core Rules](core-rules.md). One file can contain several independent changes.
Several files can form one result. File count is only a review signal.

## Recheck The Boundary

After each split, confirm that:

- `purpose` names one result;
- `expectedOutput` describes that result;
- verification checks that result;
- dependencies identify predecessor tasks and artifacts; and
- assigned skills match the final boundary.

Do not use punctuation, lifecycle order, or skill availability as proof. Do not
introduce universal task, file, step, or skill limits.
