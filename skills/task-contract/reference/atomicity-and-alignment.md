# Atomicity And Alignment

An atomic task is one bounded piece of a problem. It produces one result that a
worker can complete and verify.

## Split Rule

A valid decomposition derives smaller required results from the requested outcome.
Any proposed result that still contains separate questions, decisions, changes,
or deliverables is not yet atomic.

Required predecessor results are treated as fixed and available when testing a
boundary. Two results are separate when either can then be accepted, rejected,
retried, completed, or verified without redoing the other. A dependency preserves
order; it does not make the results one task.

Apply this rule to analysis, documentation, implementation, and operations. Do not
derive a boundary from file count, wording, workflow phase, available skill, or
desired task count.

## One Result

One task has one purpose, one expected result, and one completion decision. Internal
steps may read sources, make edits, and run checks when all of those actions produce
or verify that same result.

A proposed task requires splitting when it contains:

- separately answerable questions;
- a finding or decision consumed by later work;
- changes that can be accepted or retried separately;
- independently useful deliverables; or
- an investigation whose answer determines the scope, design, interface, or
  acceptance criteria of later work.

An intermediate result can be a real task even when the user did not request a
separate document. A necessary predecessor provides a concise handoff to its
consumer.

## Keep Rule

Activities remain together when separation would only fragment how one bounded
result is produced or checked. Multiple files may implement one behavior. Research
may remain internal when it only supports an already-defined result and does not
establish a reusable finding or alter downstream work.

Multiple apparent results belong together only when they share one useful result
and one verification boundary, and separation would leave an invalid, misleading,
or unsafe state. A shared topic, file, final document, release, skill, or dependency
is not enough.

## Verification Alignment

Verification checks the task's result. Ordinary tests, validators, or lint belong
with the result being checked. Create a separate verification task only when it
produces an independently requested or reviewable result, such as an audit finding,
approval, or report.

## Stopping Rule

Splitting stops when the task has one result, known inputs, a clear stopping
condition, and an observable completion check. Further splits that create only
procedural fragments are not valid task boundaries.
