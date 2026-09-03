---
title: "Add proposal-directory linting"
slug: "add-proposal-directory-linting"
created: "0"
created-at: "1970-01-01T00:00:00Z"
status: draft
readiness: review-ready
decision-owner: "responsible engineer"
source-documents:
  - "analysis/current-linter-boundary.md"
---

# Add proposal-directory linting

## Table of Contents

- [Recommendation](#recommendation)
- [Technical Rationale](#technical-rationale)
- [Questions](#questions)
- [Options Considered](#options-considered)
- [Implementation Details](#implementation-details)
- [Verification Criteria](#verification-criteria)
- [Sources](#sources)

## Recommendation

`lint-md` will accept either a Markdown file or a proposal workspace directory. File
input keeps the existing generic rules and exit codes; directory input validates the
workspace's `PROPOSAL.md`, source manifest, and relative links.

## Technical Rationale

The current file-only interface cannot verify relationships among frontmatter, copied
sources, and in-document source links. Dispatching by target type adds workspace checks
without changing the generic-file compatibility contract.

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

### Keep file-only linting

- **Differentiator:** No CLI dispatch change.
- **Consequence:** Source-manifest and workspace-link defects remain undetectable.
- **Disposition:** Rejected because one-document integrity spans more than one file.

### Add file-or-directory dispatch

- **Differentiator:** The target type selects a bounded validation profile.
- **Consequence:** The CLI and library gain directory handling while file behavior stays
  compatible.
- **Disposition:** Selected because it validates the new workspace contract without a
  second command.

## Implementation Details

### `scripts/node/src/lib/lint-md/core.ts` — dispatch by target type

- **Change:** Preserve the file pipeline and route directories to proposal validation.
- **Invariant:** Generic files keep their current rules, diagnostic ordering, and exit
  behavior.
- **Compatibility and migration:** Existing file callers require no changes.
- **Failure behavior:** Unsupported targets return a stable input diagnostic.
- **Verification dependency:** Library tests cover both target kinds.

### `scripts/node/src/lib/lint-md/proposal.ts` — validate workspace identity

- **Change:** Parse frontmatter, headings, copied sources, and relative links from
  `PROPOSAL.md`.
- **Invariant:** Validation never writes proposal content.
- **Compatibility and migration:** New workspaces use one document; historical
  workspaces remain unchanged and outside authoring validation.
- **Failure behavior:** Malformed YAML and missing sources produce stable rule IDs.
- **Verification dependency:** Focused fixtures cover valid and invalid workspaces.

### `scripts/node/src/cli/lint-md.ts` — preserve CLI behavior

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
  IDs and exit with the validation-failure code.
- Directory validation performs no writes and does not alter historical workspaces.

## Sources

- [Current linter boundary](./analysis/current-linter-boundary.md)
