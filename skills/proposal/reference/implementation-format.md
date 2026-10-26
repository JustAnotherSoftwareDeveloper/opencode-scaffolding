# Implementation Details format

Use this reference inside the proposal's `Implementation Details` section. The section
defines the implementation boundary for planning; it is not a companion file or runbook.

## Structure

- Use one H3 for each affected area: component, interface, schema, file family,
  workflow, or tightly coupled artifact set.
- Use H4 headings when several independently reviewable concrete changes belong to one
  affected area.
- Name the target and modification in each heading.
- State the behavior change first, then preserved invariants, dependencies,
  compatibility or migration effects, failure behavior, and verification dependency
  when applicable.
- Separate affected areas when their interface, review concern, or verification differs.
- Do not group work by generic phases such as prepare, implement, integrate, or deploy.

## Concrete examples

### Operation Contract

#### `skills/proposal/SKILL.md` — Create One Authored Proposal Document

- Replace numbered-file generation with one metadata-bearing `PROPOSAL.md` and copied
  source directories.
- Preserve source bytes, readiness semantics, stable evidence labels, and historical
  workspace immutability.
- Verify the operation with profile, Markdown, workspace, and source-manifest checks.

### Validator Interface

#### `lint-md` — Dispatch Proposal Directories to Workspace Validation

- Preserve existing generic file behavior and exit codes.
- Parse proposal frontmatter with a maintained YAML parser; report parse errors as
  stable violations rather than uncaught exceptions.
- Reject Markdown tables in proposal content and verify directory behavior with focused
  library and CLI tests.

### Schema Migration

#### `source-documents` — Reconcile Copied Sources with In-Document `Sources`

- Require each safe relative manifest path to resolve to one copied regular file and
  one matching internal source entry.
- Reject traversal, absolute paths, unsafe symlinks, missing files, and duplicate or
  mismatched identities.

### Downstream Consumer

#### `plan-audit` — Read Implementation and Verification Traceability from `PROPOSAL.md`

- Replace fixed numbered-file reads with heading and frontmatter parsing.
- Preserve immutable snapshots, finding identity, status precedence, and report-only
  behavior.
- Migrate the existing regression module rather than introducing a second fixture owner.

## Optional detail

Add security, performance, reliability, or stakeholder detail only when evidence shows
that it affects the decision. Include rollout, rollback, monitoring/observability,
troubleshooting, and operational-readiness detail only when the proposal materially
affects deployment or ongoing operations; identify the relevant risk and verification
dependency. Keep applicable operational details within the affected area rather than
adding a generic operational section. State failure modes and compatibility
consequences where material. Omit empty headings.

Exclude assignments, estimates, generic lifecycle phases, unsupported dependencies,
and command-by-command execution instructions. A proposal may identify a CLI as an
affected interface and specify its required behavior without prescribing an operator
runbook.
