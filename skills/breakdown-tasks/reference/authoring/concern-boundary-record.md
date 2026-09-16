# Concern And Boundary Record

<!-- markdownlint-disable MD013 -->

Use one compact record for each normalized inventory concern while applying the
[decomposition method](decomposition-method.md). This is human authoring evidence,
not a task packet schema, validator input, or runtime instruction. The loaded
`task-contract` documentation skill's named **Atomicity and alignment** and
**Dependencies and coupling** references remain authoritative.

Keep one completed record per candidate result. A reviewer must be able to see one,
and only one, selected outcome-linked disposition for every candidate result in the
publication-review evidence record.

## Reusable Record

```markdown
### Concern: CONCERN_NAME

- **Inventory trace:** REQUEST_SOURCE_OR_INVENTORY_ID
- **Candidate-result ID:** STABLE_REVIEW_ID
- **Proposed result:** ONE_INSPECTABLE_RESULT
- **Result evidence:** OBSERVABLE_REVIEW_EVIDENCE
- **Relevant inputs:** NONE_OR_MATERIAL_INPUTS
- **Boundary-test answers:**
  - **Independence:** INDEPENDENCE_ANSWER_AND_EVIDENCE
  - **One result:** ONE_RESULT_AND_VERIFICATION_BOUNDARY_ANSWER
  - **Order:** NONE_OR_PREDECESSOR_AND_REQUIRED_ARTIFACT
  - **Coupling:** NO_OR_SHARED_RESULT_VERIFICATION_AND_SEPARATION_RISK
- **Completion claim:** REVIEWABLE_COMPLETION_CLAIM
- **Outcome-linked disposition — select exactly one:**
  - [ ] **Split:** INDEPENDENT_RESULT_AND_OWN_TASK_BASIS
  - [ ] **Dependency:** PREDECESSOR_ARTIFACT_CONSUMER_USE_AND_READINESS
  - [ ] **Integral evidence:** NAMED_RETAINED_RESULT_AND_WHY_NOT_INDEPENDENT
  - [ ] **Intentional exclusion:** EXCLUSION_AND_SOURCE_BASIS
  - [ ] **Retained coupling:** SHARED_RESULT_VERIFICATION_AND_SEPARATION_RISK
```

## Filling Guidance

- **Concern and inventory trace:** Normalize the concern to reviewable work and
  identify where it arose. This lets the boundary mapping in the decomposition
  method show that no inventory concern disappeared or was duplicated.
- **Proposed result and result evidence:** Name the single inspectable outcome, not a
  lifecycle phase, broad topic, or a list of actions. State the evidence a reviewer
  can inspect for that outcome.
- **Relevant inputs:** List only material sources and constraints. For ordered work,
  name the predecessor's produced artifact; order alone is not coupling.
- **Boundary-test answers:** Answer each question briefly with evidence. Apply the
  shared atomicity test to independence and one-result review; apply the shared
  dependency/coupling semantics to order and coupling. Shared files, topics,
  destinations, skills, or a final document are not coupling evidence by themselves.
- **Completion claim:** State the outcome that can honestly be claimed complete after
  this concern's disposition. It must match the proposed result, or, for exclusion,
  state that the exclusion and its basis were reviewed.

## Disposition Rules

Select exactly one disposition; do not leave a candidate result unclassified or mark
multiple outcomes. Missing, ambiguous, or contradictory evidence leaves the boundary
unresolved and prevents an atomicity-assessed semantic review outcome, even if the
packet is structurally valid.

- **Split** applies when the candidate produces its own result and can be independently
  reviewed. Record why the independence and one-result tests pass and map it to its
  own task.
- **Dependency** applies when the candidate remains separate but needs another result
  first. Record the predecessor, required artifact, consumer use, and readiness
  condition. A
  dependency explains sequence; it does not combine concerns.
- **Integral evidence** applies when research, investigation, or verification is
  necessary to produce or verify one named retained result and is neither separately
  requested nor independently reviewable. Name that result and its verification
  boundary; multi-action wording alone is not evidence of another result.
- **Intentional exclusion** applies only when the candidate will not be retained. Record a
  specific scope decision, duplicate destination, unavailable input, or other
  reviewable basis, together with the source that supports it. Do not use exclusion
  to hide unresolved work.
- **Retained coupling** applies only when the concerns share one result and one
  verification boundary *and* separation would be unsafe, misleading, or impossible.
  Record evidence for all three conditions and identify the coupled concern(s). If
  either concern can be independently assigned, rejected, retried, completed, or
  verified, retain separate records instead.

Before moving on, scan the complete inventory: every candidate result must have its
own visible record and exactly one checked disposition. Use the decomposition method's
boundary mapping and set review for the later cross-record and publication review.
