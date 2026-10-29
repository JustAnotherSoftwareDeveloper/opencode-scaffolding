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

# Decompose Requests Into Worker-Ready Tasks

<!-- markdownlint-disable MD007 MD013 -->

Normalize a request, apply the operation-owned decomposition method, collect and
select skills inline, publish the packet, and hand it to downstream dispatch.

## Input Contract

Read and normalize `PURPOSE` and `DETAILS`, preserving the request's explicit scope,
constraints, files, and expected outcome. Block if either field is absent.

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
   an empty selection only when no planning concern exists. Reading `SKILL.md`
   does not substitute for loading a planning or documentation skill.

3. **Collect operation skills.** Run:

   ```bash
   uv run --project ~/.config/opencode/scripts/python collect-skills --class operation
   ```

   Capture stdout as a JSON array with the same shape as step 1. This is the
   operation result for this decomposition request. Block on non-zero exit.

4. **Collect documentation skills.** Run:

   ```bash
   uv run --project ~/.config/opencode/scripts/python collect-skills --class documentation
   ```

   Capture stdout as a JSON array with the same shape as step 1. Keep this
   documentation result distinct from the operation result and available for the
   pre-authoring load and later assignment. These class-targeted calls do not
   filter candidates by individual task; do not recollect for each task. Block
   on non-zero exit.

5. **Load shared task and writing references before authoring.**
   Reconcile the exact collector winner named `task-contract` in the
   documentation result with class `documentation` and its discovered `SKILL.md`
   path, then load it before drafting boundaries. The passive, non-transitive
   load adds no authority, workflow, tools, writes, delegation, assignment, or
   completion evidence. Read needed references explicitly. Block on an absent
   name, stale path, class mismatch, or load failure.

   Before drafting substantive task-field prose, reconcile the exact
   `markdown-writing-guide` collector winner in that same documentation result
   with class `documentation` and its discovered `SKILL.md` path, load it with
   the skill tool, and read
   `markdown-writing-guide -> reference/writing-quality.md`. Apply it only to
   prose authored or substantively revised in fields such as purpose, context,
   execution instructions, verification, and expected output. Preserve each
   field's purpose, task-contract semantics, source-derived evidence and
   constraints, accepted boundaries, and packet schema. The guide is passive
   and non-transitive; it adds no workflow, assignment, authority, or other
   execution permission. Block on an absent name, stale path, class mismatch,
   or required load failure.

6. **Draft boundaries and close the pre-assignment review.** Before selecting executable
   skills, follow the operation-owned
   [Decomposition Method](reference/authoring/decomposition-method.md). Name the
   requested outcome, inventory every discovery, research, analysis, finding,
   decision, recommendation, authored artifact, implementation change, verification,
   review, and report needed to reach it. Make each candidate its own task, then split
   it again if it still contains more than one immediate result. Prefer too many small
   tasks over one compound task. When uncertain, split.

    Apply the loaded documentation references
    `task-contract -> reference/atomicity-and-alignment.md`,
    `task-contract -> reference/dependencies-and-coupling.md`, and
    `task-contract -> reference/traceability-and-metadata.md`.
    Hold predecessor outputs fixed when testing whether dependent results can be
    accepted or retried separately. Treat lifecycle stages as separate tasks by
    default. Reading a known file may support one task, but source discovery, findings,
    decisions, changes, and independently executable checks are separate results. Do
    not use a final deliverable, shared file, workflow, sequence, or available skill to
    merge them.

   Draft tasks without `skills`. Give each task a unique `taskId` and populate
   `verificationCoverage`, `dependencies`, `antiPatternSignals`, and
   `purposeOutputAlignment`; add `couplingRationale` only when the shared contract
   supports it. Create and retain a boundary-review record alongside the draft and
   canonical packet. For every applicable packet, the record must cover every
   request-derived immediate and necessary intermediate result; map every proposed
   task to one immediate result and its fixed predecessor outputs; record the
   split-by-default fixed-predecessor decision; and close every warning as `split`,
   `accepted-indivisible`, or `not-applicable`. An accepted-indivisible disposition
   states one shared result, one verification boundary, and concrete separation harm.
   Review the complete set for coverage, duplication, hidden compound work, usable
   dependency handoffs, and closed warning dispositions before assignment. Missing,
   ambiguous, contradictory, or unresolved evidence returns the set for revision.
   Do not merge tasks to avoid fine granularity. Retain multiple actions only when
   separation is demonstrably invalid, misleading, or unsafe; inconvenience is not
   coupling evidence.

7. **Assign skills only after boundary acceptance.** Assign only after the completed
   pre-assignment review accepts the draft boundaries. Present the complete accepted
   draft and the distinct operation and documentation results to the LLM. For
   each task, select exactly one `class: operation` execution owner without
   changing the accepted boundary. When one specialized operation clearly owns a
    distinct lifecycle, artifact contract, orchestration flow, destructive
    authority, or other special execution semantics, select that operation. When
    no specialized operation semantically fits, select the exact
    collector-winning `generic-executor` operation as the execution owner; a lack
    of a specialized match is not a blocker. Add zero to two materially relevant
    `class: documentation` skills when useful. Zero is valid when none adds distinct
    material value. Documentation is passive and cannot replace or compete with the
    operation owner. Store the result in the existing flat `skills` array: one
    operation owner followed by zero to two documentation skills. Exclude passive
    `task-contract` from executable `skills`.

   When a task requires substantive prose authoring or revision in a Markdown
   deliverable or structured task fields, include the exact collector-winning
   `markdown-writing-guide` documentation record when it adds material value
   and fits within the two-documentation limit. Do not assign it for a path or
   Markdown output alone, mechanical edits, or deterministic rendering. This
   assignment is independent of the pre-authoring passive load and does not
   transfer its guidance transitively to a worker.

   Reconcile every selected skill, including `generic-executor`, against the winning
   `name`, `class`, and `path`. Before publication, confirm the reconciled assignment
   contains exactly one operation and zero to two documentation skills. If multiple
   specialized operations appear relevant, resolve which one owns the bounded result;
   do not publish multiple operation owners and do not change an accepted task boundary
   merely because skill coverage overlaps. Block on an absent name, stale or
   substituted path, class mismatch, unresolved assignment, failed required load, no
   operation owner, more than one operation owner, or more than two documentation
   skills. Do not use `generic-executor` to conceal collector failure, a broken
   specialized collector record, a failed selected skill load, malformed task
   metadata, or execution failure inside a specialized operation that clearly owns
   the task. Do not score, rank, rerank, clip, repair, or use lexical or similarity
   fallback.

8. **Verify selected contracts.** Load each selected documentation skill with the
   skill tool before relying on its guidance; reading its `SKILL.md` is not a load.
   For operation assignments, inspect the collector-winning `SKILL.md` without
   executing that future task's operation. Verify every contract matches its task.
   Block on a stale or substituted path, class mismatch, or required load failure.

9. **Write the completed draft.** Add the reconciled `skills` arrays without
    changing boundaries or metadata. Require the author to select one packet slug.
    Run `mktemp "${TMPDIR:-/tmp}/opencode-breakdown.XXXXXX.json"`, capture the
    returned unique path as `DRAFT_PATH`, and write the schema-valid canonical packet
    root to that path. Block if the command fails. Preserve the packet slug unchanged.
    The canonical root fields and slug constraints are owned by
    [the task-packet schema](schema/task-packet.schema.json), not this workflow.

10. **Publish the candidate packet.** Run:

   ```bash
   uv run --project ~/.config/opencode/scripts/python init-task-packet \
     --output-dir .tasks < "$DRAFT_PATH" || status=$?
   rm -f -- "$DRAFT_PATH" || status=2
   exit "${status:-0}"
   ```

   Run from the workspace root so `.tasks` resolves there. The command preserves the
   supplied slug, writes atomically, prints the output path, and removes the temporary
   draft on success or failure. Block on non-zero exit. This publication does not
   accept the packet for display or dispatch.

11. **Validate structure and close final request-aware acceptance.** Run structural
    validation in a loop until valid. Treat repairable structural diagnostics as
    warnings before hard failure. Revalidate task coverage, boundaries, dependencies,
    and skills after any split:

   ```bash
   schema=~/.config/opencode/skills/breakdown-tasks/schema
   uv run --project ~/.config/opencode/scripts/python validate-task-structure \
     --state-file "$PUBLISHED_PATH" \
     --schema "$schema/task-packet.schema.json" \
     --auto-fix
   ```

   Follow [structure validation](reference/scripts/validate-task-structure.md): repair
   diagnostics, reread and retry changed files, and block on unrecoverable errors.

   After structural validation, the delegator independently compares the retained
   boundary-review record, original request, and final task set. Accept the packet
   for display or dispatch only when the record is closed: the inventory covers every
   necessary intermediate and final result exactly once; every task owns one immediate
   result; each fixed-predecessor split decision is supported; every dependency
   supplies a usable handoff without claiming coupling; every warning has a closed
   disposition; retained coupling has concrete indivisibility evidence; and no skill
   assignment changed a boundary. Otherwise return the set for split or a concrete
   indivisibility rationale and repeat the applicable review. Structural validation
   remains structural only; it never approves atomicity. There is no absent-record,
   warning-free, structural-validity, or alternate acceptance path.

## Output Contract

Return the relative published packet path.

## Guardrails

- Run the planning-, operation-, and documentation-class collector commands
  exactly once per request as shown.
- Run publication and validation from the workspace root. Use `--project` so
  packet paths remain workspace-relative.
- Use the planning result for planning selection. Use the distinct operation and
  documentation results for assignment. Do not combine or swap them.
- Do not recollect for individual tasks, rebuild metadata from names, or
  substitute paths.
- Do not manually populate, correct, reorder, or remove `skills`.
- Require an author-selected packet slug in every published root. Never derive,
  normalize, or locally validate it; use the canonical task-packet schema.
- Do not cap, target, or pad the number of tasks.
- Bias aggressively toward splitting. Too many atomic tasks are acceptable; hidden
  compound work is not.
- Every applicable packet requires one closed boundary-review record before it may be
  accepted for display or dispatch. The record is request-aware evidence retained
  alongside the canonical packet, not a schema claim or mechanical proof of atomicity.
  Do not provide an optional adoption, backwards-compatibility, migration, legacy,
  transition, prior-format, or alternate acceptance path.
- Every task's flat `skills` array contains exactly one operation owner and zero to two
  documentation skills. Reconcile those classes against collector metadata before
  publication; JSON schema cardinality alone does not prove the class composition.
- A task with no specialized operation owner uses the exact collector-winning
  `generic-executor`; lack of a specialized semantic match is not a reason to block.
  Collector failures, stale or mismatched records, failed required skill loads, and
  malformed contracts remain blockers and must not be hidden by generic fallback.
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

- [Skill assignment](reference/skill-assignment.md)
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
