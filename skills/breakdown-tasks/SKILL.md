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

Decompose a request into atomic worker packets using direct LLM selection over one frozen inventory.

## Input Contract

Read `PURPOSE` and `DETAILS`; block when either is absent. Preserve the complete request context in the draft tasks.

## Phase A — Direct Planning Selection

1. Collect one full caller-root inventory containing planning, operation, and documentation profiles. Freeze its JSON and winning paths for the run.
2. Present the request and planning profiles to the LLM. Select every materially relevant planning profile, with no numeric cap. An empty set is valid only when no planning concern is present.
3. Load exactly the selected planning names through the skill tool, in selected order. These loads are passive context and are reported separately from executable skills.
4. Reconcile names, classes, and collector-winning paths before loading; block on an unknown name, stale or substituted path, irrelevant load, or load failure.
5. Use the selected planning context to produce schema-valid `{summary, tasks}` without `skills` or a slug. Read the authoring references linked below.

## Phase B — Direct Task Assignment And Publication

1. From the same frozen inventory, present only operation/documentation profiles and the complete draft to the LLM.
2. Select one to three task skills per task, or block with explicit no-match evidence. Selection is semantic and direct: never score, rank, threshold, rerank, clip, or fall back to lexical/path matching.
3. Inspect each selected collector-winning `SKILL.md` contract before generation. Reconcile names, class, cardinality, and paths against the same frozen snapshot.
4. Invoke the generator with the complete draft, frozen inventory, and final assignments. The generator owns assignment validation, field/order preservation, destination derivation, and atomic no-replacement publication.
5. Reconcile the generated packet after publication against the frozen inventory and task contracts. Do not repair or mutate assignments.

## Phase C — Blocking Validation

1. Validate the generated packet against the task-packet schema and frozen inventory without `--auto-fix`.
2. Treat assignment, schema, inventory, path, source, contract, or publication errors as blockers. Publish no partial output.
3. Preserve copied/request source context and all non-skill task fields exactly. Do not repair or mutate assignments; return only the relative generated packet path.

## Phase D — Publication Reconciliation

1. Validate the published packet against the same frozen inventory and selected skill contracts.
2. Do not pass `--auto-fix`; treat every validation error as blocking.
3. Do not trim, deduplicate, replace, or remove assignments after publication.

## Output Contract

Return the relative generated packet path only after atomic publication succeeds.

## Guardrails

- One inventory snapshot serves both planning selection and task assignment; do not recollect.
- Planning selection is uncapped and direct; task assignment is bounded to one through three skills.
- Do not invoke a planning reranker, fallback selector, score/threshold policy, or obsolete assignment mode.
- Do not manually populate, correct, reorder, or remove `skills`.
- Dynamic planning loads are passive; executable task capabilities remain packet-declared.
- Fail closed and publish atomically only after all reconciliation and validation passes.

## References

- `reference/skill-assignment.md`
- `reference/scripts/pipeline-overview.md`
- `reference/scripts/generate-task-json.md`
- `reference/scripts/error-handling-testing.md`
- `reference/authoring/core-rules.md`
- `reference/authoring/task-granularity.md`
- `reference/authoring/anti-patterns.md`
- `reference/authoring/context-preservation.md`

## Self-Validation

- One frozen inventory is used end to end.
- No reranker or fallback path is invoked.
- Planning loads are uncapped; assignments are one to three.
- Sources, task fields, and atomic publication are preserved.
