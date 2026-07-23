# Worker Agent Output Contract Template

Workers return this envelope after executing the packet and running verification. The
content below `## Deliverable` is the exact payload requested by `EXPECTED OUTPUT`.

```markdown
## Worker Result

| Field | Value |
| --- | --- |
| Status | COMPLETE, PARTIAL, or BLOCKED |
| What was done | Concise execution summary |
| Accomplishments | Concrete outcomes, or None |
| Files modified | Created, modified, or deleted path list or count, or None |
| Skills loaded | Exact successfully loaded skill names, or None |
| Deviations | Material interpretations or execution deviations, or None |
| Blocker | Blocking reason, or None |
| Unblock condition | Required condition, or None |

## File Changes

| Path | Action | Details |
| --- | --- | --- |
| relative/path, or None | created, modified, deleted, unchanged, not completed, or none | Concise result or reason |

## Verification

| Check | Result | Details |
| --- | --- | --- |
| check name, or None | PASS, FAIL, or NOT RUN | Concise evidence or reason |

## Deliverable

The exact payload required by `EXPECTED OUTPUT`, or `None` for `BLOCKED`.
```

## Status And Reconciliation Rules

- `COMPLETE` requires a non-empty Deliverable and passing applicable checks.
- `PARTIAL` requires a non-empty Deliverable and records incomplete or failed work.
- `BLOCKED` requires a blocker and unblock condition; its Deliverable is `None`.
- List every actual created, modified, or deleted path in both `File Changes` and
  `Files modified`; use `None` when there were no such changes.
- Keep report-table cells on one physical line; use `<br>` for line breaks and escape
  literal pipes as `\|`.
