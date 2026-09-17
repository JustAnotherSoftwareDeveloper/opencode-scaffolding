---
name: breakdown-tasks
description: "Use when decomposing a request into bounded task-delegation work items and producing canonical task JSON."
selection:
  role: owner
  tags:
    actions: [decompose]
    inputs: [user request]
    outputs: [delegation task JSON]
    topics: [task decomposition]
    constraints: [atomic work items]
  use_when: [a request must be split into worker-ready tasks]
  not_for: [executing one existing task packet]
class: delegated
---

# Breakdown Tasks

<!-- markdownlint-disable MD007 MD013 -->

Normalize a request, apply the operation-owned decomposition method, collect skills,
select inline, publish, and hand the published packet to downstream dispatch.

## Input Contract

Read and normalize `PURPOSE` and `DETAILS`, preserving the request's explicit scope,
constraints, files, and expected outcome. Block when either is absent.

## Execution

1. **Collect planning skills.** Run:

   ```bash
   uv run --project ~/.config/opencode/scripts/python collect-skills --class planning
   ```

   Capture stdout as a JSON array. Require `name`, `description`, `selection`,
   `class`, `path`, and `source` in every record. Block on non-zero exit.

2. **Select and load planning skills.** Present the request and planning array to
   the LLM. Select every materially relevant planning skill. Load each selection
   with the skill tool. Block on an absent name, stale path, or load failure. Allow
   an empty selection only when no planning concern exists.

3. **Collect operation and documentation skills.** Run:

   ```bash
   uv run --project ~/.config/opencode/scripts/python collect-skills \
     --class operation --class documentation
   ```

   Capture stdout as a JSON array with the same shape as step 1. Block on
   non-zero exit.

4. **Load the shared task contract before authoring boundaries.**
   Reconcile the exact collector winner named `task-contract` with class
   `documentation` and its
   discovered `SKILL.md` path, then load it before drafting boundaries. The passive,
   non-transitive load adds no authority, workflow, tools, writes, delegation,
   assignment, or completion evidence. Read needed references explicitly. Block on
   an absent name, stale path, class mismatch, or load failure.

5. **Break down the problem into extremely atomic tasks.** Before selecting executable
   skills, follow the operation-owned
   [Decomposition Method](reference/authoring/decomposition-method.md). Name the
   requested outcome, inventory every discovery, research, analysis, finding,
   decision, recommendation, authored artifact, implementation change, verification,
   review, and report needed to reach it. Make each candidate its own task, then split
   it again if it still contains more than one immediate result. Prefer too many small
   tasks over one compound task. When uncertain, split.

   Apply the loaded `task-contract` documentation skill's named **Atomicity and
   alignment**, **Dependencies and coupling**, and **Traceability and metadata**
   references. Hold predecessor outputs fixed when testing whether dependent results
   can be accepted or retried separately. Treat lifecycle stages as separate tasks by
   default. Known-file reading may support one task, but source discovery, findings,
   decisions, changes, and independently executable checks are separate results. Do
   not use a final deliverable, shared file, workflow, sequence, or available skill to
   merge them.

   Draft tasks without `skills`. Give each task a unique `taskId` and populate
   `verificationCoverage`, `dependencies`, `antiPatternSignals`, and
   `purposeOutputAlignment`; add `couplingRationale` only when the shared contract
   supports it. Review the complete set for coverage, duplication, hidden compound
   work and usable dependency handoffs before assignment. Do not merge tasks to avoid
   fine granularity. Retain multiple actions only when separation is demonstrably
   invalid, misleading, or unsafe; inconvenience is not coupling evidence.

6. **Assign skills to each task.** Present the complete draft and operation and
   documentation array to the LLM. Select one to three skills per task without
   changing boundaries. Reconcile each selection against the winning `name`, `class`,
   and `path`; block on no match, absence, stale or substituted path, class mismatch,
   or unresolved assignment. Exclude passive `task-contract` from executable
   `skills`. Do not score, rank, rerank, clip, repair, or use lexical or similarity
   fallback.

7. **Inspect contracts.** Read each selected skill's `SKILL.md` at its
   collector-winning `path`. Verify that the contract matches the task.

8. **Write the completed draft.** Add the reconciled `skills` arrays without
    changing boundaries or metadata. Require the author to select one packet slug.
    Run `mktemp "${TMPDIR:-/tmp}/opencode-breakdown.XXXXXX.json"`, capture the
    returned unique path as `DRAFT_PATH`, and write the schema-valid canonical packet
    root there. Block if the command fails. Preserve the packet slug unchanged. The
    canonical root fields and slug constraints are owned by
    [the task-packet schema](schema/task-packet.schema.json), not this workflow.

9. **Publish for dispatch.** Run:

   ```bash
   uv run --project ~/.config/opencode/scripts/python init-task-packet \
     --output-dir .tasks < "$DRAFT_PATH" || status=$?
   rm -f -- "$DRAFT_PATH" || status=2
   exit "${status:-0}"
   ```

   Run from the workspace root so `.tasks` resolves there. The command preserves the
   supplied slug, writes atomically, prints the output path, and removes the temporary draft on success or failure. Block on non-zero exit.

10. **Validate structure and recheck the breakdown.** Run structural validation in a loop
   until valid. Treat repairable structural diagnostics as warnings before hard
   failure. Revalidate task coverage, boundaries, dependencies, and skills after any
   split or migration:

   ```bash
   schema=~/.config/opencode/skills/breakdown-tasks/schema
   uv run --project ~/.config/opencode/scripts/python validate-task-structure \
     --state-file "$PUBLISHED_PATH" \
     --schema "$schema/task-packet.schema.json" \
     --auto-fix
   ```

   Follow [structure validation](reference/scripts/validate-task-structure.md): repair
   diagnostics, reread and retry changed files, and block on unrecoverable errors.

   After structural validation, compare the packet with the requested outcome and
   the final breakdown. Confirm that every necessary intermediate and final result
   appears once, every task owns one immediate result, every dependency supplies a
   usable handoff, and no skill assignment changed a boundary. Split every unresolved
   boundary rather than approving a broad task. Structural validation remains
   structural only; it does not approve atomicity.

## Output Contract

Return the relative published packet path.

## Guardrails

- Run both collector commands exactly as shown.
- Run publication and validation from the workspace root. Use `--project` so
  packet paths remain workspace-relative.
- Use the planning array for planning selection. Use the operation and
  documentation array for assignment. Do not swap them.
- Do not recollect, rebuild metadata from names, or substitute paths.
- Do not manually populate, correct, reorder, or remove `skills`.
- Require an author-selected packet slug in every published root. Never derive,
  normalize, or locally validate it; use the canonical task-packet schema.
- Do not cap, target, or pad the number of tasks.
- Bias aggressively toward splitting. Too many atomic tasks are acceptable; hidden
  compound work is not.
- The one-to-three limit applies to `skills` within each task.
- Fail closed. Publish no partial output.
- Do not claim atomicity from schema validity, metadata presence, wording, a
  dependency, shared file, skill, order, destination, or final document. Break the
  problem into the smallest useful results first, then connect them. Retained
  coupling requires one indivisible result, one verification boundary, and concrete
  separation harm. If any element is uncertain, split.
- Planning loads are passive context and are reported separately. Only reconciled
  operation and documentation assignments are executable. A documentation
  assignment may be loaded as passive, non-transitive context. It cannot add
  authority, steps, tools, writes, delegation, or completion evidence. Ordinary
  execution may not load planning skills. These are contract boundaries, not
  claims of runtime loader enforcement.

## References

- [Core rules](reference/authoring/core-rules.md)
- [Decomposition method](reference/authoring/decomposition-method.md)
- [Packet drafting checklist](reference/authoring/packet-drafting-checklist.md)
- [Task-set review](reference/authoring/task-set-review.md)
- [Worked decomposition examples](reference/authoring/decomposition-examples.md)
- `task-contract` documentation skill for shared task semantics
- [Task granularity](reference/authoring/task-granularity.md)
- [Atomicity anti-patterns](reference/authoring/anti-patterns.md)
- [Atomicity examples](reference/authoring/atomicity-examples.md)
- [Context preservation](reference/authoring/context-preservation.md)
- [Field reference](reference/authoring/field-reference-table.md)
- [Structure validation](reference/scripts/validate-task-structure.md)
- [Error handling and testing](reference/scripts/error-handling-testing.md)
- [Task validation](reference/orchestration/task-validation.md)
- [Verification practices](reference/maintenance/verification-best-practices.md)
