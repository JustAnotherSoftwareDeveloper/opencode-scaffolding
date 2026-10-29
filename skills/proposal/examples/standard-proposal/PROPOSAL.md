---
title: "Add Proposal-Directory Linting"
slug: "add-proposal-directory-linting"
created: "0"
created-at: "1970-01-01T00:00:00Z"
status: draft
readiness: review-ready
decision-owner: "responsible engineer"
source-documents:
  - "analysis/current-linter-boundary.md"
---

# Add Proposal-Directory Linting

## Table of Contents

- [Recommendation](#recommendation)
- [Technical Rationale](#technical-rationale)
- [Questions](#questions)
- [Options Considered](#options-considered)
- [Implementation Details](#implementation-details)
- [Verification Criteria](#verification-criteria)
- [Sources](#sources)

## Recommendation

`lint-md` will accept a Markdown file or a proposal workspace directory. File input
keeps the existing generic rules and exit codes. Directory input validates
`PROPOSAL.md`, checks its `source-documents` manifest against the copied sources, and
verifies relative links.

## Technical Rationale

The file-only interface checks one document's syntax but cannot verify that the
`source-documents` manifest matches the copied sources or that relative links resolve
within the workspace. Dispatching by target type adds those workspace checks without
changing the generic-file compatibility contract.

The implementation must preserve diagnostic ordering and exit code `1` for validation
violations. Parse or filesystem failures must become stable diagnostics rather than
uncaught exceptions.

## Questions

- Assumption: Existing callers depend on generic-file diagnostics and exit codes but
  do not pass directories accidentally.
- Evidence Gap: Production invocation frequency is unavailable; this does not block
  review because the compatibility contract is covered by regression tests.
- Open Question: None.

## Options Considered

### Keep File-Only Linting

- **Differentiator:** No CLI dispatch change.
- **Consequence:** Source-manifest and workspace-link defects remain undetectable.
- **Disposition:** Rejected because copied-source identity and relative links require
  workspace context.

### Add File-or-Directory Dispatch

- **Differentiator:** The target type selects a bounded validation profile.
- **Consequence:** The CLI and library gain directory handling while file behavior stays
  compatible.
- **Disposition:** Selected because it validates the new workspace contract through the
  existing command.

## Implementation Details

### `scripts/node/src/lib/lint-md/core.ts` — Dispatch by Target Type

- **Change:** Preserve the file pipeline and route directories to proposal validation.
- **Invariant:** Generic files keep their current rules, diagnostic ordering, and exit
  behavior.
- **Compatibility and migration:** Existing file callers require no changes.
- **Failure behavior:** Unsupported targets return a stable input diagnostic.
- **Verification dependency:** Library tests cover both target kinds.

### `scripts/node/src/lib/lint-md/proposal.ts` — Validate Workspace Identity

- **Change:** Parse `PROPOSAL.md` frontmatter and headings; validate its copied sources
  and relative links against the workspace.
- **Invariant:** Validation never writes proposal content.
- **Compatibility and migration:** New workspaces use one document; historical
  workspaces remain unchanged and outside authoring validation.
- **Failure behavior:** Malformed YAML and missing sources produce stable rule IDs.
- **Verification dependency:** Focused fixtures cover valid and invalid workspaces.

### `scripts/node/src/cli/lint-md.ts` — Preserve CLI Behavior

- **Change:** Accept a file or directory and format aggregated diagnostics.
- **Invariant:** Help text and established exit codes remain stable.
- **Compatibility and migration:** Existing automation continues to invoke the same
  command.
- **Failure behavior:** Input errors are reported once without a stack trace.
- **Verification dependency:** CLI tests assert output and exit status.

## Verification Criteria

- Existing generic-file library and CLI tests pass unchanged.
- A valid one-document workspace exits successfully.
- Missing sources, malformed frontmatter, and broken relative links report stable rule
  IDs and exit with code `1`.
- Directory validation performs no writes and does not alter historical workspaces.

## Sources

- [Current linter boundary](./analysis/current-linter-boundary.md)
