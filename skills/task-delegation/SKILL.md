---
name: task-delegation
description: "Use when adapting loose task information into one worker packet and forwarding it via the current supervisor's functions.subagent tool."
selection:
  role: owner
  tags:
    actions: [construct packet, assess worker result]
    inputs: [loose task information, worker report]
    outputs: [one worker packet, validated result]
    topics: [task delegation, resource reconciliation]
    environments: [functions.subagent]
  use_when: [one selected task must be dispatched and its report assessed]
  not_for: [decomposing a request into multiple tasks]
class: inline
---

# Worker Packet Construction And Result Review

Construct one worker packet from loose task information, dispatch exactly one worker,
and assess the complete returned report. This skill supplies shared policy; the caller
owns workflow decisions. A delegator may repair delegation metadata and replan its own
work. An executor must preserve an already approved task plan unchanged.

## Packet Construction

Before composing or substantively revising packet prose in `PURPOSE`, `DETAILS`,
`EXECUTION INSTRUCTIONS`, `VERIFICATION`, or `EXPECTED OUTPUT`, explicitly load
`markdown-writing-guide` and read `markdown-writing-guide -> reference/writing-quality.md`.
Apply the guidance only to prose in those five fields that is being authored or
substantively revised, and only when compatible with the supplied intent, source
evidence, resource rules and reconciliation, packet grammar, assigned operation or
delegated owner, and dispatch boundary. Preserve verbatim source context when
required; do not rewrite it solely for style. This passive load does not transfer to the
dispatched worker, alter its `SKILLS` assignment, or change any field made authoritative
after dispatch.

Accept plaintext, JSON, YAML, key-value lists, or mixed notes. Map aliases to exactly
these eight sections and mark genuinely uninferable values `UNKNOWN — not provided in
input`. Use `None` for known-empty resource arrays:

```text
## PURPOSE
## DETAILS
## FILES TO READ
## FILES TO WRITE
## SKILLS
## EXECUTION INSTRUCTIONS
## VERIFICATION
## EXPECTED OUTPUT
```

- Preserve explicit reads, writes, skills, and outcome requirements.
- Treat reads as minimum starting context.
- For ordinary canonical tasks, require exactly one assigned operation owner plus zero
  to two passive documentation skills in `SKILLS`.
- Let the worker add materially relevant documentation context, but do not let it add
  or substitute a second operation owner. Changing the operation owner requires
  supervisory adaptation and re-dispatch.
- Internal workflow packets may instead explicitly assign their single delegated
  workflow owner, such as `breakdown-tasks`.
- Treat writes as strong suggestions, not an exact authorization list. Allow minor,
  purpose-preserving adjustments only when the worker explains them. Do not add broad
  or destructive patterns.
- Reject an ambiguous multi-task object unless one task is clearly selected.

Before dispatch, the caller may improve any section while preserving the intended
outcome. After dispatch, `purpose`, `details`, `executionInstructions`, `verification`,
and `expectedOutput` are authoritative. `filesToRead` and `filesToWrite` may vary under
the worker contract. `skills` may gain passive documentation context, but the assigned
operation or delegated owner remains fixed until supervisory re-dispatch.

## Result Validation

Before assessing a result, read `~/.config/opencode/output-contract-template.md`.
It is the sole authority for the envelope grammar, required fields, vocabularies,
reconciliation rules, status invariants, and payload boundary. Reject any report that
does not conform to that contract; do not maintain a second grammar in this skill.

If validation fails, the malformed report is not a deliverable. Preserve the exact
original response and expose it to the supervisor with precise diagnostics (missing
or misordered headings, invalid labels, malformed records, failed reconciliation, or
status/payload contradiction). Never translate malformed output into a valid report
or use parser failure as evidence that the task itself was completed. The supervisor
may supply focused correction context and re-dispatch the task in a new invocation;
the original response and diagnostics remain available and unchanged.

Treat the payload boundary defined by
`~/.config/opencode/output-contract-template.md` as opaque. Do not parse payload
content as envelope metadata.

## Scoped Planning Workflow

When the executable skill is `breakdown-tasks`:

- Validate the uncapped materially relevant planning profiles from the planning
  collector separately from each generated task's assignments from the
  operation/documentation collector.
- Require each generated task to have exactly one `class: operation` owner and zero to
  two `class: documentation` assignments.
- Preserve each assignment's collector-winning `name`, `class`, and `path`, use
  existing `SKILL.md` files within their source roots, inspect `task-contract`, and
  perform two-pass reconciliation.
- Use the exact collector-winning `generic-executor` when no specialized operation
  semantically owns a task.
- Treat planning loads as passive; they never grant execution or transitive authority.
- Block on stale or substituted paths, failed loads, irrelevant names, names absent
  from the relevant array, class mismatches, invalid class composition, or unresolved
  assignments. Never repair these by similarity.

During ordinary execution, the assigned operation or delegated worker may explicitly
load a materially relevant `documentation` skill named by the packet or discovered as
needed. Treat that load as passive, non-transitive context: it cannot add steps,
authority, tools, writes, delegation, or completion evidence. Ordinary execution may
not load an additional operation owner or any `planning` skill; keep
inline/task-executor exact-declaration behavior unchanged.

## Reporting Boundary

- Preserve the canonical worker envelope without adding a local grammar.
- Put only the assigned executable operation or delegated owner in `Skills loaded`.
- Report passive documentation loads in `Reads relied on` as passive documentation,
  with their collector-winning identity when applicable.
- Reserve `Planning context loaded` for passive planning profiles from the scoped
  planning collector. It is not an executable assignment or completion evidence.
- Do not claim runtime enforcement for loading, recursion, duplication, or passive
  behavior without loader-harness evidence.

## Dispatch Boundary

Launch exactly one worker task per invocation with the complete plaintext packet. Do not
rewrite the worker's valid envelope, extract only its status, or silently broaden the
caller's authority. For a malformed result, return the original response and
diagnostics for supervisory review. A supervisor may correct only the transient
execution context and re-dispatch the complete task in a subsequent invocation;
preserve the approved task's authoritative fields and do not infer completion or
silently repair the malformed response. For the current supervisor environment,
keep the `functions.subagent` tool, one worker per invocation, and no silent
authority creep as hard boundaries.

## Execution Steps

1. Accept one selected task in any supported input format.
2. Map its fields into the eight-section plaintext packet and mark only genuinely
   unknown values with the explicit unknown marker.
3. Validate the packet and dispatch exactly one worker.
4. Read `~/.config/opencode/output-contract-template.md`, then validate the complete
   envelope, resource reconciliation, status, and payload against it.
5. If malformed, preserve the original response and precise diagnostics for the
   supervisor to decide a focused correction and re-dispatch. Do not treat the
   malformed response as a deliverable or alter it into a valid envelope.
6. When valid, return the report unchanged.
