# Atomicity And Alignment

Atomicity describes whether a proposed task contains one independently reviewable
concern.

## Split Test

Two concerns are independent when either concern can be assigned, rejected, retried,
completed, or verified without the other.

The test applies to analysis, documentation, implementation, and operations.

A lifecycle label, shared topic, desired packet size, file count, or available skill
is not a task boundary.

## One Result

One task has one purpose and one expected result.

The purpose names that result rather than naming a phase or a collection of actions.

The expected output describes the one deliverable produced by that purpose.

Several files may form one result when the coupling evidence is explicit.

One file may contain independent changes that require separate tasks.

## Verification Alignment

Verification is evidence about the task's result, not a second result hidden inside
the same task.

Every verification check addresses the deliverable named by the purpose and expected
output.

A separately reviewable verification artifact is a separate concern only when that
artifact is independently requested.

## Boundary Signals

- Several independently answerable questions indicate separate concerns.
- A final document does not merge independently reviewable findings into one task.
- Implementation and a separately requested test artifact have separate results.
- A dependency explains order and does not prove that concerns are inseparable.
- A shared file, topic, destination, release, or skill does not prove coupling.

The signals prompt boundary review; they do not replace evidence of the result and
its verification boundary.
