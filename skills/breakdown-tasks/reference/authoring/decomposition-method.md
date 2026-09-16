# Decomposition Method

<!-- markdownlint-disable MD013 -->

Use this operation-owned procedure after request normalization and before skill
assignment. It makes boundary reasoning inspectable by recording the work at each
pass. The loaded `task-contract` documentation skill remains authoritative for task
identity, atomicity, result and verification alignment, dependencies, coupling,
traceability, and authoring metadata; this method applies those semantics and does
not redefine them.

Keep the records together while drafting and retain them as one reviewer-visible
**publication-review evidence record** with the draft and published packet. The record
is durable review evidence, not packet fields, schema additions, validator inputs, or
runtime behavior; this workflow does not select a storage field or representation.

## Ordered Passes

1. **Normalize the request.** Record the requested outcome, explicit scope,
   constraints, exclusions, source inputs, requested deliverables or decisions, and
   observable completion evidence in a **normalized request record**. Separate
   explicit asks from inferred work and label every inference as an assumption.
   **Test:** every later concern can be traced to the request or a necessary stated
   constraint. **Disposition:** return materially ambiguous, missing, or conflicting
   outcome, scope, or completion evidence for clarification before boundary drafting;
   otherwise continue.

2. **Inventory concerns.** List each question, change, operation, decision,
   deliverable, and materially separate requested verification artifact in a
   **concern inventory** using the reusable
   [Concern and Boundary Record](concern-boundary-record.md); name the intended result
   and request/source trace for each concern. **Test:** a broad phrase, lifecycle
   label, final document, phase, topic,
   file, destination, skill, comma, or desired task count has not concealed or
   invented a boundary. **Disposition:** omit only explicitly out-of-scope work;
   otherwise add omitted concerns and expand concealed work into separate inventory
   entries.

3. **State candidate results.** For every inventory entry, write a **candidate-result
   record** identifying the result, necessary inputs, observable evidence, and a
   completion claim: “produce/assess/decide _X_ so that _Y_; complete when _Z_ is
   checkable.” **Test:** apply the shared independent-concern test and ask whether
   the entry has one inspectable result, one review boundary, closed inputs, a useful
   handoff, and no hidden work. **Disposition:** divide independently reviewable or
   multi-result work into concerns to reconsider; return missing inputs to
   normalization or relationship review; or mark one shared result for coupling
   review. Give it a stable candidate-result ID and retain its source trace and
   boundary-test answers in the publication-review evidence record.

4. **Propose boundaries and disposition each candidate result.** Group only the concerns that
   may produce one task result
   into a **candidate-boundary record** with its purpose, expected output, relevant
   inputs and outputs, and source traceability. **Test:** review the boundary using
   the shared atomicity-and-alignment reference without relying
   on a workflow phase, shared topic, file count, or desired packet size.
   **Disposition:** give every candidate result exactly one inspectable,
   outcome-linked disposition: **split** (its own task), **dependency** (a separate
   task with a named prerequisite), **integral evidence** (investigation or
   verification necessary for one stated result, not an independently reviewable
   result), **intentional exclusion** (with source-supported scope basis), or
   **retained coupling** (with all coupling facts). Split unsupported groupings and
   return the resulting concerns to pass 3; return an unmarked, absent, ambiguous,
   contradictory, unsupported-exclusion, or merged-independent result to the
   relevant earlier pass. Do not select skills, merge for a final document, or tune
   task count to resolve a boundary.

5. **Decide independence, order, and coupling.** Compare candidate boundaries using
   the loaded documentation skill's named **Atomicity and alignment** and
   **Dependencies and coupling** references and the
   [Dependency and Coupling Decisions](dependency-coupling-decisions.md) guide.
   Record each outcome in a **boundary-decision log** with its candidate-result ID,
   selected disposition, and evidence used. For every dependency,
   record predecessor, supplied item, consumer use, and readiness condition; a common
   source is shared input, not an edge. **Test:** independent work is not bundled,
   required order is represented as a usable dependency interface, and retained
   coupling states one shared result, one verification boundary, and why separation
   is unsafe, misleading, or impossible. **Disposition:** split and return to pass 3;
   add or revise a dependency, then return to pass 4; or reject unsupported coupling
   and split. Continue only with supported boundaries.

6. **Draft task records.** Review every compound signal using the decision guide and
   record its `split` or `retain` disposition. Then turn each retained boundary into
   a **draft-task record** using the
   [Packet Drafting and Traceability Checklist](packet-drafting-checklist.md)
   with its `taskId`, purpose, context, `filesToRead`, `filesToWrite`, execution
   instructions, expected output, `verificationCoverage`, dependencies,
   `antiPatternSignals`, and `purposeOutputAlignment`; record
   `couplingRationale` only when pass 5 supports it. Apply the loaded documentation
   skill's named **Traceability and metadata** reference for their meaning. **Test:**
   the record preserves its boundary decision, candidate-result disposition,
   traceability, result, and verification evidence. **Disposition:** send an
   incomplete or misaligned record back to the pass that supplies the missing
   reasoning. Do not add `skills`.

7. **Review boundary mappings.** Make a **boundary-mapping record** that maps every
   candidate result to one retained draft task, an explicit dependency, integral
   evidence for a named retained result, or an explained exclusion. **Test:** no
   candidate result is lost, duplicated, or covered by
   an unsupported compound task; identify predecessor artifacts where needed.
   **Disposition:** return uncovered or duplicated work to pass 2. Return invalid
   boundaries or dependency mappings to passes 4 or 5.

8. **Review the task set.** Produce a **set-review record** using the
   [Task-Set Review protocol](task-set-review.md), covering all draft-task
   records, boundary decisions, dependencies, traceability, verification coverage,
   and the publication-review evidence record. **Test:** each draft is independently reviewable under the shared
   contract, every concern is covered once or intentionally excluded, no independent
   result is merged only for synthesis, dependency interfaces are usable and ordered,
   shared inputs are not edges, every candidate result has exactly one supported,
   inspectable disposition, unresolved boundaries are named, and no assignment has
   influenced a boundary. **Disposition:** rework the affected record through the
   earliest corrective pass, then repeat passes 6 through 8 after every split, merge,
   or relationship change. **Stop point:** proceed to the separate skill-assignment
   procedure only when the set-review record passes; otherwise do not assign skills
   or report semantic atomicity assessment.

Use the [Worked Decomposition Examples](decomposition-examples.md) to calibrate the
complete record sequence, failure routes, and retained-coupling exception without
turning an example into a new semantic rule.

## Rework Loop

Any split, dependency revision, coupling rejection, missing traceability, or failed
set review returns to the named earlier pass. Preserve the prior record and decision
reason so the rework is inspectable. Re-run the affected later passes through the
set review before entering skill assignment. This loop changes authoring records
only;
it does not introduce packet fields, task-count rules, validation behavior, or
enforcement.
