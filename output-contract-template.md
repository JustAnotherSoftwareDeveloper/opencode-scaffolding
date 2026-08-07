# Worker Agent Output Contract Template

This file is the sole canonical source for the worker result envelope. Producers,
validators, and specialized consumers must read and apply this contract rather than
reproducing its grammar elsewhere.

Workers return the list-based envelope below after execution and verification. Every
shown field and nested record field is required. The content after the first
`## Deliverable` heading is the exact payload requested by `EXPECTED OUTPUT` and is
opaque to envelope parsing.

```markdown
## Worker Result

- **Status:** COMPLETE, PARTIAL, or BLOCKED
- **What was done:** Concise execution summary; multiline Markdown is allowed.
- **Accomplishments:** Concrete outcomes, or None.
- **Files modified:** Actual created, modified, and deleted paths, or None.
- **Skills loaded:** Every successfully loaded executable skill, including relevant extras, or None.
- **Planning context loaded:** Successful materially relevant planning profiles from the planning collector call, or None.
- **Reads relied on:** Listed and materially discovered sources, or None.
- **Deviations:** Resource additions, superseded suggestions, or other material interpretations, or None.
- **Blocker:** Blocking reason, or None.
- **Unblock condition:** Required condition, or None.

## File Changes

- **Path:** relative/path
  - **Action:** created, modified, deleted, unchanged, not completed, or none
  - **Details:** Result, reconciliation, and reason for any deviation.
- **Path:** Repeat this record for each relevant suggested or actual target.

## Verification

- **Check:** Check name
  - **Result:** PASS, FAIL, or NOT RUN
  - **Details:** Concise evidence or reason.
- **Check:** Repeat this record for each applicable check.

## Deliverable

The exact payload required by `EXPECTED OUTPUT`, or `None` for `BLOCKED`.
```

## Status And Reconciliation Rules

- `COMPLETE` requires a non-empty payload and passing applicable checks.
- `PARTIAL` requires a non-empty payload and records incomplete non-critical work.
- `BLOCKED` requires a material blocker, an unblock condition, and `None` payload.
- Use `None` for required fields or records that have no applicable value. Do not omit
  required fields.
- Skills and reads are minimums; report successful additional skills and materially
  relied-on purposeful reads.
- Writes are suggestions. Reconcile every suggestion as used, superseded, unnecessary,
  or not completed, and report every actual write. Use an allowed `Action` value for
  the file state and state the suggestion disposition in `Details`. Explain minor
  deviations; seek clarification for major, destructive, unrelated, or
  outcome-changing deviations.
- `Files modified` lists every `created`, `modified`, or `deleted` path and is `None`
  when no files changed. `File Changes` contains one record for every suggested or
  actual target; use a single `None`/`none` record when no targets apply.
- `Planning context loaded` is `None` outside the scoped planning workflow.
- The four headings are exact and ordered. Reject table envelopes and legacy status
  prefixes. Preserve all Markdown after the first `## Deliverable` boundary verbatim.
