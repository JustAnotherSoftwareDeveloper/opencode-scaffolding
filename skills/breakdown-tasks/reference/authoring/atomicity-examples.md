# Atomicity Examples

Use these operation examples with the loaded `task-contract` documentation skill's
named **Atomicity and alignment** reference to review a proposed boundary. They
illustrate decomposition choices; they do not define shared semantics or replace
judgment.

## Independent Analysis

**Request:** Assess authentication design and dependency risk.

- Draft two task boundaries for the independently requested assessments.
- Add a later synthesis task only when the user requests one combined conclusion.
- **Publication-review dispositions:** `auth-design` — **split**, because it can be
  reviewed and rejected apart from dependency risk; `dependency-risk` — **split** for
  the same independently reviewable-result evidence. A shared final report would not
  change either disposition.

## One Analytical Result

**Request:** Produce one threat model for the login flow, including dependency attack
paths.

- Draft one task for the requested threat model and review it with the shared
  one-result and verification-alignment contract.
- **Publication-review disposition:** `dependency-attack-paths` — **integral
  evidence** for the one threat-model result. The paths are investigated to support
  that analysis and are not separately requested or independently reviewable. The
  multi-action wording “model ... including paths” does not itself require a split.

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
- **Publication-review disposition:** **retained coupling** only when the evidence
  states all three facts: one reproducible source-and-client result, one generation
  and correspondence verification boundary, and the risk that separating them leaves
  a mismatched shipped state. “Same file,” “same skill,” “must run after,” or “same
  release/final document” are rejected proxy rationales, not retained-coupling facts.

## Ordered Separate Work

**Request:** Analyze migration risk, then write a proposal from the analysis.

- Draft an analysis task and a dependent proposal task.
- Put the analysis artifact in the proposal task's `filesToRead`, following the
  shared dependency and traceability contract.
- **Publication-review disposition:** `migration-risk analysis` — **split**; `write
  proposal` — **dependency**, naming the analysis artifact, consumer use, and
  readiness condition. Order does not make them one result.

## Structurally Valid But Semantically Unresolved

**Candidate:** One schema-valid packet says “assess risks and decide the bridge,” with
aligned-looking purpose/output metadata but no candidate-result records.

- **Publication-review outcome:** **structural-only, not atomicity-assessed.** The
  reviewer records the absent dispositions for `risk-assessment` and `bridge-decision`
  as the unresolved boundaries and returns to candidate-result and boundary review.
- The same outcome applies when a record both calls the decision independent and
  integral, or retains it because of only a shared document. No structural proxy
  repairs absent, ambiguous, or contradictory semantic evidence.
