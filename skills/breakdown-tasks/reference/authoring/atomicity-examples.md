# Atomicity Examples

Use these examples to review a proposed boundary. They illustrate the rules. They
do not replace judgment.

## Independent Analysis

**Request:** Assess authentication design and dependency risk.

- Split into two tasks.
- Each assessment produces an independently reviewable finding.
- Add a later synthesis task only when the user requests one combined conclusion.

## One Analytical Result

**Request:** Produce one threat model for the login flow, including dependency attack
paths.

- Keep the work together.
- The shared result is one threat model.
- One review verifies the complete threat boundary.

## Implementation And Verification

**Request:** Change cache invalidation and confirm the regression suite passes.

- Keep the test run as verification of the implementation result.
- Split only when the user requests a separately owned test artifact or report.

## Independent Documentation

**Request:** Revise the API reference and change the deprecation policy.

- Split into two tasks.
- The documents have separate owners, review decisions, and results.

## Coupled Generated Output

**Request:** Change a source schema and regenerate its checked-in client.

- Keep the source and generated output together.
- The shared result is one reproducible generated package.
- The generator check verifies the complete result.

## Ordered Separate Work

**Request:** Analyze migration risk, then write a proposal from the analysis.

- Create an analysis task and a dependent proposal task.
- Put the analysis artifact in the proposal task's `filesToRead`.
- The dependency establishes order, not coupling.
