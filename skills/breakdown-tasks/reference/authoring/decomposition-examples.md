# Worked Decomposition Examples

These examples apply the shared `task-contract` semantics through the
[decomposition method](decomposition-method.md). They show how to make a problem
smaller, connect the tasks, and prefer fine-grained handoffs over compound work.

## Research That Determines Later Work

**Request:** Research the available OpenCode session evidence, then create an
operation skill for auditing sessions.

An incorrect one-task breakdown is “research and create a validated session-audit
skill.” It hides a prerequisite finding inside implementation merely because both
activities contribute to one final skill.

Break the request down:

1. **Establish session evidence and audit limitations.** The result is a concise
   finding that identifies usable session artifacts, access methods, and evidence
   gaps.
2. **Define the session-audit skill contract.** This task consumes the finding and
   decides the audit input, checks, report shape, constraints, and completion rules.
3. **Create the session-audit skill.** This task consumes the contract and authors
   the workspace.
4. **Validate the session-audit skill.** This task consumes the authored workspace
   and reports whether it satisfies the contract and repository checks.

The first task is separate because its finding can be reviewed or retried without
creating the skill. Contract definition, workspace creation, and validation are also
separate because each has a distinct completion decision. The user does not need to
request those intermediate handoffs explicitly.

## Known-Source Lookup Inside One Task

**Request:** Add the already-specified `timeout` option using the documented parser
API and run the parser tests.

Reading the already-identified parser documentation may remain an implementation
step because it discovers neither the relevant source nor a new decision. Create a
separate verification task for the parser tests because they can run against the
fixed implementation and independently accept or reject it.

## Analysis Followed By A Proposal

**Request:** Analyze migration risk, then propose whether to add a compatibility
bridge.

Create at least two tasks:

1. Produce the migration-risk assessment.
2. Produce the bridge proposal from that assessment.

If collecting migration evidence and analyzing it are independently meaningful,
split those too. The proposal depends on the assessment. Record the assessment as
the supplied item, explain how the proposal uses it, and begin only when the
assessment is complete enough to support a decision. Sequence does not merge the
results.

## Independent Findings In One Report

**Request:** Assess authentication design and dependency risk in one report.

Create one task for each assessment because either finding can be reviewed or retried
without the other. Add a dependent synthesis task only if producing the combined
report is itself requested work. A shared destination is not a shared result.

## Coupled Source And Generated Output

**Request:** Change the source API schema and regenerate the checked-in client.

Keep one implementation task only when the source and generated client form one
indivisible repository state and separating their production would leave the
checked-in client inconsistent with its source. Put independently executable
correspondence checks in a dependent verification task.
“Same release” or “same tool” would not be enough.

## Aggressive Stopping Contrast

An explicitly known file read may stay with the task that uses it. Source discovery,
a finding derived from the source, a decision based on that finding, the resulting
edit, and independently executable tests are separate tasks. If it is unclear whether
an action produces a handoff, split it and state the smallest useful handoff.
