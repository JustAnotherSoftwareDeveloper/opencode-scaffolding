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

Require either a topic or summary.

Require explicit source-document paths.

Accept an optional source category for each path.

Assign uncategorized paths to `other`.

Return `BLOCKED: Missing proposal topic.` when the input contains no topic or summary.

Return `BLOCKED: Missing source documents.` when the input contains no source paths.

## Procedure

1. Classify and resolve each source document under [the workspace contract](./reference/workspace-contract.md), rejecting invalid paths before authoring.
2. Derive an epoch-millisecond timestamp and create a new `$CWD/.proposals/<epoch-ms>-<summary-slug>/` workspace without replacing an existing directory. Copy supplied sources into their declared category directories without modifying them.
3. Before drafting, confirm authoring readiness: the decision owner and topic are known, the source set is sufficient to state the decision, and the proposal can distinguish evidence, assumptions, evidence gaps, and engineer decisions. If readiness is not met, record the specific `Evidence Gap:` or `Open Question:` rather than inventing content.
4. Use the nine-part answer-first taxonomy, in this order: **Summary**, **Problem and rationale**, **Scope**, **Criteria**, **Alternatives and trade-offs**, **Selected direction**, **Design constraints**, **Open owner choices**, and **Acceptance criteria**. Keep these semantic areas independently findable; add conditional detail only where it improves review. Treat **Supporting sources** as the required source index, not as an additional decision section.
5. Populate the proposal from the copied sources using the [proposal format](./reference/proposal-format.md). State the decision and expected outcome first; then provide the rationale, scope, criteria, alternatives, selected direction, constraints, owner choices, and acceptance tests needed to make it reviewable. Omit unsupported optional detail and do not add decorative structure or fixed length requirements.
6. Derive readiness from the completed decision path, evidence, and owner-choice state, and write the result to `PROPOSAL.md` frontmatter. New workspaces start with `status: draft` and `readiness: not-ready`. Use only `not-ready`, `review-ready`, or `decision-ready`: `review-ready` requires every owner choice to be resolved and the path and evidence to be reviewable; `decision-ready` requires blocking evidence gaps to be resolved and the remaining decision record to be explicit and ready for the decision authority. Reassess a transition only when its corresponding conditions hold, and record unmet conditions as an `Evidence Gap:` or `Open Question:` rather than inflating readiness.
7. Support every material claim affecting the decision, scope, criterion, acceptance criterion, risk, trade-off, or option rejection with a descriptive relative inline link to the copied source at the end of the sentence, paragraph, or list item. Use Chicago notes and bibliography for internal copied sources and external research, capture available metadata without fabrication, and list each copied source exactly once under **Supporting sources**.
8. Label unverified claims `Assumption: <statement>` and unavailable material evidence `Evidence Gap: <missing evidence>`. Resolve questions answerable through source review, analysis, research, testing, or discovery before drafting; reserve `Open Question: <question>` for a decision that still requires the responsible engineer after that work.
9. Link `implementation.md` from **Selected direction** and add a table of contents only when document length or expanded structure materially improves navigation. Keep the implementation overview separate: it may describe concrete proposal-specific targets and behavior changes, but it does not redefine the decision, add generic lifecycle work, or become a runbook.
10. Keep normative language scoped to the proposal: state requirements and acceptance conditions as intended constraints for this decision, and do not turn assumptions, evidence gaps, optional guidance, or unrelated workflow conventions into requirements. Exclude generic lifecycle phases, commands, assignments, estimates, owners, and runbook detail.
11. Apply this procedure only to newly authored or deliberately revised proposal documents. Leave historical `.proposals` workspaces unchanged; do not add migration, import, assignment, estimate, or runbook behavior. Validate the completed workspace against [the workspace contract](./reference/workspace-contract.md).

## Self-Validation

- [ ] The workspace name contains an epoch-millisecond timestamp.
- [ ] The workspace name contains a lowercase kebab-case summary slug.
- [ ] Every source document exists under its declared category directory.
- [ ] `PROPOSAL.md` contains valid YAML frontmatter.
- [ ] `PROPOSAL.md` contains a populated `readiness` value, and it is exactly `not-ready`, `review-ready`, or `decision-ready`.
- [ ] The written readiness matches the proposal state: unresolved owner choices do not support `review-ready`; the path and evidence support `review-ready`; blocking evidence gaps are resolved and the decision record is explicit before `decision-ready`.
- [ ] Evidence and owner-choice consistency has been checked against the readiness derivation; unmet conditions are recorded as `Evidence Gap:` or `Open Question:` rather than hidden by the frontmatter value.
- [ ] `readiness` is reviewed independently from lifecycle `status`; neither field is inferred from the other, and readiness does not mean approval or acceptance. Acceptance is recorded separately by an authorized owner or plan trigger.
- [ ] `implementation.md` contains valid YAML frontmatter.
- [ ] `PROPOSAL.md` contains the required semantic decision content with only applicable optional sections.
- [ ] The proposal uses the nine canonical answer-first sections in order: Summary; Problem and rationale; Scope; Criteria; Alternatives and trade-offs; Selected direction; Design constraints; Open owner choices; and Acceptance criteria.
- [ ] `PROPOSAL.md` uses sentence-case headings, ordinary Markdown structures, and one supporting-sources index.
- [ ] `PROPOSAL.md` links the separate implementation overview from Selected direction.
- [ ] A table of contents appears only when it materially improves navigation and does not repeat source links.
- [ ] Every material claim is evidence-linked.
- [ ] Every unsupported material claim is explicitly labeled.
- [ ] Authoring readiness is established, or each unmet condition is recorded as an evidence gap or engineer decision.
- [ ] Every researchable unresolved matter is labeled as an evidence gap rather than an open question.
- [ ] Each open question requires an engineer decision rather than further investigation.
- [ ] Criteria evaluate options and the proposed shape; Acceptance criteria are observable completion tests and remain distinct from evaluation criteria.
- [ ] Normative requirements and acceptance criteria are scoped to the proposal and supported by evidence or an explicit assumption.
- [ ] `implementation.md` groups proposal-specific changes by affected area and names each known target and modification.
- [ ] Every implementation claim is evidence-linked or explicitly labeled as an assumption.
- [ ] `implementation.md` contains no generic lifecycle phase unsupported by proposal evidence.
- [ ] Every concrete change uses the heading and bullet structure in the implementation format.
- [ ] Neither generated document contains a template placeholder or authoring instruction.
- [ ] Optional implementation sections appear only when proposal evidence supports their content.
- [ ] The completed documents conform to the applicable short, standard, or complex guidance and [format fixtures](./reference/fixtures/README.md).

## Expected Output

Create `.proposals/<epoch-ms>-<summary-slug>/`.

Create `PROPOSAL.md` as the canonical decision document.

Create `implementation.md` as the concrete implementation-change document with affected-area headings, concrete-change subheadings, and concise change details.

Copy source documents into their top-level category directories.

## Docs

See `./reference/README.md` for documentation of supporting files.
