# Decomposition Method

Use this method after request normalization and before skill assignment. Turn one
requested outcome into smaller results, then connect those results so workers can
complete the whole request.

The loaded `task-contract` documentation skill owns task identity, atomicity,
dependencies, coupling, traceability, and verification meaning. This method applies
that contract.

## Procedure

1. **Name the requested outcome.** Record what the user wants to be true or delivered,
   along with explicit scope, constraints, source inputs, exclusions, and completion
   evidence. Ask for clarification only when missing information changes the outcome
   or prevents a usable breakdown.

2. **Break the outcome into smaller results.** List the questions that must be
   answered, decisions that must be made, changes that must be completed, and
   deliverables that must exist. Work backward from the requested outcome: ask what
   must already be known, decided, or available before it can be produced. Include
   necessary intermediate results even when the user did not request a separate
   document for them.

3. **Split each result into one assignment.** For every proposed result, ask:

   - Does it still contain another substantial question, decision, change, or
     deliverable?
   - With predecessor outputs held fixed, can part of it be accepted, rejected,
     retried, completed, or verified without redoing the rest?
   - Does investigation establish a finding that changes later scope, design,
     interfaces, or acceptance criteria?

   If an answer reveals another useful result, split it and repeat the test. Keep
   ordinary reading, editing, and checks inside a task when they only produce or
   verify that task's result. Do not split by punctuation, file count, workflow
   phase, available skill, or desired task count.

4. **Connect the results.** For every result, state its required inputs, expected
   output, and completion check. When one result consumes another, keep both tasks
   separate and record the predecessor, supplied item, consumer use, and readiness
   condition. Put file handoffs in the consumer's `filesToRead`. Retain multiple
   apparent results together only when they share one useful result and verification
   boundary and separation would create an invalid, misleading, or unsafe state.

5. **Draft and review the task set.**
   Turn each final result into one task. Give each task a unique `taskId`, one purpose,
   one expected output, concrete instructions, relevant context, verification
   coverage, dependencies, anti-pattern signals, and purpose/output alignment.
   Do not add `skills` yet. Review the whole set:

   - completing all tasks satisfies the original request;
   - every requested or necessary result appears once;
   - no task still hides multiple results;
   - every dependency supplies a usable handoff;
   - no task was split into procedural fragments; and
   - ordinary verification remains with its result unless verification has its own
     independently reviewable output.

   Rework failed boundaries and repeat the review. Proceed to skill assignment only
   after the set passes.

## Stopping Rule

Stop splitting when one worker can take the stated inputs, produce one result, and
prove completion without also owning another result. Further splitting must not
create tasks that only read one file, write one fragment, or run one check for the
same result.

Use the [worked examples](decomposition-examples.md) to calibrate splitting,
dependencies, internal supporting work, and the stopping rule.
