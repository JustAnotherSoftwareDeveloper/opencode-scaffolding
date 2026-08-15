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
2. Derive an epoch-millisecond timestamp and create a new `$CWD/.proposals/<epoch-ms>-<summary-slug>/` workspace without replacing an existing directory. Copy [the proposal templates](./templates/) into it, then copy supplied sources into their declared category directories without modifying them.
3. Before drafting, confirm authoring readiness: the decision owner and topic are known, the source set is sufficient to state the decision, and the proposal can distinguish evidence, assumptions, evidence gaps, and engineer decisions. If readiness is not met, record the specific `Evidence Gap:` or `Open Question:` rather than inventing content.
4. Keep `PROPOSAL.md` as the workspace index and metadata owner. It MUST link the numbered section files in decision order and MUST NOT duplicate their substantive prose.
5. Populate one file per canonical decision section, in this order: `01-summary.md`, `02-problem-and-rationale.md`, `03-scope.md`, `04-criteria.md`, `05-alternatives-and-trade-offs.md`, `06-selected-direction.md`, `07-design-constraints.md`, `08-open-owner-choices.md`, and `09-acceptance-criteria.md`. Populate `10-implementation.md` as the implementation overview and `11-supporting-sources.md` as the required source index. Do not combine canonical sections into one file.
6. Populate the proposal from the copied sources using the [proposal format](./reference/proposal-format.md) and [writing style](./reference/writing-style.md). Start each canonical file with the answer to its review question; use direct subjects and verbs, stable terms, focused paragraphs, parallel list items, and evidence adjacent to claims. Put conditional detail in the nearest canonical section or a separately indexed companion file when it is substantial. Omit unsupported optional detail and do not add decorative structure or fixed length requirements.
7. Derive readiness from the completed decision path, evidence, and owner-choice state, and write the result to `PROPOSAL.md` frontmatter. New workspaces start with `status: draft` and `readiness: not-ready`. Use only `not-ready`, `review-ready`, or `decision-ready`: `review-ready` requires every owner choice to be resolved and the path and evidence to be reviewable; `decision-ready` requires blocking evidence gaps to be resolved and the remaining decision record to be explicit and ready for the decision authority. Reassess a transition only when its corresponding conditions hold, and record unmet conditions as an `Evidence Gap:` or `Open Question:` rather than inflating readiness.
8. Support every material claim affecting the decision, scope, criterion, acceptance criterion, risk, trade-off, or option rejection with a descriptive relative inline link to a copied source. Use Chicago notes and bibliography for internal copied sources and external research, capture available metadata without fabrication, and list each copied source exactly once in `11-supporting-sources.md`.
9. Label unverified claims `Assumption: <statement>` and unavailable material evidence `Evidence Gap: <missing evidence>`. Resolve questions answerable through source review, analysis, research, testing, or discovery before drafting; reserve `Open Question: <question>` for a decision that still requires the responsible engineer after that work.
10. Link `10-implementation.md` from `06-selected-direction.md` and from `PROPOSAL.md`. Keep the implementation overview separate: it may describe concrete proposal-specific targets and behavior changes, but it does not redefine the decision, add generic lifecycle work, or become a runbook.
11. Keep normative language scoped to the proposal: state requirements and acceptance conditions as intended constraints for this decision, and do not turn assumptions, evidence gaps, optional guidance, or unrelated workflow conventions into requirements. Exclude generic lifecycle phases, commands, assignments, estimates, owners, and runbook detail.
12. Apply this procedure only to newly authored or deliberately revised proposal documents. Leave historical `.proposals` workspaces unchanged; do not add migration, import, assignment, estimate, or runbook behavior. Validate the completed workspace against [the workspace contract](./reference/workspace-contract.md).

## Self-Validation

- [ ] The workspace name contains an epoch-millisecond timestamp.
- [ ] The workspace name contains a lowercase kebab-case summary slug.
- [ ] Every source document exists under its declared category directory.
- [ ] `PROPOSAL.md` contains valid YAML frontmatter.
- [ ] `PROPOSAL.md` is an index, not a monolithic decision document, and links every canonical section file in order.
- [ ] `PROPOSAL.md` contains a populated `readiness` value, and it is exactly `not-ready`, `review-ready`, or `decision-ready`.
- [ ] The written readiness matches the proposal state: unresolved owner choices do not support `review-ready`; the path and evidence support `review-ready`; blocking evidence gaps are resolved and the decision record is explicit before `decision-ready`.
- [ ] Evidence and owner-choice consistency has been checked against the readiness derivation; unmet conditions are recorded as `Evidence Gap:` or `Open Question:` rather than hidden by the frontmatter value.
- [ ] `readiness` is reviewed independently from lifecycle `status`; neither field is inferred from the other, and readiness does not mean approval or acceptance. Acceptance is recorded separately by an authorized owner or plan trigger.
- [ ] `10-implementation.md` contains valid YAML frontmatter.
- [ ] The nine numbered canonical section files exist, contain their matching H2 heading, and appear in decision order in `PROPOSAL.md`.
- [ ] `11-supporting-sources.md` exists and is linked once from `PROPOSAL.md`.
- [ ] No canonical section is duplicated in `PROPOSAL.md` or another section file.
- [ ] `06-selected-direction.md` links `10-implementation.md`.
- [ ] Any substantial conditional companion document is linked from `PROPOSAL.md` and from its governing canonical section.
- [ ] The first substantive block in every canonical file answers that section's review question.
- [ ] The Summary states the decision, expected outcome, and material trade-off.
- [ ] Paragraphs retain one connected idea; terms and actors are explicit and stable.
- [ ] Bullets are parallel and front-loaded with descriptive labels when labels improve scanning.
- [ ] Tables contain genuinely comparable rows and columns rather than compressed narrative.
- [ ] Evidence, assumptions, evidence gaps, and owner questions appear next to the claims they qualify.
- [ ] Every material claim is evidence-linked.
- [ ] Every unsupported material claim is explicitly labeled.
- [ ] Authoring readiness is established, or each unmet condition is recorded as an evidence gap or engineer decision.
- [ ] Every researchable unresolved matter is labeled as an evidence gap rather than an open question.
- [ ] Each open question requires an engineer decision rather than further investigation.
- [ ] Criteria evaluate options and the proposed shape; Acceptance criteria are observable completion tests and remain distinct from evaluation criteria.
- [ ] Normative requirements and acceptance criteria are scoped to the proposal and supported by evidence or an explicit assumption.
- [ ] `10-implementation.md` groups proposal-specific changes by affected area and names each known target and modification.
- [ ] Every implementation claim is evidence-linked or explicitly labeled as an assumption.
- [ ] `10-implementation.md` contains no generic lifecycle phase unsupported by proposal evidence.
- [ ] Every concrete change uses the heading and bullet structure in the implementation format.
- [ ] No generated proposal artifact contains a template placeholder or authoring instruction.
- [ ] Optional implementation sections appear only when proposal evidence supports their content.
- [ ] The completed documents conform to the applicable short, standard, or complex guidance and [examples](./examples/README.md).

## Expected Output

Create `.proposals/<epoch-ms>-<summary-slug>/`.

Create `PROPOSAL.md` as the canonical metadata-bearing proposal index.

Create one numbered Markdown file for each canonical decision section, the implementation overview, and supporting sources.

Create `10-implementation.md` as the concrete implementation-change document with affected-area headings, concrete-change subheadings, and concise change details.

Copy source documents into their top-level category directories.

## Docs

See `./reference/README.md` for documentation of supporting files.
