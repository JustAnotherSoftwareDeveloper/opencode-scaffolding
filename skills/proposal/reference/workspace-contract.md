# Proposal workspace contract

This forward-only contract governs new or deliberately revised proposal workspaces.
Treat historical `.proposals/` workspaces as immutable evidence, not as valid output
shapes for new work.

## Workspace Shape

```text
.proposals/<epoch-ms>-<summary-slug>/
  PROPOSAL.md
  <declared-source-category>/
    <copied-source-file>
```

`PROPOSAL.md` is the only authored root document. Create a source-category directory
only when it contains supplied files. New workspaces must not contain numbered decision
files, separate implementation or source indexes, unindexed companion documents, or
active legacy aliases.

The workspace name starts with a 13-digit epoch-millisecond prefix, followed by a
hyphen and a lowercase kebab-case slug. Creation must not replace an existing
workspace.

## Source Path and File Safety

Each supplied source path must resolve from `$CWD` to a regular file inside `$CWD`.
Reject directories, devices, sockets, missing paths, absolute manifest paths, path
traversal, duplicate identities, and symlinks whose resolved target leaves `$CWD` or
the allowed source boundary. A safe symlink may be read only when its resolved target
is a regular file inside the allowed boundary; the copied result is a regular file.

Copy each source without modifying bytes. Preserve its filename unless a deterministic
collision suffix is required; block when distinct identity cannot be preserved. Allow
only the caller-declared top-level source categories and create no empty categories.

## Frontmatter

`PROPOSAL.md` contains valid YAML frontmatter with exactly the supported proposal
metadata needed by the operation:

- `title`, `slug`, `created`, and `created-at` identify the artifact;
- `status` records lifecycle state;
- `readiness` records evidence and decision closure;
- `decision-owner` identifies the responsible authority; and
- `source-documents` lists every copied source by safe workspace-relative path.

New workspaces start with `status: draft`. Readiness is one of `not-ready`,
`review-ready`, or `decision-ready`. Validate status and readiness independently.
Readiness is not approval or acceptance, and this contract does not infer or mutate an
authorized lifecycle transition.

## Source manifest and Sources identity

Frontmatter `source-documents` is the canonical copied-source manifest. Every entry:

1. is a normalized safe relative path;
2. resolves to one copied regular file inside the workspace;
3. appears exactly once as an internal link under `Sources`; and
4. has no second alias or duplicate identity.

Every copied source must have one manifest entry and one matching internal `Sources`
entry. Internal source sets therefore reconcile exactly in both directions. External
bibliography entries may appear under `Sources` but are not manifest entries. Missing,
extra, duplicate, unsafe, or mismatched entries are workspace violations.

Caller-supplied persisted research packet files are predecessor source artifacts, not
proposal-authored documents. Copy each supplied packet file unchanged under its
caller-declared, allowed top-level source category (normally `research/`) and reconcile
it like any other copied source: one safe `source-documents` entry and one matching
internal `Sources` link. External URLs and bibliographic records in the packet's
`sources.md` are references, not copied files or manifest entries.

## Document structure

Require unique H2 headings in this order: `Table of Contents`, `Recommendation`,
`Technical Rationale`, `Questions`, optional domain-specific H2 sections,
`Options Considered`, `Implementation Details`, `Verification Criteria`, and `Sources`.
Optional H2 sections may appear only in the indicated position and only when they add
decision-relevant technical detail.

The table of contents must:

- contain every H2 exactly once and in document order;
- omit its own heading and avoid self-reference;
- use internal anchors that resolve to unique headings;
- contain no stale or broken entries; and
- include H3 entries only for major technical workstreams, in their document order.

Relative Markdown links must resolve inside the workspace or to explicit external URLs.

## Evidence and Questions

Use `Assumption:` for an unverified decision dependency, `Evidence Gap:` for unavailable
material research evidence, and `Open Question:` only for a residual engineering
decision after research. An open question identifies the decision-maker, choices, and
deferral consequence. Do not add proposal-only aliases for these machine-stable labels.

Unresolved owner decisions prevent `review-ready`. Blocking evidence gaps prevent
`decision-ready`. Deterministic validation may detect labels and declared state but
cannot decide whether prose is technically correct or a question is genuinely
researchable; human review owns those judgments.

## Publication Integrity

Published output contains no unresolved placeholder, authoring comment, template
instruction, duplicate heading, stale link, undeclared copied source, legacy authored
artifact, unsupported section alias, command sequence, assignment, estimate, or generic
runbook/lifecycle content. `Implementation Details` may name concrete commands or paths
as affected interfaces but must not become an execution procedure.

Validation must report deterministic violations with stable identities and locations
when available. Human review separately evaluates recommendation quality, technical
completeness, prose, researchability, and reader comprehension.
