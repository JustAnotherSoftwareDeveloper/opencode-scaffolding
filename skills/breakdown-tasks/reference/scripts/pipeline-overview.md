# Pipeline Overview

This is an in-file map of one request's path from normalization to an accepted
task packet. The [producer workflow](../../SKILL.md) owns the full procedure;
the [skill assignment reference](../skill-assignment.md) explains assignment
decisions. The stages below show what each phase consumes, produces, and must
prove before the next phase starts.

## Ordered Stages

1. **Normalize the request.** Read the request's purpose and details. Preserve its
   requested result, scope, constraints, files, and expected outcome in the
   normalized context used throughout decomposition. Missing purpose or details
   blocks the workflow rather than inviting an invented objective.

2. **Collect the planning inventory.** Run the planning collector once for this
   request and capture its stdout JSON array:

   ```bash
   uv run --project ~/.config/opencode/scripts/python collect-skills --class planning
   ```

   Planning records supply `name`, `description`, `selection`, `class`, `path`,
   and `source`. A non-zero exit blocks the request.

3. **Select and load planning context.** Present the normalized request and
   planning array for selection. Select every materially relevant planning skill
   from that array and load each through the skill tool. The planning loads inform
   decomposition; they do not supply task execution assignments. An empty
   selection is valid only when the request has no planning concern. An absent
   winner, stale path, or failed required load blocks.

4. **Collect operation and documentation inventories.** After planning context
   is selected and loaded, run each remaining collector once, separately and in
   this order:

   ```bash
   uv run --project ~/.config/opencode/scripts/python collect-skills --class operation
   ```

   ```bash
   uv run --project ~/.config/opencode/scripts/python collect-skills --class documentation
   ```

   Capture the two stdout JSON arrays separately; each record supplies `name`,
   `description`, `selection`, `class`, `path`, and `source`. Keep these distinct
   inventories for the pre-authoring documentation load and later task assignment.
   Do not combine the calls or recollect for individual tasks. A non-zero exit
   blocks the request.

5. **Load the shared task contract before authoring boundaries.** From the
   documentation array, reconcile the exact winning `task-contract` record by
   `name`, documentation `class`, and `path`, then load it before drafting
   boundaries. This is passive, documentation-only, non-transitive context: it
   adds no workflow, authority, tools, writes, delegation, assignments, or
   completion evidence. It is not itself a task assignment. A missing name,
   class/path mismatch, or load failure blocks before authoring.

6. **Inventory results and accept task boundaries before assignment.** Apply the
   operation-owned decomposition method to the normalized request. Inventory all
   immediate and necessary intermediate results; give each candidate task one
   immediate result; split compound results again by default; and connect tasks
   only with usable predecessor handoffs. Draft the task set without `skills`.
   Retain a request-aware `boundaryReview` alongside the draft: map inventory
   results to tasks, record fixed predecessor outputs and each split decision,
   and close every warning. Review coverage, duplication, hidden compound work,
   dependencies, and warning dispositions. Unresolved or contradictory evidence
   returns the set for revision. Assignment cannot begin until this review accepts
   the complete boundaries. See the [decomposition method](../authoring/decomposition-method.md)
   for the detailed review method.

7. **Assign skills from the distinct operation and documentation results.**
   Present the complete accepted task set and both relevant arrays for assignment.
   For each task, choose exactly one `class: operation` owner. Choose a specialized
   operation when it owns the task's distinct lifecycle or execution semantics;
   otherwise use the exact collector-winning `generic-executor` operation. Add
   zero to two materially relevant `class: documentation` skills when they add
   distinct value; zero is valid. Documentation stays passive and cannot replace
   or compete with the operation owner. Store the reconciled result in the flat
   `skills` array, with the operation owner first and selected documentation
   skills after it.

   Reconcile every assignment, including a generic fallback, against the winning
   `name`, `class`, and `path`. Load selected documentation before relying on it;
   inspect each operation's winning `SKILL.md` contract without running that
   future task. Do not score, rank, rerank, use lexical/path fallback, recollect,
   or manually repair assignments. Missing winners, stale or substituted paths,
   class mismatches, failed loads, unresolved ownership, or invalid class
   composition block publication. The passive pre-authoring `task-contract` load
   does not count as one of a task's assignments.

8. **Complete the canonical packet draft.** Preserve the accepted boundaries and
   metadata while adding the checked skill arrays. The root object contains
   `summary`, an author-selected `slug`, `tasks`, and required `boundaryReview`;
   `tasks` is a non-empty list, not the root itself. Each task requires
   `taskId`, `purpose`, `context`, `filesToRead`, `filesToWrite`, `skills`,
   `executionInstructions`, `expectedOutput`, `verificationCoverage`,
   `dependencies`, `antiPatternSignals`, and `purposeOutputAlignment`. Optional
   fields include `verification`, the top-level checks for the complete
   deliverable (distinct from per-step checks), and `couplingRationale`. The boundary
   review contains `requestResultInventory`, `taskReviews`, and
   `warningDispositions`. Inventory records state `result`, `kind`
   (`immediate` or `necessary-intermediate`), and `disposition`
   (`represented-by-task`, `split-into-tasks`, or `not-applicable`). Task reviews
   map `immediateResult` and `predecessorOutputs` to a `single-result` or
   `retained-indivisible` pre-assignment disposition and an `accepted` or
   `accepted-indivisible` acceptance disposition; retained indivisibility
   requires `sharedResult`, `verificationBoundary`, and `separationHarm`.
   Warning records state a `signal` and `split`, `accepted-indivisible`, or
   `not-applicable` disposition, with `taskId` for accepted indivisibility. Use
   the [task-packet schema](../../schema/task-packet.schema.json)
   for exact types and constraints. The author selects the slug; do not derive or
   normalize it.

9. **Write a temporary draft.** Create a unique JSON draft path and write the
   complete schema-valid root object there:

   ```bash
   DRAFT_PATH=$(mktemp "${TMPDIR:-/tmp}/opencode-breakdown.XXXXXX.json")
   ```

   A failed `mktemp` blocks publication. Keep this draft distinct from the
   workspace packet until the publisher succeeds.

10. **Atomically publish a complete candidate.** From the workspace root, run
   `init-task-packet` with the draft on stdin and `.tasks` as the output directory:

   ```bash
   uv run --project ~/.config/opencode/scripts/python init-task-packet \
     --output-dir .tasks < "$DRAFT_PATH" || status=$?
   rm -f -- "$DRAFT_PATH" || status=2
   exit "${status:-0}"
   ```

   The publisher preserves the selected slug, atomically writes the complete
   candidate, and prints its relative path; capture that path as
   `PUBLISHED_PATH`. Remove the temporary draft on success or failure. Run from
   the workspace root so `.tasks` and the published path are workspace-relative.
   This is candidate publication, not structural or request-aware acceptance; a
   file's existence alone never authorizes display or dispatch.

11. **Validate structure and retry supported repairs.** From the workspace root,
    validate the published state against the canonical schema:

    ```bash
    schema=~/.config/opencode/skills/breakdown-tasks/schema
    uv run --project ~/.config/opencode/scripts/python validate-task-structure \
      --state-file "$PUBLISHED_PATH" \
      --schema "$schema/task-packet.schema.json" \
      --auto-fix
    ```

    This checks the complete root, including `summary`, `slug`, `tasks`, and
    `boundaryReview`, plus structural consistency; it does not prove semantic
    atomicity. `--auto-fix` is limited to supported `skills`-array repairs
    (remove empty names, deduplicate while preserving order, and trim arrays to
    three entries). It does not add fallback skills, remove unknown names, or
    repair unrelated structural errors. A clean result returns `{"valid": true}`;
    invalid state returns `{"valid": false, "errors": [...]}`; a successful
    auto-fix result also reports whether `fixed` was true. After a repair changes
    state, reread and validate the published file again and independently
    reconfirm the one-operation/zero-to-two-documentation class assignment;
    schema cardinality alone does not establish class composition. Repeat the
    applicable task-set review and validation after any boundary-changing split.
    Unrepairable diagnostics or non-zero validation block acceptance. See
    [structure validation](validate-task-structure.md) and
    [error handling and testing](error-handling-testing.md).

12. **Close final request-aware acceptance.** Only after structural success,
    compare the original request, retained boundary-review record, and final task
    set. Accept for display or dispatch only when the inventory covers every
    necessary intermediate and final result exactly once, each task owns one
    immediate result, fixed-predecessor split decisions are supported, and every
    dependency supplies a usable handoff without claiming coupling. Warnings must
    be closed; any retained coupling must have concrete indivisibility evidence;
    and assignments must not change accepted boundaries. Structural validity is
    not semantic acceptance. Unresolved boundary evidence or task deficiencies
    return the set for revision and another applicable review.

## Fail-Closed Gates

- Collector, selection, reconciliation, required-load, draft, and publisher
  failures stop the workflow; do not conceal them with a fallback or substitute.
- Do not accept an invalid assignment or unresolved structural diagnostic. Apply
  only supported repairs, then validate again.
- The publisher writes a complete candidate atomically, not a partial file. Do
  not display or dispatch it until both structural validation and the separate
  request-aware acceptance gate pass.
- Never infer atomicity from schema validity, metadata, wording, dependencies,
  shared files, skills, or task order. When the boundary evidence does not support
  a result as indivisible, split it rather than treating the packet as accepted.

## Related References

- [Producer workflow](../../SKILL.md) — authoritative end-to-end order and guardrails.
- [Skill assignment](../skill-assignment.md) — collector-winner identity and class rules.
- [Decomposition method](../authoring/decomposition-method.md) — boundary inventory and review.
- [Task-packet schema](../../schema/task-packet.schema.json) — canonical root and task shape.
- [Structure validation](validate-task-structure.md) — validator modes, diagnostics, and repairs.
- [Error handling and testing](error-handling-testing.md) — workflow failure and integration checks.
