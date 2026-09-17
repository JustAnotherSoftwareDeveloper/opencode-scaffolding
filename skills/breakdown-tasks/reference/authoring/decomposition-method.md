# Decomposition Method

Use this method after request normalization and before skill assignment. Turn one
requested outcome into the smallest useful results, then connect those results so
workers can complete the whole request. Deliberately over-split rather than risk a
compound assignment.

The loaded `task-contract` documentation skill owns task identity, atomicity,
dependencies, coupling, traceability, and verification meaning. This method applies
that contract.

## Procedure

1. **Name the requested outcome.** Record what the user wants to be true or delivered,
   along with explicit scope, constraints, source inputs, exclusions, and completion
   evidence. Ask for clarification only when missing information changes the outcome
   or prevents a usable breakdown.

2. **Inventory every candidate result.** List every discovery, evidence collection,
   question, analysis, finding, decision, recommendation, authored artifact, change,
   verification, review, and report needed for the outcome. Treat each action verb
   and each distinct object as a candidate. Work backward from the requested outcome:
   ask what must already be known, decided, or available before each candidate can be
   produced. Include intermediate results even when the user requested only one final
   deliverable.

3. **Split every candidate aggressively.** Begin with one task per candidate. For
   every proposed task, ask:

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

   If any answer is yes or uncertain, split and repeat. Known-source reading may stay
   inside one task; discovering sources or producing meaning from them does not.
   Punctuation alone is not proof, but each action verb is a mandatory split prompt.
   Do not limit task count or merge work to fit a skill.

4. **Connect the results.** For every result, state its required inputs, expected
   output, and completion check. When one result consumes another, keep both tasks
   separate and record the predecessor, supplied item, consumer use, and readiness
   condition. Put file handoffs in the consumer's `filesToRead`. Retain multiple
   apparent results together only when they are one indivisible state change and
   separation would create a concrete invalid, misleading, or unsafe state. If the
   separation harm cannot be stated confidently, split.

5. **Draft and review the task set.**
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

   Rework failed boundaries and repeat the review. Proceed to skill assignment only
   after the set passes.

## Stopping Rule

Stop splitting only when one worker can take fixed inputs, produce one immediate
result, and stop without also discovering, deciding, changing, or independently
checking another result. Fine granularity is acceptable. When there is a reasonable
argument for another boundary, create it.

Use the [worked examples](decomposition-examples.md) to calibrate aggressive
splitting, dependencies, narrow retained coupling, and the stopping rule.
