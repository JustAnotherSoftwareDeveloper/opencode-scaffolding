# Atomicity And Alignment

Atomicity describes whether a proposed task contains one independently reviewable
concern.

## Split Test

Two concerns are independent when either concern can be assigned, rejected, retried,
completed, or verified without the other.

The test applies to analysis, documentation, implementation, and operations.

A lifecycle label, shared topic, desired packet size, file count, or available skill
is not a task boundary.

## Required Outcome-Linked Disposition

Before a task boundary is treated as atomicity-assessed, every independently
reviewable candidate result has exactly one inspectable disposition linked to that
result:

- **Split:** the candidate has its own task because it can be independently assigned,
  rejected, retried, completed, or verified.
- **Integral evidence for one result:** the candidate is investigation, research, or
  other evidence necessary to produce or verify the one stated result; it is not a
  separately requested or independently reviewable result.
- **Intentional exclusion:** the candidate is explicitly outside the stated result
  and task scope; the record identifies what is excluded and why it is not part of
  the result.
- **Retained coupling:** the candidate remains with another concern only when the
  coupling evidence states one shared result, one verification boundary, and the
  risk that separation would create.

These are semantic dispositions, not packet fields, schema requirements, or runtime
behavior. A multi-action phrase alone does not establish multiple candidate results,
and research integral to one analysis result does not require a split.

Missing, ambiguous, or contradictory disposition evidence leaves the boundary
unresolved. It is not semantic approval that atomicity was assessed.

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

Dependencies, shared files, skills, ordering, final documents, and lifecycle labels
may describe context or structure, but none is a rationale for retained coupling.
