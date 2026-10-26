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
2. Before creating a workspace or copying any source, use [bounded research
   evidence](./reference/research-evidence.md)
   to decide whether external, comparative, or prior-art evidence not covered by the
   supplied sources can materially change the recommendation.
   - If no material research is needed, or the supplied sources already cover it,
     follow the existing source-only path. Do not require or create a research packet.
   - If material research is needed but absent, stop before creating a workspace or
     drafting. Report what evidence is missing and require the caller to complete and
     persist research separately, then resume with explicit paths to the packet files.
     Do not conduct research, delegate research or proposal drafting, or invoke another
     operation automatically. Do not rely on search snippets or accept an unpersisted
     conversational summary as completed evidence.
   - If a caller-supplied persisted packet is present, require explicit source paths
     for `README.md`, `answer.md`, `sources.md`, and `claims.md`, and check completeness
     against the research reference. If any file is missing or inadequately documented,
      block as above. Documented unavailable or unresolved findings do not by themselves
      make a packet incomplete; carry them forward as `Evidence Gap:` records and assess
      their effect on readiness. The complete packet is a predecessor source artifact,
      not content created inside the proposal workspace; include its files among the
      sources copied in step 3.
3. After source resolution and research intake permit authoring, derive an
   epoch-millisecond timestamp and create a new
   `$CWD/.proposals/<epoch-ms>-<summary-slug>/` workspace without replacing an
   existing directory. Copy supplied sources into their declared category
   directories without modifying them. Create only directories that contain copied
   sources.
4. Inventory the recommendation, decision owner, evidence, assumptions, evidence
   gaps, residual owner decisions, affected components and interfaces, compatibility
   and migration constraints, failure modes, implementation targets, and completion
   evidence. Treat the supplied affected-file list as the minimum discovered scope;
   inspect active consumers before declaring the proposal complete.
5. Establish authoring readiness before drafting. Resolve questions answerable by
   supplied-source review, repository inspection, analysis, separately persisted
   research, testing, or prototyping; do not conduct or delegate new research within
   this operation. Record unavailable material evidence as
   `Evidence Gap: <missing evidence>` and a residual engineering decision as
   `Open Question: <question>`, including the decision-maker, choices, and consequence
   of deferral. Never convert missing research into an owner decision.
6. For direct execution, before drafting, load `markdown-writing-guide` as passive
   documentation context and read `markdown-writing-guide -> reference/writing-quality.md`.
   Apply it only to authored `PROPOSAL.md` prose as a supplement to the [proposal
   format](./reference/proposal-format.md) and [writing
   style](./reference/writing-style.md); preserve the required section order,
   readiness semantics, source traceability, and human engineering review. During
   canonical packet execution, use the guide only when declared in the packet's
   documentation assignments and already loaded; never self-load it. Then create one
   metadata-bearing `PROPOSAL.md` from
      [the active template](./templates/PROPOSAL.md), as the sole authored decision,
      implementation, verification, and source-traceability artifact. No companion
      implementation/source files or active legacy aliases. See [proposal format, core
     document order](./reference/proposal-format.md#core-document-order).
7. Write the required core sections in the order defined by [proposal
     format](./reference/proposal-format.md#core-document-order); add an optional
     domain-specific H2 only in its permitted position when it adds decision-relevant
     technical detail.
8. Apply [proposal format](./reference/proposal-format.md), [writing
     style](./reference/writing-style.md), and [implementation
     format](./reference/implementation-format.md). Keep implementation details concrete
     enough for planning, not a runbook.
9. Distinguish option-evaluation criteria from completion evidence and map every
     intended result to observable verification. Structural checks do not establish
     technical correctness, prose quality, researchability, or comprehension; see
     [proposal format, Verification Criteria](./reference/proposal-format.md#verification-criteria)
     and [writing style, Human evidence boundary](./reference/writing-style.md#human-evidence-boundary).
10. Establish readiness from evidence and question state without implying approval or
     acceptance. Use [proposal format, Metadata and readiness](./reference/proposal-format.md#metadata-and-readiness)
     and [workspace contract, Frontmatter](./reference/workspace-contract.md#frontmatter)
     for exact metadata and readiness rules.
11. Reconcile copied-source identity through the canonical `source-documents` manifest
     and `Sources`; use [workspace contract, Source manifest and Sources
     identity](./reference/workspace-contract.md#source-manifest-and-sources-identity).
12. Keep `Assumption:`, `Evidence Gap:`, and `Open Question:` distinct and do not turn
     researchable uncertainty into an owner decision; use [proposal format,
     Questions](./reference/proposal-format.md#questions) and [workspace contract,
     Evidence and Questions](./reference/workspace-contract.md#evidence-and-questions).
13. Verify the table of contents, anchors, and relative links under [workspace
     contract, Document structure](./reference/workspace-contract.md#document-structure).
14. Before publication, run applicable workspace, Markdown, and relative-link checks,
     then perform a human engineering review for decision clarity and technical
     completeness. Keep deterministic evidence separate from human judgments; see
     [workspace contract, Publication Integrity](./reference/workspace-contract.md#publication-integrity)
     and [writing style, Human evidence boundary](./reference/writing-style.md#human-evidence-boundary).
15. Apply this contract only to newly authored or deliberately revised proposals.
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
- [ ] For material research, the proposal operation blocks before authoring when the
      packet is absent or incomplete, and copies each file from a complete
      caller-supplied packet unchanged.
- [ ] Research intake and packet completeness are resolved before workspace creation
      or source copying; missing or incomplete material research stops at step 2.
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

See [the proposal reference index](./reference/README.md) and [bounded research
evidence](./reference/research-evidence.md).
