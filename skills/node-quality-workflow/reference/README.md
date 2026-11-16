# Reference Index

This folder indexes the supporting reference for the
[standalone quality workflow](../SKILL.md). The subject is standalone type-check, lint,
and format diagnostics and configuration for TypeScript in Node.js or Bun projects; a
JavaScript-only request is reported as out of scope. This page is an index only: it
carries no procedure, permission, delegation, or completion claim.

## Route By Question

- [Quality Scope And Mutation](quality-scope-and-mutation.md) — what does a quality tool
  do, which program or files does a TypeScript check cover, why is a changed file absent
  from a green check, does a command write, and what details bound the report?
- [Lint And Format Target Selection](lint-and-format-target-selection.md) — which files
  did this ESLint, Biome, or Prettier invocation target, which configuration and ignore
  rules applied, and which files received diagnostics?

## Concern-To-Section Map

- Why a changed file is absent from a green check:
  [Diagnose A Changed File Missing From A Green Check](quality-scope-and-mutation.md#diagnose-a-changed-file-missing-from-a-green-check).
- Which files a TypeScript check includes:
  [Establish The Actual Target Set](quality-scope-and-mutation.md#establish-the-actual-target-set).
- Whether a command reports diagnostics or writes:
  [Distinguish Diagnostics From Writes](quality-scope-and-mutation.md#distinguish-diagnostics-from-writes).
- Which files ESLint, Biome, or Prettier select, and what each tool reads versus reports:
  [ESLint Per-File Configuration Lookup](lint-and-format-target-selection.md#eslint-per-file-configuration-lookup),
  [Biome Working Directory, Configuration, And Scanner Inputs](lint-and-format-target-selection.md#biome-working-directory-configuration-and-scanner-inputs),
  [Prettier Path Expansion, Configuration, And Ignore Rules](lint-and-format-target-selection.md#prettier-path-expansion-configuration-and-ignore-rules),
  and [When No Files Match](lint-and-format-target-selection.md#when-no-files-match).
- Where a finding or configuration change goes:
  [Route Findings To Owners](quality-scope-and-mutation.md#route-findings-to-owners) and
  [Route Findings And Configuration Changes](lint-and-format-target-selection.md#route-findings-and-configuration-changes).

## Applicability

Examples and commands on both pages depend on the installed tool versions and each
project's own invocation. Verify the target project's tools, versions, working directory,
configuration, and scripts before relying on a described result. A JavaScript source
edit, dependency or runtime change, test or coverage outcome, package artifact, or
`scripts/node/` change stays with its outcome owner.
