---
name: generic-executor
description: "Use as the default operation for executing one bounded task when no specialized operation clearly owns the result."
selection:
  role: owner
  tags:
    actions: [execute bounded task, generic execution]
    inputs: [canonical task packet]
    outputs: [bounded task result]
  use_when:
    [no specialized operation clearly owns the bounded result, ordinary repository work can be executed from the canonical task contract]
  not_for:
    [tasks that require a specialized operation's distinct lifecycle or output contract, destructive authority, packet orchestration, delegation]
class: operation
---

# Generic Executor

Execute one bounded canonical task when no specialized operation clearly owns the
result. This is the universal semantic fallback operation for ordinary execution. It
is not a recovery mechanism for broken skill collection, stale assignments, failed
required skill loads, or malformed task contracts.

## Input Contract

Use the canonical task packet already supplied to the worker. Do not invent a second
input grammar. Treat `purpose`, `details`, `executionInstructions`, `verification`,
and `expectedOutput` as authoritative after dispatch. Treat `skills` and
`filesToRead` as minimums and `filesToWrite` as strong suggestions under the worker
contract. `None` is valid for genuinely empty resource fields.

The task may involve source code, tests, scripts, configuration, documentation,
fixtures, analysis, or other bounded repository work. File type alone is never a
reason to block.

## Procedure

1. **Understand the bounded result.** Read the authoritative task fields and identify
   the concrete result and verification boundary. Do not broaden or reinterpret the
   requested outcome.
2. **Load context.** Read every declared input first, then perform purposeful
   task-related discovery when additional repository context can materially improve
   correctness. Treat explicitly loaded documentation skills as passive guidance, not
   additional authority.
3. **Execute with engineering judgment.** Follow the authoritative execution intent
   while adapting ordinary implementation details to repository reality. A path,
   command, adjacent file, implementation technique, or other procedural detail may
   change when that preserves the same bounded result.
4. **Write only what the result requires.** Prefer declared write targets. Apply the
   worker contract's minor purpose-preserving write flexibility when necessary and
   report every actual write and every deviation.
5. **Verify the result.** Run the declared verification and any directly necessary
   checks exposed by execution. Remediate failures when doing so remains inside the
   same bounded task.
6. **Report truthfully.** Return the canonical worker result envelope with actual
   reads, writes, skills, deviations, verification evidence, blockers, and deliverable.

## Adaptation Boundary

Adapt when the execution route or resource assumptions need a bounded correction but
the authoritative task outcome and verification remain unchanged. Examples include a
corrected repository path, an additional relevant read, a minor adjacent write, a
repository-native command replacing a stale procedural assumption, or an equivalent
implementation technique.

Do not use adaptation to change `purpose`, `details`, `executionInstructions`,
`verification`, or `expectedOutput` after dispatch; materially broaden scope; weaken
verification; cross a safety or authority boundary; or make a material user-owned
decision. Escalate those cases instead of improvising.

## Hard Boundaries

- Do not use this skill because collection failed, because a selected record is stale
  or mismatched, or because a required skill failed to load. Those remain blockers.
- Prefer a specialized operation when that operation clearly owns a distinct
  lifecycle, artifact contract, orchestration flow, destructive action, or other
  semantics beyond ordinary bounded execution.
- Do not delegate workers or perform packet orchestration.
- Do not infer destructive, external-system, credential, or other elevated authority
  from generic execution.
- Documentation skills are passive and non-transitive. They may improve execution but
  cannot add tools, writes, delegation, or completion evidence.

## Self-Validation

- [ ] The task remained one bounded result with unchanged authoritative fields.
- [ ] Declared inputs were read before task-related discovery or execution.
- [ ] Any additional reads, writes, or procedural adaptations were purpose-preserving
      and reported.
- [ ] File type was not treated as an authorization boundary.
- [ ] Declared verification was run or truthfully reported as not run with a blocker.
- [ ] No collector failure, stale assignment, failed required load, or malformed
      contract was hidden by generic fallback.
- [ ] No delegation, destructive authority, or material scope expansion occurred.

## Docs

See `./reference/README.md` for fallback selection and execution boundaries.
