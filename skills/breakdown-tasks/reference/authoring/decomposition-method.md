# Decomposition Method

Use this method after request normalization and before skill assignment. Turn one
requested outcome into the smallest useful results, then connect those results so
workers can complete the whole request. Deliberately over-split rather than risk
a compound assignment.

The loaded `task-contract` documentation skill owns task identity, atomicity,
dependencies, coupling, traceability, and verification meaning. This method applies
that contract.

## Procedure

1. **Name the requested outcome.** Record what the user wants to be true or delivered,
   along with explicit scope, constraints, source inputs, exclusions, and completion
   evidence. Ask for clarification only when missing information changes the outcome
   or prevents a usable breakdown.

2. **Create the request-result inventory.** For every applicable packet, retain
   a boundary-review record alongside the draft and canonical packet. Its request-result
   inventory lists every discovery, evidence collection,
   question, analysis, finding, decision, recommendation, authored artifact, change,
   verification, review, and report needed for the outcome. Treat each action verb
   and each distinct object as a candidate. Work backward from the requested outcome:
   ask what must already be known, decided, or available before each candidate can
   be produced. Include intermediate results even when the user requested only one
   final deliverable.

3. **Make and record the fixed-predecessor split decision.** Begin with one task
   per candidate. For every proposed task, hold predecessor outputs fixed and
   available,
   map the task to one immediate result, and record whether the candidate is `split`
   or `accepted-indivisible`. Then ask:

   - Does it still contain another substantial question, decision, change, or
     deliverable?
   - With predecessor outputs held fixed, can part of it be accepted, rejected,
     retried, completed, or verified without redoing the rest?
   - Does investigation establish a finding that changes later scope, design,
     interfaces, or acceptance criteria?

   - Does it cross from discovery to analysis, analysis to decision, decision to
     authoring, authoring to implementation, or implementation to verification?
   - Could another worker consume or check an intermediate result, even as a short
     handoff rather than a requested document?

   If any answer is yes or uncertain, record `split`, split and repeat. Known-source
   reading may stay inside one task; discovering sources or producing meaning from
   them does not. Punctuation alone is not proof, but each action verb is a
   mandatory split prompt. An `accepted-indivisible` decision requires one shared
   result, one verification boundary, and concrete separation harm. Do not limit
   task count or merge work to fit a skill.

4. **Connect the results.** For every result, state its required inputs, expected
   output, and completion check. When one result consumes another, keep both tasks
   separate and record the predecessor, supplied item, consumer use, and readiness
   condition. Put file handoffs in the consumer's `filesToRead`. Retain multiple
   apparent results together only when they are one indivisible state change and
   separation would create a concrete invalid, misleading, or unsafe state. If the
   separation harm cannot be stated confidently, split.

5. **Draft and close the pre-assignment boundary review.**
   Turn each final result into one task. Give each task a unique `taskId`, one purpose,
   one expected output, concrete instructions, relevant context, verification
   coverage, dependencies, anti-pattern signals, and purpose/output alignment.
   Do not add `skills` yet. Review the whole set:

   - completing all tasks satisfies the original request;
   - every requested or necessary result appears once;
   - no task still hides multiple results;
   - every dependency supplies a usable handoff;
   - each lifecycle stage is separate unless indivisibility is proven;
   - every uncertain boundary was split; and
   - independently executable verification has its own task.

    Record a closed disposition for every warning: `split`,
    `accepted-indivisible`, or `not-applicable`. Rework failed, missing, ambiguous,
   contradictory, or unresolved boundaries and repeat the review. Proceed to
   skill assignment only after this request-aware review accepts the complete
   record. A skill cannot create, preserve, or cure a boundary.

6. **Close final acceptance after candidate publication.** After the canonical packet
   is produced and structural validation is complete, the delegator independently
   compares the original request, boundary-review record, and final task set. Accept
   it for display or dispatch only if inventory coverage, one-immediate-result mapping,
   fixed-predecessor decisions, warning dispositions, dependency handoffs, and any
   indivisibility rationale are all closed and still match the final set. Structural
    validity is diagnostic evidence only and never proves atomicity. Return any failed
    review to splitting or a concrete indivisibility rationale. For every applicable
    packet, reject optional adoption, backwards compatibility, migration, legacy,
    transition, prior-format, absent-record acceptance, and alternate paths.

## Stopping Rule

Stop splitting only when one worker can take fixed inputs, produce one immediate
result, and stop without also discovering, deciding, changing, or independently
checking another result. Fine granularity is acceptable. When there is a reasonable
argument for another boundary, create it.

Use the [worked examples](decomposition-examples.md) to calibrate aggressive
splitting, dependencies, narrow retained coupling, and the stopping rule.
