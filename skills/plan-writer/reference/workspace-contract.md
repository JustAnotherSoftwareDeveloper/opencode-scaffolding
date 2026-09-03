# Workspace Contract

## Inputs

Require one or more source documents.

Accept source categories of `analysis`, `research`, `requirements`, `design`, `notes`, and `other`.

Resolve each path and reject a missing path, a non-file path, a target outside `$CWD`, or a target inside the new plan workspace.

Follow a symbolic link only when its resolved target is a regular file inside `$CWD`.

When `PROPOSAL.md` is an input, require either a recorded accepted lifecycle state
or `readiness: decision-ready` plus explicit planning authorization from its
`decision-owner`. A stable file, successful validation, `review-ready`, recency,
or invocation does not satisfy this authorization gate.

## Workspace Layout

Create this workspace structure.

```text
.plans/<epoch-ms>-<summary-slug>/
  tasks.json
  tasks.md
  analysis/
  research/
  requirements/
  design/
  notes/
  other/
```

Create category directories only when they contain copied source documents.

Preserve the source filename unless a deterministic suffix preserves a collision distinctly.

## Validation

Require an epoch-millisecond prefix and lowercase kebab-case summary slug.

Require `tasks.json` to validate through `validate-task-structure` against the shared task-packet schema.

Require `tasks.md` to contain every final task purpose in order.

Use relative source links only, and preserve copied sources when selection or publication fails by leaving no partial output.
