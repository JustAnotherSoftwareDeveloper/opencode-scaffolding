---
name: proposal
description: "Use when creating an evidence-based decision proposal from source documents."
selection:
  role: owner
  tags:
    actions: [create decision proposal]
    inputs: [source documents]
    outputs: [decision proposal]
    topics: [decision making]
    constraints: [source grounded]
  use_when: [source documents must become a durable decision proposal]
  not_for: [general assessment or executable task planning]
class: operation
---

# Proposal

## Normalize Input

Require a topic or summary, explicit source-document paths, and a known decision
owner. Accept an optional source category for each path and assign uncategorized
paths to `other`.

Return `BLOCKED: Missing proposal topic.` when no topic or summary is supplied.
Return `BLOCKED: Missing source documents.` when no source paths are supplied.
Return `BLOCKED: Missing decision owner.` when the responsible decision authority
is unknown.

## Procedure

1. Resolve every source under [the workspace contract](./reference/workspace-contract.md).
   Reject missing files, unsafe paths, non-regular files, unsafe symlinks, duplicate
   identities, and sources outside the workspace boundary before authoring.
2. Derive an epoch-millisecond timestamp and create a new
   `$CWD/.proposals/<epoch-ms>-<summary-slug>/` workspace without replacing an
   existing directory. Copy supplied sources into their declared category
   directories without modifying them. Create only directories that contain copied
   sources.
3. Inventory the recommendation, decision owner, evidence, assumptions, evidence
   gaps, residual owner decisions, affected components and interfaces, compatibility
   and migration constraints, failure modes, implementation targets, and completion
   evidence. Treat the supplied affected-file list as the minimum discovered scope;
   inspect active consumers before declaring the proposal complete.
4. Establish authoring readiness before drafting. Resolve questions answerable by
   source review, repository inspection, analysis, research, testing, or prototyping.
   Record unavailable material evidence as `Evidence Gap: <missing evidence>` and a
   residual engineering decision as `Open Question: <question>`, including the
   decision-maker, choices, and consequence of deferral. Never convert missing
   research into an owner decision.
5. Create one metadata-bearing `PROPOSAL.md` from
   [the active template](./templates/PROPOSAL.md). It is the decision,
   implementation, verification, and source-traceability artifact. Do not create
   numbered section files, a separate implementation document, a separate source
   index, or active aliases for legacy artifacts.
6. Write the core H2 sections in this order: `Table of Contents`, `Recommendation`,
   `Technical Rationale`, `Questions`, `Options Considered`,
   `Implementation Details`, `Verification Criteria`, and `Sources`. Add a
   domain-specific H2 between `Questions` and `Options Considered` only when it adds
   decision-relevant technical detail. Omit optional subsections that add no useful
   information; do not omit a core H2.
7. Populate the document using the [proposal format](./reference/proposal-format.md),
   [writing style](./reference/writing-style.md), and
   [implementation format](./reference/implementation-format.md). Lead with the
   selected architecture or behavior. Use neutral, direct engineering prose, stable
   component names, focused paragraphs, parallel lists, selective citations, and
   explicit interfaces, invariants, dependencies, compatibility, migration, failure
   modes, and rollback constraints when material. Keep implementation detail concrete
   enough for planning without turning the proposal into a runbook.
8. Keep evaluation criteria in rationale or option comparison distinct from
   completion evidence in `Verification Criteria`. Map every intended result to a
   test, inspection, metric, observation, or bounded human-review task. Do not claim
   that structural lint proves technical correctness, prose quality, researchability,
   or reader comprehension.
9. Write valid YAML frontmatter in `PROPOSAL.md`, including `title`, `slug`, `created`,
   `created-at`, `status`, `readiness`, `decision-owner`, and `source-documents`.
   New workspaces start with `status: draft`. Use only `not-ready`, `review-ready`, or
   `decision-ready` for readiness. Derive readiness from evidence and question state:
   unresolved owner decisions prevent `review-ready`; blocking research gaps prevent
   `decision-ready`; and `decision-ready` requires an explicit decision record ready
   for the decision authority. Lifecycle status, readiness, acceptance, and approval
   are independent facts. Never infer approval from `review-ready` or mutate metadata
   to manufacture authorization.
10. Treat frontmatter `source-documents` as the canonical copied-source manifest.
    Every entry must be a safe relative path to one copied regular file and must appear
    exactly once as an internal entry under `Sources`; every copied source must appear
    in both places. External bibliography entries may appear in `Sources` but are not
    copied-source manifest entries. Use descriptive links and preserve source identity
    without fabricating metadata.
11. Label decision-dependent unverified claims `Assumption: <statement>`. Keep
    `Assumption:`, `Evidence Gap:`, and `Open Question:` distinct and machine-stable;
    do not add `Research Question:` or `Decision Question:` aliases. Put evidence and
    labels next to the claims they qualify.
12. Build a non-recursive table of contents that links every H2 exactly once in
    document order, excludes its own heading, and includes major H3 implementation or
    verification workstreams when they are needed for technical review. Verify every
    internal anchor and relative link.
13. Remove all authoring prompts, comments, and placeholders before publication.
    Reject duplicate headings, stale TOC entries, unsupported aliases, undeclared
    sources, legacy authored files, and source-manifest drift. Run applicable
    workspace, Markdown, and relative-link checks, then perform a human engineering
    review for decision clarity, technical completeness, and comprehension limits.
14. Apply this contract only to newly authored or deliberately revised proposals.
    Leave historical `.proposals/` workspaces byte-for-byte unchanged. Do not add
    migration adapters, generic lifecycle phases, assignments, estimates, approval
    authority, execution commands, or runbook behavior.

## Self-Validation

- [ ] The workspace name contains an epoch-millisecond timestamp and lowercase
      kebab-case summary slug.
- [ ] The workspace contains one authored root `PROPOSAL.md` plus only declared
      copied-source directories and files.
- [ ] Every supplied source was copied without modification and the original sources
      remain unchanged.
- [ ] `PROPOSAL.md` has valid required frontmatter and `status: draft` unless an
      authorized lifecycle fact says otherwise.
- [ ] `readiness` is valid, supported by evidence and Questions state, independent of
      lifecycle status, and never presented as approval or acceptance.
- [ ] The eight core H2 sections exist once and in order; optional domain H2 sections
      occur only between `Questions` and `Options Considered`.
- [ ] The TOC is non-recursive, complete, ordered, unique, and free of stale or broken
      anchors.
- [ ] The recommendation, decisive constraints, alternatives, affected components,
      interfaces, invariants, dependencies, compatibility, migration, failure modes,
      implementation boundary, and completion evidence are explicit where material.
- [ ] `Assumption:`, `Evidence Gap:`, and `Open Question:` retain distinct meanings;
      researchable matters are not represented as owner decisions.
- [ ] Frontmatter `source-documents`, copied regular files, and internal `Sources`
      entries reconcile exactly, with safe relative paths and no unsafe symlinks.
- [ ] Evaluation criteria and `Verification Criteria` remain distinct.
- [ ] No numbered proposal artifact, separate implementation/source index, placeholder,
      authoring comment, duplicate rationale, unsupported alias, or runbook instruction
      survives in the authored workspace.
- [ ] Deterministic checks and human engineering review are reported separately; no
      lint result is treated as proof of readability or comprehension.
- [ ] Active-consumer discovery is recorded and historical `.proposals/` workspaces
      remain unchanged.

## Expected Output

Create `.proposals/<epoch-ms>-<summary-slug>/PROPOSAL.md` as the single authored,
metadata-bearing engineering proposal. Copy each supplied source into its declared
top-level category directory. Create no numbered decision files, companion
implementation file, or separate source index.

## Docs

See [the proposal reference index](./reference/README.md).
