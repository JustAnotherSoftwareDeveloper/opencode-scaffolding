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

Normalize a request, collect skills, draft bounded tasks, select inline, publish, and
hand the published packet to downstream dispatch.

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

4. **Load the shared task contract before authoring boundaries.** Reconcile the
   collector array to the exact winning record whose `name` is `task-contract`, whose
   `class` is `documentation`, and whose `path` is the discovered `SKILL.md` path.
   Load that record with the skill tool before drafting task boundaries. Treat the
   load as passive, documentation-only, and non-transitive: it can add no authority,
   workflow steps, tools, writes, delegation, assignment decisions, or completion
   evidence. Read any task-contract reference files needed for authoring explicitly;
   loading the index does not recursively load them. Block on an absent name, stale
   path, class mismatch, or load failure.

5. **Draft atomic tasks.** Inventory every question, change, operation, decision,
   and deliverable before selecting executable skills. Follow the operation-owned
   request-inventory and decomposition procedure in the
   [core rules](reference/authoring/core-rules.md), while consuming the shared
   [task-contract semantics](../task-contract/reference/README.md) for identity,
   atomicity, result and verification alignment, dependencies, coupling, traceability,
   and authoring metadata. Consult the [atomicity examples](reference/authoring/atomicity-examples.md).
   Split independently reviewable concerns regardless of task count. Establish candidate boundaries
   before assignment. Give each task a unique `taskId` and
   populate `verificationCoverage`, `dependencies`, `antiPatternSignals`, and
   `purposeOutputAlignment`. Add `couplingRationale` only when the shared contract's
   coupling evidence is present. Do not include `skills` yet.

6. **Assign skills to each task.**
   Present the complete draft and the operation and documentation array to the LLM.
   Select one to three skills per task. Do this
   without changing the established boundaries. Block with explicit no-match
   evidence when no assignment fits. Reconcile each selection against the array's
   winning `name`, `class`, and `path`. Block on an absent name, stale or
   substituted path, class mismatch, or unresolved assignment. Do not include the
   pre-authoring passive `task-contract` record in an executable `skills` array. Do not score,
   rank, rerank, clip, repair, or use lexical or similarity fallback.

7. **Inspect contracts.** Read each selected skill's `SKILL.md` at its
   collector-winning `path`. Verify that the contract matches the task.

8. **Write the completed draft.** Add the reconciled `skills` arrays without
   changing boundaries or metadata. Write the schema-valid `{summary, tasks}`
   object to `/tmp/breakdown-draft.json`.

9. **Publish for dispatch.** Run:

   ```bash
   uv run --project ~/.config/opencode/scripts/python init-task-packet \
     --output-dir .tasks < /tmp/breakdown-draft.json
   ```

   Run from the workspace root so `.tasks` resolves there. The project option
   selects the scripts environment without changing the working directory. The
   command derives a safe filename, writes atomically, and prints the output path.
   Block on non-zero exit.

10. **Validate and fix.** Run in a loop until valid. Treat repairable evidence gaps
   as warnings before hard failure. Revalidate after any split or migration. Then
   revalidate boundaries, mappings, dependencies, and skills:

   ```bash
   schema=~/.config/opencode/skills/breakdown-tasks/schema
   uv run --project ~/.config/opencode/scripts/python validate-task-structure \
     --state-file "$PUBLISHED_PATH" \
     --schema "$schema/task-packet.schema.json" \
     --auto-fix
   ```

   - Exit 0 with no diagnostics and no `"fixed": true` means valid.
   - Exit 0 with diagnostics means repair actionable gaps and retry. Preserve a
     warning only for migration compatibility or an unresolved decision.
   - Exit 0 and `"fixed": true` means the file changed. Read it and retry.
   - For Exit 1, fix the JSON, retry, and read errors from stderr.
   - Exit 2 → unrecoverable error. Block.

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
- Do not cap, target, or pad the number of tasks.
- The one-to-three limit applies to `skills` within each task.
- Fail closed. Publish no partial output.
- Planning loads are passive context and are reported separately. Only reconciled
  operation and documentation assignments are executable. A documentation
  assignment may be loaded as passive, non-transitive context. It cannot add
  authority, steps, tools, writes, delegation, or completion evidence. Ordinary
  execution may not load planning skills. These are contract boundaries, not
  claims of runtime loader enforcement.

## References

- [Core rules](reference/authoring/core-rules.md)
- [Shared task-contract reference](../task-contract/reference/README.md)
- [Task granularity](reference/authoring/task-granularity.md)
- [Atomicity anti-patterns](reference/authoring/anti-patterns.md)
- [Atomicity examples](reference/authoring/atomicity-examples.md)
- [Context preservation](reference/authoring/context-preservation.md)
- [Field reference](reference/authoring/field-reference-table.md)
- [Structure validation](reference/scripts/validate-task-structure.md)
- [Error handling and testing](reference/scripts/error-handling-testing.md)
- [Task validation](reference/orchestration/task-validation.md)
- [Verification practices](reference/maintenance/verification-best-practices.md)
