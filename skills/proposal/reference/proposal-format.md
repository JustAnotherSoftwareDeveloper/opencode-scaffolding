# Proposal format

Use this reference to author readable, evidence-based proposal workspaces. It
defines the presentation and content contract for the indexed section files;
the workspace contract defines workspace integrity and metadata storage.
Apply the concrete prose and scan-path rules in [proposal writing style](./writing-style.md).

## Canonical decision architecture

Every proposal uses these nine canonical, answer-first sections, in this order, with
one section per numbered Markdown file:

1. **Summary** — state the decision, expected outcome, and material trade-off.
2. **Problem and rationale** — state the current state, problem, consequence, and
   why the proposed direction follows from evidence.
3. **Scope** — state goals, exclusions, included work, boundaries, and success
   measures.
4. **Criteria** — define the drivers, constraints, trade-offs, and evidence used to
   evaluate approaches and the proposed shape.
5. **Alternatives and trade-offs** — compare viable alternatives on differentiators,
   consequences, and evidence.
6. **Selected direction** — state the recommendation and rationale. Link
   `10-implementation.md` from this section.
7. **Design constraints** — state what the format or decision must preserve or
   cannot import.
8. **Open owner choices** — record only unresolved decisions requiring the
   responsible owner, including the consequence of deferral.
9. **Acceptance criteria** — state observable completion tests for the decision or
   proposal-specific change.

**Supporting sources** is a required source index at `11-supporting-sources.md`, but
is not an additional decision section. List every copied source exactly once there.
Do not combine canonical sections into one file. A short proposal may keep each
section concise, but the section files remain separate so each decision boundary is
independently readable.

Keep implementation detail in `10-implementation.md`, not in the decision files:
commands, assignments, estimates, owners, and runbook steps are not proposal
format content. Add risks, migration, objections, benefits, confirmation, or
revisit details only as conditional subsections where they help review.

## Proportionality and quick reading

Choose the smallest structure that makes the decision reviewable:

- **Short:** use compact canonical section files and omit unsupported optional detail.
- **Standard:** use distinct headings and conditional subsections where they
  improve scanning.
- **Complex:** add indexed companion files only when expanded structure materially
  benefits navigation. Link them from `PROPOSAL.md` and their governing canonical
  section; do not repeat individual source links in the index.

Use these reviewable heuristics, not quotas:

- Use plain, concise wording, concrete subjects, strong verbs, and familiar
  terms. Do not remove a material condition, uncertainty, boundary, or citation
  for brevity.
- Lead each major section or subsection with its answer, decision, or
  consequence, followed by rationale and evidence. Put the recommendation and
  decisive trade-off in **Summary**.
- Keep sentences and paragraphs focused. Split when the claim, evidence,
  decision state, or audience question changes.
- Use bold selectively for a key term, result, decision, or material caveat;
  never use emphasis as evidence or bold whole paragraphs.
- Use bullets for parallel alternatives, criteria, requirements, risks,
  trade-offs, evidence states, and owner choices. Keep connected reasoning in
  prose.
- Use descriptive, sentence-case headings and deliberate whitespace. Do not use
  decorative blockquotes, callout boxes, horizontal-rule decoration, or
  title-case compound headings.
- Use tables only for genuinely parallel comparisons. Use prose or bullets for
  sequence, nuance, unequal evidence, long caveats, or acceptance tests.

The [proposal writing style](./writing-style.md) is authoritative when “readable,”
“scannable,” “concise,” or “answer-first” requires interpretation. In particular,
each canonical file starts with its answer, paragraphs retain one connected idea,
terms remain stable, and evidence sits next to the claim it supports.

No sentence, word, bullet, option, heading, section, or bold-span count is a
completion requirement. Readability must not fragment reasoning, hide evidence,
or merge **Scope**, **Criteria** (evaluation), and **Acceptance criteria**
(completion tests).

## Criteria and acceptance criteria

**Criteria** is the evaluation model: the qualities, drivers, constraints,
trade-offs, and evidence used to compare options and justify the recommendation.
It answers, “How will we judge the direction?” Criteria may be qualitative or
quantitative and must not be presented as completed outcomes.

**Acceptance criteria** is the completion test: observable conditions that show
the selected direction or proposal-specific change is complete. It answers,
“What must be true for this decision to be accepted?” Keep it distinct from
evaluation criteria even when both use measurable language. Put concrete
implementation targets in `10-implementation.md` when appropriate.

## Metadata and readiness

Use YAML frontmatter as the workspace metadata store. `status` remains the
proposal lifecycle state and is independent of `readiness`. Keep
`decision-owner` as the accountable field; do not add speculative checker
timestamps, DACI roles, or other authority fields.

Use only these readiness values:

- `not-ready` — the initial state; the decision path, evidence, or owner choices
  are not yet sufficient for review.
- `review-ready` — all owner choices are resolved and the path and evidence are
  reviewable. This is not approval.
- `decision-ready` — the proposal is prepared for the decision authority's
  decision. This is not acceptance.

Do not use `accepted` unless an explicit acceptance authority and workflow have
been established. Acceptance may be recorded manually or occur when a plan is
triggered from the proposal; neither event may be conflated with readiness or
`status`. Do not invent acceptance evidence, transitions, or timestamps.

## Evidence, labels, and strength

A **material claim** affects the decision, scope, requirement, acceptance
criterion, risk, trade-off, or rejection of an option. Support each material
claim with a descriptive relative inline link to a copied source at the end of
the sentence, paragraph, or list item. One link may support adjacent claims only
when the source clearly supports all of them.

Distinguish citation completeness from evidence strength:

- **Citation completeness** asks whether every material claim has a source link
  or an explicit evidence label.
- **Evidence strength** asks how directly, reliably, and sufficiently the source
  supports the claim. A citation is not proof of strong evidence; record weak or
  indirect support and do not inflate it through formatting.

Use these labels when appropriate:

- `Assumption: <statement>` for an unverified claim.
- `Evidence Gap: <missing evidence>` when material evidence is unavailable.
- `Open Question: <question>` only for an unresolved decision required from the
  responsible owner after researchable questions have been resolved. Include
  the consequence of deferring it.

Researchable questions belong in evidence work or an evidence gap, not as owner
questions. Material objections and their dispositions belong with the selected
direction or the rationale for the decision.

## Sources and citations

Use Chicago notes and bibliography for both internal copied sources and external
research. Capture available metadata without fabricating facts:

- author or responsible organization;
- title;
- site, publisher, or container when applicable;
- publication or update date when known;
- URL for external sources or workspace-relative path for copied sources; and
- access date when appropriate, especially for web material without a stable
  publication date.

Internal copied sources also require descriptive relative Markdown links to the
copied files. Give each copied source one canonical entry under **Supporting
sources**; use notes or inline links for claims without duplicating the source's
index entry. External research may be cited in Chicago notes and bibliography
and need not be copied unless the workspace contract requires it. Never invent
missing author, date, publisher, URL, or access metadata.

## Owner choices and conditional follow-up

Only the responsible decision owner may resolve an `Open Question`. Do not ask
the owner to answer a question that source review, research, testing, analysis,
or discovery can resolve. Resolved owner choices belong in the selected direction
or its rationale;
unresolved ones prevent `review-ready`.

Record confirmation conditions only when alignment or direction needs checking.
Record revisit conditions only when the direction can age, become invalid, or is
reversible. State the trigger and the consequence; do not add universal review
dates, confirmation gates, or lifecycle steps without evidence.

## Normative language and migration

Use **MUST** only for an enforced format or workspace-contract rule. Use
**SHOULD** for review guidance and recommended writing practice. Use ordinary
prose for analysis, rationale, examples, and conditional advice. Scope every
normative requirement to this proposal format; do not turn optional guidance,
assumptions, evidence gaps, or unrelated workflow conventions into requirements.

New or deliberately revised documents migrate forward to this taxonomy. Do not
retain legacy heading aliases, compatibility behavior, or alternate names for
the canonical sections. Historical proposal workspaces are not rewritten.

## Workspace index pattern

```markdown
## Proposal index

1. [Summary](./01-summary.md)
2. [Problem and rationale](./02-problem-and-rationale.md)
3. [Scope](./03-scope.md)
4. [Criteria](./04-criteria.md)
5. [Alternatives and trade-offs](./05-alternatives-and-trade-offs.md)
6. [Selected direction](./06-selected-direction.md)
7. [Design constraints](./07-design-constraints.md)
8. [Open owner choices](./08-open-owner-choices.md)
9. [Acceptance criteria](./09-acceptance-criteria.md)
10. [Implementation overview](./10-implementation.md)
11. [Supporting sources](./11-supporting-sources.md)
```
