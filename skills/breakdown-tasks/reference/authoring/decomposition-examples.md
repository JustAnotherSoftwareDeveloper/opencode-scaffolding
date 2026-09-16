# Worked Decomposition Examples

<!-- markdownlint-disable MD005 MD007 MD013 -->

These worked records apply the [decomposition method](decomposition-method.md).
They are authoring evidence, not packet schema, validation input, or runtime
behavior. The loaded `task-contract` documentation skill remains authoritative.

## Mixed Request: Complete Records

### Exact Mixed Request

> Research the migration risks, decide whether a compatibility bridge is needed,
> write a proposal, implement the approved bridge, and provide a separate validation
> report. Run relevant regression coverage as part of implementing it. Put the
> research, decision, and proposal in `docs/migration-bridge.md`.

### Normalized Request And Inventory

- **C1 — Research migration risks:** inspectable risk assessment.
- **C2 — Decide whether a compatibility bridge is needed from the assessment:**
  inspectable decision.
- **C3 — Write a proposal from the decision:** inspectable proposal.
- **C4 — Implement the approved bridge after the decision:** code change.
- **C5 — Run relevant regression coverage:** evidence for C4's code result.
- **C6 — Deliver a validation report:** separately requested report.

The shared destination is a compound signal, not a result: C1, C2, and C3 remain
separate contributions even though they will occupy sections of the same document.

### Concern Records

#### Concern: Research Migration Risks (C1)

- **Inventory trace:** Exact request, first sentence.
- **Proposed result:** A written assessment of migration risks.
- **Result evidence:** The research section in `docs/migration-bridge.md` identifies
  material risks and supporting sources.
- **Relevant inputs:** Migration implementation and relevant tests.
- **Boundary-test answers:**
  - **Independence:** It can be reviewed, rejected, or retried without choosing a
    bridge or changing code.
  - **One result:** The assessment is one analytical result with review of its
    evidence.
  - **Order:** None.
  - **Coupling:** No; its shared document destination does not make it the same
    result as the decision or proposal.
- **Completion claim:** The migration-risk assessment is available for later decision-making.
- **Disposition — select exactly one:**
  - [x] **Standalone:** Retain as `T1`; the assessment is independently reviewable.
  - [ ] **Prerequisite-linked:**
  - [ ] **Excluded with basis:**
  - [ ] **Retained coupled:**

#### Concern: Decide Whether A Compatibility Bridge Is Needed (C2)

- **Inventory trace:** Exact request, second clause.
- **Proposed result:** A compatibility-bridge decision with its rationale.
- **Result evidence:** The decision section states whether a bridge is needed and cites the
  assessment that supports it.
- **Relevant inputs:** `docs/migration-bridge.md` research section produced
  by T1.
- **Boundary-test answers:**
   - **Independence:** The decision can be reviewed or revised separately from the
     assessment and from a proposal.
  - **One result:** It is one decision and one decision-review boundary.
  - **Order:** T1 supplies the assessment needed to decide.
  - **Coupling:** No; needing an assessment creates an ordered interface, not one
    shared result.
- **Completion claim:** A decision is available for proposal and implementation.
- **Disposition — select exactly one:**
   - [ ] **Standalone:**
   - [x] **Prerequisite-linked:** T1 supplies the assessment; the bridge decision
    uses it when the assessment section is complete and reviewable.
  - [ ] **Excluded with basis:**
  - [ ] **Retained coupled:**

#### Concern: Write Proposal (C3)

- **Inventory trace:** Exact request, "write a proposal" clause.
- **Proposed result:** A proposal for the selected compatibility-bridge decision.
- **Result evidence:** The proposal section states the recommended bridge work and refers to the
  selected decision.
- **Relevant inputs:** T2's decision section in `docs/migration-bridge.md`.
- **Boundary-test answers:**
   - **Independence:** It can be accepted or revised separately from selecting the
     bridge and from making the code change.
   - **One result:** The proposal is one document contribution with its own
    review boundary.
   - **Order:** T2 supplies the bridge decision; the proposal can proceed when that
     decision and rationale are recorded.
  - **Coupling:** No; a final/shared document does not make decision and proposal one
    result.
- **Completion claim:** A reviewable proposal is available.
- **Disposition — select exactly one:**
   - [ ] **Standalone:**
   - [x] **Prerequisite-linked:** T2 supplies the bridge decision and rationale.
  - [ ] **Excluded with basis:**
  - [ ] **Retained coupled:**

#### Concern: Implement Approved Bridge (C4)

- **Inventory trace:** Exact request, "After the decision, implement" clause.
- **Proposed result:** The approved compatibility bridge implemented in migration code.
- **Result evidence:** The code diff implements the decision and regression coverage
  passes as verification evidence for that change.
- **Relevant inputs:** T2's bridge decision in `docs/migration-bridge.md`;
  implementation and regression sources.
- **Boundary-test answers:**
  - **Independence:** It can be reviewed or retried as a code result separately from
    the proposal and validation report.
  - **One result:** The code change is one result; running regression coverage checks
    that result and is not a second deliverable.
   - **Order:** T2 supplies the approved bridge decision; implementation begins when
     the decision identifies the bridge to implement.
  - **Coupling:** No retained coupling with C5: C5 is verification coverage of this
    same result, not a separately requested artifact.
- **Completion claim:** The approved bridge is implemented with regression evidence.
- **Disposition — select exactly one:**
   - [ ] **Standalone:**
   - [x] **Prerequisite-linked:** T2 supplies the bridge decision needed by the code
    change.
  - [ ] **Excluded with basis:**
  - [ ] **Retained coupled:**

#### Concern: Run Regression Coverage (C5)

- **Inventory trace:** Exact request, "Run the relevant regression coverage" clause.
- **Proposed result:** Verification coverage for C4's implementation result, not a
  new artifact.
- **Result evidence:** T4 records the executed relevant regression coverage and its
  result in its verification coverage.
- **Relevant inputs:** T4's implementation result and relevant test suite.
- **Boundary-test answers:**
  - **Independence:** It is not independently requested as a report or other
    deliverable; it is evidence about C4.
  - **One result:** It verifies the implementation result rather than producing a
    separate completion claim.
  - **Order:** It occurs while completing T4; no predecessor task artifact is needed.
  - **Coupling:** No coupling decision is needed; this is verification coverage, not
    a concern retained as a task.
- **Completion claim:** T4's implementation claim is supported by regression
  evidence.
- **Disposition — select exactly one:**
  - [ ] **Standalone:**
  - [ ] **Prerequisite-linked:**
  - [x] **Excluded with basis:** C5 maps to T4 verification coverage because the
    request does not ask for an independently reviewable verification artifact.
  - [ ] **Retained coupled:**

#### Concern: Deliver Validation Report (C6)

- **Inventory trace:** Exact request, final clause.
- **Proposed result:** A validation report describing the regression run and result.
- **Result evidence:** A report artifact contains the run description and outcome.
- **Relevant inputs:** T4's completed implementation and recorded regression result.
- **Boundary-test answers:**
  - **Independence:** The request expressly makes this report independently
    reviewable; it can be rejected or revised without redoing the implementation.
  - **One result:** The report is one artifact with report-specific review.
  - **Order:** T4 supplies the implementation and regression outcome; the report is
    ready when those facts are available.
  - **Coupling:** No; verification evidence within T4 does not absorb a separately
    requested report.
- **Completion claim:** A validation report is delivered.
- **Disposition — select exactly one:**
  - [ ] **Standalone:**
  - [x] **Prerequisite-linked:** T4 supplies the implementation and recorded run
    outcome used by the report.
  - [ ] **Excluded with basis:**
  - [ ] **Retained coupled:**

### Boundary Decisions, Handoffs, And Packet Decisions

- **C1, C2, and C3 share `docs/migration-bridge.md` — Split.** A shared
  destination is not one shared result; research, decision, and proposal have
  separate completion claims.
- **C1 → C2 — Dependency.** Predecessor: T1. Supplied item: migration-risk
  assessment. Consumer use: bridge decision. Readiness: research section is complete
  and reviewable. T2 reads the document.
- **C2 → C3 — Dependency.** Predecessor: T2. Supplied item: bridge decision and
  rationale. Consumer use: proposal. Readiness: decision section is recorded. T3
  reads the document.
- **C2 → C4 — Dependency.** Predecessor: T2. Supplied item: approved bridge
  decision. Consumer use: code implementation. Readiness: decision identifies the
  bridge. T4 reads the document.
- **C4 and C5 — Verification coverage.** Retain C5 as verification coverage, not a
  task. Regression evidence addresses T4's one code result; no separate artifact was
  requested.
- **C4 → C6 — Dependency.** Predecessor: T4. Supplied item: implementation and
  recorded regression outcome. Consumer use: validation report. Readiness:
  implementation and result are available. T5 reads the implementation outcome
  record.

The resulting draft packet decisions are: T1 assessment; T2 decision (depends on
T1); T3 proposal (depends on T2); T4 implementation (depends on T2 and includes C5
in `verificationCoverage`); and T5 validation report (depends on T4). Each packet
has one purpose, expected output, completion claim, and aligned verification. The
shared document is listed where material, but creates neither a merge nor an edge by
itself.

### Completed Set-Review Record

- **Reviewed records:** the normalized request, C1–C6 concern records, the boundary
  decisions above, the T1–T5 mapping, and the listed dependency interfaces.
- **Coverage and intentional exclusion:** **pass.** C1–C4 and C6 map once to T1–T5;
  C5 has the explicit verification-coverage exclusion.
- **No duplicate or synthesis-only merges:** **pass.** The shared destination did
  not merge C1–C3; no task claims another task's result.
- **One completion claim per task:** **pass.** T4's regression run is evidence for
  the implementation, while T5 owns the separately requested report.
- **Usable interfaces:** **pass.** Every dependency names predecessor, supplied item,
  consumer use, readiness condition, and the consumer reads the required artifact.
- **Order without false edges:** **pass.** The document destination is only shared
  input; all edges carry a supplied result.
- **Signal disposition:** **pass.** Shared destination and verification/report
  signals have recorded split or exclusion dispositions; no coupling is asserted.
- **Disposition:** **pass;** the draft set may proceed to the separate assignment
  procedure.

## Coupled Source And Generated-Client Exception

### Coupled-Exception Request

> Change the source API schema for the `deliveryWindow` field and regenerate the
> checked-in client.

### Retained-Coupling Record

The source-schema edit and checked-in generated client are retained in one packet
only for these three facts:

1. **One shared result:** the repository's source schema and checked-in client form
   one reproducible API-client change, rather than two independently useful results.
2. **One verification boundary:** generation and the relevant client checks verify
   that the checked-in client corresponds to that source schema as one result.
3. **Unsafe, misleading, or impossible separation:** separating the schema edit from
   its required checked-in generated client would leave a repository state in which
   the source contract and shipped client disagree; reviewing or retrying either side
   alone would misrepresent that reproducible change.

**Packet decision:** retain one coupled task whose purpose and expected output are the
reproducible source-schema-plus-generated-client change. Its `couplingRationale`
records the three facts above, and its verification covers regeneration and the
source/client correspondence. This exception does not derive from having multiple
files or from a generation tool alone.

### Contrasts That Fail Retention

- **Both edits touch `api/schema.yaml` — Split.** A shared file is shared input; it
  does not establish one result, one verification boundary, and separation risk.
- **Both contributions ship in one release — Split.** A release is a destination or
  lifecycle signal, not coupling evidence.
- **Put analysis and a decision in the final document — Split.** A final document
  does not merge independently reviewable findings or decisions.
- **Use the same skill for analysis and implementation — Split.** A common available
  skill cannot shape the task boundary.

## Failure And Rework Record

### Failed Review: False Shared-Destination Merge

- **Drafted boundary:** One task titled “Complete migration bridge document”
  combining C1, C2, and C3 because all write to
   `docs/migration-bridge.md`.
- **Failure:** The boundary has separate assessment, decision, and proposal results;
  its title and destination conceal the separate completion claims. The shared file
  supplies no coupling evidence.
- **Failed set-review checks:** No duplicate or synthesis-only merges — **fail**;
  one completion claim per task — **fail**; signal disposition — **fail**.
- **Rework route:** Return to decomposition-method pass 4, **Propose boundaries**;
  split C1–C3, then redo relationship decisions, draft records, boundary mapping, and
  the complete set review.
- **Preserved outcome:** The failed boundary is retained as review evidence; it is not
  repaired by changing packet wording or by selecting a skill.

### Rework Completion

The split records and dependency interfaces in the mixed example are the rerun
result. The completed set-review record above passes after mapping C1 to T1, C2 to
T2, and C3 to T3 and recording the actual handoffs. No numerical limit, runtime
diagnostic, or new semantic rule is introduced by this example.

### Failed Review: Unresolved Prompt Ambiguity

- **Observed record:** “Improve migration behavior” names no outcome, affected scope,
  or completion evidence.
- **Failed test:** Pass 1 cannot trace later concerns to a requested result and cannot
  distinguish a code change from analysis or a decision.
- **Rework route:** Pause before boundary drafting and return to pass 1,
  **Normalize the request**, for clarification of outcome, scope, and evidence.
- **Corrected disposition:** Resume pass 2 only after the normalized request records
  the clarified result; rerun all later passes.

### Failed Review: Underspecified Candidate

- **Observed record:** “Choose the bridge” names a decision but has no migration-risk
  assessment or other decision input.
- **Failed test:** Pass 3 cannot state closed material inputs or an honest completion
  claim for the candidate decision.
- **Rework route:** Return to pass 1 when the input is absent from the request, or pass
  5 when another candidate must supply it through a dependency interface.
- **Corrected disposition:** Record the assessment as a prerequisite with a readiness
  condition, then rerun passes 4–8.

### Failed Review: Unsupported Retention

- **Observed record:** Analysis and implementation are retained together because one
  skill can perform both and both affect the same release.
- **Failed test:** The rationale states neither one shared result nor one verification
  boundary, and separation is not unsafe, misleading, or impossible.
- **Rework route:** Return to pass 5, reject the coupling, split the concerns, and add
  a dependency only if implementation consumes an approved analytical result.
- **Corrected disposition:** Preserve separate completion claims and rerun passes
  6–8.

### Failed Review: Opaque Dependency

- **Observed record:** T2 “depends on T1” without a supplied item, consumer use, or
  readiness condition.
- **Failed test:** Pass 5 cannot distinguish a real handoff from topical order or a
  shared input.
- **Rework route:** Return to pass 5. If T1 supplies no result consumed by T2, remove
  the edge and record shared input. Otherwise name the supplied item, consumer use,
  readiness condition, and consumer read path.
- **Corrected disposition:** Rerun passes 6–8 after recording or removing the edge.

<!-- markdownlint-enable MD013 -->
