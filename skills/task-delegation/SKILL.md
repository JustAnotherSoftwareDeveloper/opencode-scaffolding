---
name: task-delegation
description: "Use when adapting loose task information into one worker packet and forwarding it via the task tool."
selection:
  role: owner
  tags:
    actions: [construct packet, assess worker result]
    inputs: [loose task information, worker report]
    outputs: [one worker packet, validated result]
    topics: [task delegation, resource reconciliation]
    environments: [task tool]
  use_when: [one selected task must be dispatched and its report assessed]
  not_for: [decomposing a request into multiple tasks]
class: inline
---

# Task Delegation

Construct one worker packet from loose task information, dispatch exactly one worker,
and assess the complete returned report. This skill supplies shared policy; the caller
owns workflow decisions. A delegator may repair delegation metadata and replan its own
work. An executor must preserve an already approved task plan unchanged.

## Packet Construction

Accept plaintext, JSON, YAML, key-value lists, or mixed notes. Map aliases to exactly
these eight sections and mark genuinely uninferable values `UNKNOWN — not provided in
input`; known-empty resource arrays become `None`:

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

Preserve explicit reads, writes, skills, and outcome requirements. Reads and skills are
minimums for the worker, not closed sets. Writes are strong suggestions, not an exact
authorization list: the worker may make a minor purpose-preserving adjustment and must
explain it. Do not add broad or destructive patterns. Reject an ambiguous multi-task
object unless one task is clearly selected.

Before dispatch, the caller may improve any section while preserving the intended
outcome. After dispatch, `purpose`, `details`, `executionInstructions`, `verification`,
and `expectedOutput` are authoritative. Only `skills`, `filesToRead`, and
`filesToWrite` may vary during execution.

## Result Validation

Before assessing a result, read `output-contract-template.md` from the workspace root.
It is the sole authority for the envelope grammar, required fields, vocabularies,
reconciliation rules, status invariants, and payload boundary. Reject any report that
does not conform to that contract; do not maintain a second grammar in this skill.

If validation fails, the malformed report is not a deliverable, but do not discard it:
return or expose the original response together with precise diagnostics (missing or
misordered headings, invalid labels, malformed records, failed reconciliation, or
status/payload contradiction). Never translate malformed output into a valid report
and never use parser failure as evidence that the task itself was completed.

Treat the payload boundary defined by `output-contract-template.md` as opaque. Do not
parse payload content as envelope metadata.

## Scoped Planning Workflow

When the executable skill is `breakdown-tasks`, validate the uncapped materially
relevant planning profiles from the planning collector call separately from one to
three executable operation/documentation assignments from the operation collector
 call. Require each assignment to preserve the collector-winning `name`, `class`, and
 `path`, existing `SKILL.md`
files within their source roots, task-contract inspection, and two-pass
reconciliation. Planning loads are passive and never grant execution or transitive
 authority. Stale paths or substituted paths, failed loads, irrelevant names, a name absent
 from the relevant array, class mismatch, or unresolved assignments block; do not
 repair by similarity.

During ordinary execution, an operation or delegated worker may explicitly load a
materially relevant `documentation` skill named by the packet or workflow. Treat that
load as passive, non-transitive context: it cannot add steps, authority, tools, writes,
delegation, or completion evidence. Ordinary execution may not load `planning` skills;
keep inline/task-executor exact-declaration behavior unchanged.

## Reporting Boundary

Preserve the canonical worker envelope without adding a local grammar. `Skills loaded`
contains executable skills only. Report passive documentation loads in `Reads relied
on` as passive documentation with their collector-winning identity when applicable.
Reserve `Planning context loaded` for passive planning profiles from the scoped planning
collector; it is not an executable assignment or completion evidence. Do not claim
runtime enforcement for loading, recursion, duplication, or passive behavior without
loader-harness evidence.

## Dispatch Boundary

Launch exactly one worker task per invocation with the complete plaintext packet. Do not
rewrite the worker's valid envelope, extract only its status, or silently broaden the
caller's authority. When a result is malformed, the delegator does not stop at a
fixed decision tree — troubleshoot the failure, infer the worker's intent from
partial evidence, and choose whatever reasonable next step reaches the intended
outcome. The only inviolable constraints are the task tool, one worker per
invocation, and no silent authority creep.

## Execution Steps

1. Accept one selected task in any supported input format.
2. Map its fields into the eight-section plaintext packet and mark only genuinely
   unknown values with the explicit unknown marker.
3. Validate the packet and dispatch exactly one worker.
4. Read `output-contract-template.md`, then validate the complete envelope, resource
   reconciliation, status, and payload against it.
5. If malformed, troubleshoot and infer the narrowest correction; do not stop at the
   first validation failure unless the evidence is genuinely insufficient.
6. When valid, return the report unchanged.
