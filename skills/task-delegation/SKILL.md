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

Accept only the sole list-based Markdown envelope. Require the first non-whitespace
content to be `## Worker Result`, followed by the first exact headings
`## File Changes`, `## Verification`, and `## Deliverable` in that order. Require
bold `Status` with `COMPLETE`, `PARTIAL`, or `BLOCKED`, plus the routing and
reconciliation labels described by the template. Use ordinary bullets; reject any
table syntax or table-specific compatibility path.

Require file records to name actual paths and actions (`created`, `modified`, `deleted`,
`unchanged`, `not completed`, or `none`). Require verification records to use `PASS`,
`FAIL`, or `NOT RUN`. Reconcile every suggested target as used, superseded,
unnecessary, or not completed, and every actual write as reported. Reconcile every
declared skill as successfully loaded while allowing and reporting relevant extras;
reconcile every attempted load truthfully. Material read additions must be reported.
`COMPLETE` and `PARTIAL` require a usable non-empty payload. `BLOCKED` requires a
material blocker and a `None` payload.

If validation fails, the malformed report is not a deliverable, but do not discard it:
return or expose the original response together with precise diagnostics (missing or
misordered headings, invalid labels, malformed records, failed reconciliation, or
status/payload contradiction). Never translate malformed output into a valid report
and never use parser failure as evidence that the task itself was completed.

Everything after the first `## Deliverable` heading is opaque payload and must not be
parsed as metadata. Multiline narrative and repeated file or verification records are
valid.

## Scoped Planning Workflow

When the executable skill is `breakdown-tasks`, validate the uncapped materially
relevant planning profiles from the planning collector call separately from one to
three executable operation/documentation assignments from the operation collector
call. Require names present in the relevant collector array, existing `SKILL.md`
files within their source roots, task-contract inspection, and two-pass
reconciliation. Planning loads are passive and never grant execution or transitive
authority. Stale paths, failed loads, irrelevant names, name absent from the
relevant array, class mismatch, or unresolved assignments block.

## Dispatch Boundary

Launch exactly one worker task per invocation with the complete plaintext packet. Do not
rewrite the worker's valid envelope, extract only its status, or silently broaden the
caller's authority. A caller may choose clarification, report repair, continuation,
re-decomposition, focused re-dispatch, or stop after reviewing the full evidence.

## Execution Steps

1. Accept one selected task in any supported input format.
2. Map its fields into the eight-section plaintext packet and mark only genuinely
   unknown values with the explicit unknown marker.
3. Validate the packet and dispatch exactly one worker.
4. Validate the complete list envelope, resource reconciliation, status, and payload.
5. If malformed, expose the original response and diagnostics without accepting it as
   a deliverable; otherwise return the valid report unchanged.
