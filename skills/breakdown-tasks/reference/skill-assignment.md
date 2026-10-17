# Direct Skill Selection

Assign skills only after the task boundaries are accepted. This reference covers
per-task assignment from the distinct operation and documentation results; the
[producer workflow](../SKILL.md) owns collection and pre-authoring sequence. The
documentation result also supplies the earlier passive `task-contract` load, but
that load is not a task assignment and does not authorize assignment before
boundary acceptance.

## Documentation Relevance

After selecting one operation owner, actively consider whether a documentation
profile adds distinct, material execution value beyond the task context and its
listed materials. Include a profile when it clarifies a relevant contract,
resolves a task-specific semantic, or helps prevent a likely execution error.
Availability or name similarity alone is not evidence of fit, and duplicating
guidance already supplied does not add distinct value.

For example, a worker-packet task may benefit from `customize-opencode` when
packet or result-envelope rules affect the outcome and are not already provided
in the task materials. Omit it for unrelated work, or when the relevant guidance
is already supplied. Do not impose a documentation quota or target, score or
rank candidates, or require a candidate-by-candidate rejection log. Zero
documentation assignments is valid when none adds distinct material value; the
existing maximum remains two.

## Task Assignment

For each accepted task:

1. Select exactly one `class: operation` execution owner without changing the
   accepted task boundary.
2. When one specialized operation clearly owns the task's distinct lifecycle,
   artifact contract, orchestration flow, destructive authority, or other special
   execution semantics, select that operation.
3. When no specialized operation semantically fits, select the collector-winning
   `generic-executor` operation. A missing specialized match is not a blocker.
4. Select zero to two `class: documentation` skills from the documentation
   result when they add material value under the criteria above. Documentation
   is passive and cannot replace or compete with the operation owner.
5. Store the assignment in the existing flat `skills` array: one operation
   owner followed by any selected documentation skills.

The pre-authoring `task-contract` load is passive, documentation-only, and
non-transitive; that load itself is excluded from executable task assignments.
This is not a blanket ban on assigning the `task-contract` profile: after a
boundary is accepted, it may be selected as a task's documentation assignment
when it independently adds material value under the same criteria. Such an
assignment must be reconciled like any other and counts toward the two-skill
documentation limit.

If more than one specialized operation initially appears relevant, determine
which one owns the bounded result. Do not publish two operation owners or change
an accepted boundary merely because skill coverage overlaps.

Reconcile every selected assignment against the collector-winning `name`,
`class`, and `path`. Confirm exactly one operation owner and zero to two
documentation skills before publication. Load selected documentation with the
skill tool before relying on it; reading `SKILL.md` is not a load. Inspect the
collector-winning operation contract without executing its future task. Block
on an absent name, stale or substituted path, class mismatch, failed required
load, unresolved assignment, no operation owner, more than one operation owner,
or more than two documentation skills.

Any later `task-contract` reference is an explicit read, not an automatic
recursive load.

`generic-executor` is a semantic fallback only. It must itself be the exact
collector-winning `class: operation` record. Do not use it to conceal a
collector failure, broken specialized record, failed required load, or an
unresolved assignment to a known specialized owner.

## Prohibited Semantics

Do not score, rank, threshold, rerank, clip, use lexical or path fallback, or
manually repair assignments. Do not recollect or rebuild metadata from names.
Do not select documentation merely to fill the available limit. Documentation
remains passive and non-transitive; it adds no execution authority, workflow,
tools, writes, delegation, or completion evidence.
