# One-document implementation examples

This example demonstrates the concrete change shape expected inside a proposal's
`Implementation Details` section. It is not a runbook or a companion file.

## Proposal operation contract

### `skills/proposal/SKILL.md` — Create one authored `PROPOSAL.md`

- **Change:** Replace numbered-file generation with one metadata-bearing document and
  copied-source directories.
- **Invariant:** Source bytes, readiness semantics, and historical `.proposals/`
  immutability are preserved.
- **Compatibility and migration:** New workspaces use the active contract; historical
  workspaces remain unchanged.
- **Verification dependency:** Profile validation, Markdown lint, workspace lint, and
  source-manifest checks.

### `skills/proposal/reference/proposal-format.md` — Define the one-document order

- **Change:** Replace the nine-section taxonomy with the eight core H2 sequence plus
  optional domain subsections.
- **Invariant:** Recommendation-first order, stable evidence labels, and the
  evaluation-versus-completion distinction remain.
- **Verification dependency:** The reference contract is internally consistent and
  relative links resolve.

## Proposal templates

### `skills/proposal/templates/PROPOSAL.md` — Provide one active template

- **Change:** Supply one template with the eight required H2 headings, compact prompts,
  and removable authoring scaffolding.
- **Compatibility and migration:** The eleven obsolete numbered templates are removed
  and referenced only in historical evidence.
- **Verification dependency:** Generated output excludes placeholders, comments, and
  legacy authored artifacts.

## Deterministic validator

### `scripts/node/src/lib/lint-md/proposal.ts` — Add workspace validation

- **Change:** Parse `PROPOSAL.md` frontmatter and headings, enforce required metadata
  and heading order, reconcile copied sources with the manifest, and validate
  relative links and table-of-contents integrity.
- **Invariant:** Existing generic-file behavior remains compatible; no rule assesses
  prose quality or reader comprehension.
- **Compatibility and migration:** Directory input reaches workspace validation while
  file input follows the existing pipeline.
- **Verification dependency:** Library tests assert stable rule IDs for each
  deterministic check.

### `scripts/node/src/lib/lint-md/core.ts` — Dispatch by target type

- **Change:** Route files to the existing generic pipeline and directories to proposal
  validation.
- **Verification dependency:** Both paths are exercised by library and CLI tests.

## Downstream consumers

### `skills/plan-audit/scripts/plan_audit.py` — Parse one `PROPOSAL.md` baseline

- **Change:** Read the recommendation, implementation targets, verification criteria,
  questions, and source identity from headings and frontmatter instead of fixed
  numbered files.
- **Invariant:** Copied-snapshot integrity, immutable-input checks, report-only
  boundaries, and stable finding identity remain unchanged.
- **Verification dependency:** The migrated parser responds to existing test fixtures
  with stable diagnostics.

### `scripts/python/tests/test_plan_audit.py` — Migrate fixtures in place

- **Change:** Replace the eleven-file proposal fixture with one-document fixtures and
  add coverage for missing sections, traceability, source drift, and label loss.
- **Verification dependency:** The existing test module passes with clean lint and
  coverage.

## Conformance tests

### `scripts/node/tests/lint-md.test.ts` — Add workspace tests

- **Change:** Add positive one-document cases and negative fixtures for each
  deterministic workspace rule.
- **Verification dependency:** Generic-file tests pass unchanged and workspace tests
  produce expected rule IDs.