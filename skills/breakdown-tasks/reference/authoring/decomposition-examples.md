# Worked Decomposition Examples

These examples apply the shared `task-contract` semantics through the
[decomposition method](decomposition-method.md). They show how to make a problem
smaller, connect the tasks, and stop before creating procedural fragments.

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
3. **Create the session-audit skill.**
   This task consumes the contract, authors and validates the workspace.

The first task is separate because its finding can be reviewed or retried without
creating the skill. The second is separate when choosing the audit contract is a
material decision rather than routine authoring. The validators remain inside the
creation task because they check the created skill and produce no separate requested
result.

## Documentation Lookup Inside One Task

**Request:** Add the already-specified `timeout` option using the documented parser
API and run the parser tests.

Keep one implementation task. Reading the parser documentation is an internal step:
the required behavior is already defined, the lookup does not establish a reusable
finding, and the tests verify the same code result.

## Analysis Followed By A Proposal

**Request:** Analyze migration risk, then propose whether to add a compatibility
bridge.

Create two tasks:

1. Produce the migration-risk assessment.
2. Produce the bridge proposal from that assessment.

The proposal depends on the assessment. Record the assessment as the supplied item,
explain how the proposal uses it, and begin only when the assessment is complete
enough to support a decision. Sequence does not merge the results.

## Independent Findings In One Report

**Request:** Assess authentication design and dependency risk in one report.

Create one task for each assessment because either finding can be reviewed or retried
without the other. Add a dependent synthesis task only if producing the combined
report is itself requested work. A shared destination is not a shared result.

## Coupled Source And Generated Output

**Request:** Change the source API schema and regenerate the checked-in client.

Keep one task when the source and generated client form one reproducible repository
state, generation and correspondence provide one verification boundary, and
separating them would leave the checked-in client inconsistent with its source.
“Same release” or “same tool” would not be enough.

## Stopping Contrast

Do not turn one bounded implementation result into separate tasks to read a file,
edit the code, run tests, and report completion. Those are procedural steps. Split
only when an activity produces another useful result, decision, change, or
deliverable with its own acceptance or retry boundary.
