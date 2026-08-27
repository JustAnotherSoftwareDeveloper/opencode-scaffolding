# Atomicity Examples

Use these operation examples with the shared
[atomicity and alignment contract](../../../task-contract/reference/atomicity-and-alignment.md)
to review a proposed boundary. They illustrate decomposition choices; they do not
define shared semantics or replace judgment.

## Independent Analysis

**Request:** Assess authentication design and dependency risk.

- Draft two task boundaries for the independently requested assessments.
- Add a later synthesis task only when the user requests one combined conclusion.

## One Analytical Result

**Request:** Produce one threat model for the login flow, including dependency attack
paths.

- Draft one task for the requested threat model and review it with the shared
  one-result and verification-alignment contract.

## Implementation And Verification

**Request:** Change cache invalidation and confirm the regression suite passes.

- Keep the test run in the implementation task's verification coverage.
- Split only when the user requests a separately owned test artifact or report.

## Independent Documentation

**Request:** Revise the API reference and change the deprecation policy.

- Draft two task boundaries for the separately requested documents.

## Coupled Generated Output

**Request:** Change a source schema and regenerate its checked-in client.

- Keep source and generated output in one task only when the shared coupling contract
  supports one reproducible result and one verification boundary.

## Ordered Separate Work

**Request:** Analyze migration risk, then write a proposal from the analysis.

- Draft an analysis task and a dependent proposal task.
- Put the analysis artifact in the proposal task's `filesToRead`, following the shared
  dependency and traceability contract.
