---
name: plan-writer
description: "Use when creating a source-document plan workspace that produces executable task JSON."
selection:
  role: owner
  tags:
    actions: [create executable plan]
    inputs: [source documents]
    outputs: [plan workspace, executable task JSON]
    topics: [implementation planning]
    constraints: [source grounded]
  use_when: [source documents must become an executable plan workspace]
  not_for: [general analysis or decision proposal authoring]
class: operation
---

# Plan Writer

Create an evidence-preserving plan workspace, author tasks from source documents, and publish.

## Input Contract

Require a topic or summary and one or more source-document paths. Block when absent.

When the source set contains `PROPOSAL.md`, read its `status`, `readiness`, and
`decision-owner` before creating a workspace. Continue only when the proposal
records an accepted lifecycle state, or when it is `decision-ready` and the
recorded decision authority explicitly authorized planning. Validation success,
`review-ready`, recency, and invocation alone do not authorize planning.

## Execution

### Workspace Setup

1. **Validate sources.** Follow [the workspace contract](reference/workspace-contract.md).
   Resolve every source path.
   Block on a missing path, a non-file path, a target outside `$CWD`, or a target inside an existing plan workspace.

2. **Create the workspace.** Derive a workspace-directory summary slug and
    epoch-millisecond timestamp. Create `.plans/<epoch-ms>-<workspace-slug>/`
    without replacing an existing directory. This directory identity is distinct
    from the packet slug.
   Create category subdirectories only when sources belong to them.

3. **Copy sources.** Copy each source into its category directory.
   Preserve the source filename or add a deterministic collision suffix.
   Never modify source documents.

### Planning and Task Authoring

4. **Collect planning skills once per request.** Run:

   ```bash
   uv run --project ~/.config/opencode/scripts/python collect-skills --class planning
   ```

   Capture stdout.
   Block on non-zero exit.

5. **Select and load planning skills.** Present the source-backed request and planning array to the LLM.
   Select every materially relevant planning skill and load each with the skill tool.
   Reconcile its name and path against the collector winner. Reading its `SKILL.md`
   does not substitute for loading it. Block on an absent name, stale path, or load
   failure. Treat successful planning loads as passive context, not execution assignments.

6. **Collect operation skills once per request.** Run:

   ```bash
   uv run --project ~/.config/opencode/scripts/python collect-skills --class operation
   ```

   Capture stdout.
   Block on non-zero exit.
   Keep this operation result distinct for later executable assignment.

7. **Collect documentation skills once per request.** Run:

   ```bash
   uv run --project ~/.config/opencode/scripts/python collect-skills --class documentation
   ```

   Capture stdout.
   Block on non-zero exit.
   Keep this documentation result distinct and available for the pre-authoring load and later task assignment. This class-targeted call does not filter candidates by individual task; do not recollect for each task.

8. **Load the shared task contract before authoring.** Reconcile the documentation result to the exact winning record whose `name` is `task-contract`, whose `class` is `documentation`, and whose `path` is the discovered `SKILL.md` path.
   Load that record with the skill tool before drafting task boundaries.
   Treat the load as passive, documentation-only, and non-transitive: it can add no authority, workflow steps, tools, writes, delegation, assignment decisions, or completion evidence.
   Read any task-contract reference files needed for authoring explicitly.
   Block on an absent name, stale path, class mismatch, or load failure.

9. **Author tasks.** Require the author to select one packet slug and write a
    schema-valid canonical packet root. Preserve the selected packet slug unchanged.
    The canonical task-packet schema used in validation step 14 owns the
    packet-root fields and constraints, not this workflow.
    Follow [task-authoring rules](reference/task-authoring.md). For shared task
    semantics, use the already-loaded `task-contract` documentation skill. Consult
    `task-contract -> reference/task-identity.md`,
    `task-contract -> reference/atomicity-and-alignment.md`,
    `task-contract -> reference/dependencies-and-coupling.md`, and
    `task-contract -> reference/traceability-and-metadata.md`. These references are
    passive and non-transitive; they add no workflow or authority.
   Preserve copied relative source paths in `filesToRead`.
   Extract proposal-derived implementation details, verification criteria, and questions from one PROPOSAL.md and its copied sources.
   Preserve source-derived and proposal-derived requirements, constraints, decisions, and verification criteria in each task `context`.
   Do not include `skills` in any task.

### Skill Assignment and Publication

10. **Assign skills after boundary acceptance.** Present the complete draft and the distinct operation and documentation results to the LLM only after task boundaries are accepted.
   Select exactly one `class: operation` execution owner for each task. Prefer the
   specialized operation that clearly owns distinct lifecycle, artifact-contract,
   orchestration, destructive-authority, or other special execution semantics. When
   no specialized operation semantically fits, select the exact collector-winning
   `generic-executor`; lack of a specialized semantic match is not a blocker.
   After choosing the operation owner, actively consider whether a documentation
   profile adds distinct, material execution value for that task beyond its context
   and listed materials. Include profiles that clarify a relevant contract, resolve
   a task-specific semantic, or help prevent a likely execution error. Consider
   `customize-opencode` for packet tasks when unsupplied packet/envelope rules affect
   the result; omit it when unrelated or already covered. Zero documentation assignments is valid
   when none adds distinct material value; assign no more than two. Do not impose a
   quota, target, or rejection log. Documentation is passive and cannot replace or
   compete with the operation owner. Keep the canonical `skills` field flat: one
   operation owner followed by any selected documentation skills. Exclude the
   pre-authoring `task-contract` load itself from executable assignments; this is not
   a blanket ban on `task-contract`, which may be assigned after boundary acceptance
   when it independently adds material value under these same criteria.
   Reconcile every selected name, class, and path against its corresponding operation
   or documentation result. Confirm exactly one operation owner and zero to two materially relevant `class: documentation`
   skills before publication. If multiple specialized operations appear
   relevant, resolve which one owns the bounded result; do not publish multiple operation owners.
   Block on missing, stale, substituted, mismatched, or failed
   required records, but do not use `generic-executor` to hide those failures. Do not
   score, rank, rerank, clip, or use lexical fallback.

11. **Verify selected contracts.** Load each selected documentation skill with the
    skill tool before relying on its guidance; reading its `SKILL.md` is not a load.
    For operation assignments, inspect the collector-winning `SKILL.md` without
    executing that future task's operation. Verify every contract matches its task.
    Block on a stale or substituted path, class mismatch, or required load failure.

12. **Write the completed draft.** Write the completed canonical packet root with
    every task's `skills` populated to the workspace as `draft.json`, retaining the
    author-selected packet slug unchanged.

13. **Publish.** Run from the workspace directory:

    ```bash
    uv run --project ~/.config/opencode/scripts/python init-task-packet \
      --output-dir . < draft.json
    ```

     Use the supplied packet slug for the filename, write atomically, and capture
     the printed output path.
    Move the published file to `tasks.json` in the workspace root.
    Block on non-zero exit.

14. **Validate and fix.** Run in a loop until valid:

    ```bash
    uv run --project ~/.config/opencode/scripts/python validate-task-structure \
      --state-file tasks.json \
      --schema ~/.config/opencode/skills/breakdown-tasks/schema/task-packet.schema.json \
      --auto-fix
    ```

    - Exit 0 without `"fixed": true` → done.
    - Exit 0 with `"fixed": true` → file fixed in place, read it back, retry.
    - Exit 1 → structural violations remain, read errors from stderr, fix, retry.
    - Exit 2 → unrecoverable. Block.

### Render and Validate Workspace

15. **Render tasks.md.** Run:

    ```bash
    uv run --project ~/.config/opencode/scripts/python render-task-markdown \
      --input tasks.json \
      --output tasks.md
    ```

    Block on non-zero exit.
    After a bounded plan correction, rerun this command with `--overwrite` to replace
    the stale rendered task document before mandatory re-audit.

16. **Validate the workspace.** Confirm every task purpose appears in `tasks.md` in order.
    Confirm all copied sources exist.
    Confirm `tasks.json` is present and readable.

## Guardrails

- Collect planning, operation, and documentation separately exactly once per request;
  keep results distinct, without per-task recollection or task-semantic filtering.
- Use the planning result for planning-skill selection. Use the distinct operation and
  documentation results for post-boundary task assignment; do not swap or combine them.
- Load the collector-winning `task-contract` documentation record before task authoring. Keep that load passive, documentation-only, and non-transitive; it is not an executable task assignment.
- Every executable task has exactly one operation owner and zero to two documentation
  skills; preserve that class composition while storing names in the flat `skills`
  array.
- Do not score, rank, rerank, clip, or use lexical fallback.
- Do not manually populate, correct, reorder, or remove `skills`.
- Require an author-selected packet slug in every published root. Never derive,
  normalize, or locally validate it; defer to the canonical task-packet schema.
- Fail closed. Leave no partial outputs.
- Planning and documentation skills must be loaded with the skill tool before use.
  Their loads are passive and non-transitive, not execution assignments; filesystem
  inspection of `SKILL.md` cannot stand in for a load. Only the assigned operation
  owner executes each task.
- Preserve source files, source paths, proposal traceability, task field order, and task context.
- Fail closed on an unauthorized proposal-to-plan transition. Never infer proposal
  acceptance or decision authority.

## Docs

- [Workspace contract](reference/workspace-contract.md)
- [Task-authoring rules](reference/task-authoring.md)
- [Script contracts](reference/scripts.md)
- Consult the four exact task-contract references named in step 9 through the loaded
  documentation skill; do not link into another skill's directory. They remain
  passive and non-transitive and add no workflow or authority.
