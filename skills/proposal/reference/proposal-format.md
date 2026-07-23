# Proposal Format

Use this reference to author readable, evidence-based proposal workspaces.
It defines presentation and content rules for `PROPOSAL.md`; the workspace
contract defines workspace integrity and metadata requirements.

## Required Decision Content

Every proposal must communicate these decision elements.
Combine compatible elements under one clear heading when that makes a short
proposal easier to review.

- **Summary:** the decision, expected outcome, and material trade-off.
- **Problem and context:** the current state, problem, and consequence.
- **Scope:** goals, exclusions, included work, and success measures.
- **Options and recommendation:** viable alternatives, the recommendation, and
  the rationale for rejecting alternatives.
- **Requirements and acceptance criteria:** intended constraints and observable
  completion conditions, kept as distinct subsections when both apply.
- **Decision record:** decisions, material objections and their disposition,
  assumptions, evidence gaps, and only unresolved engineer decisions.
- **Supporting sources:** one index of every copied source document, grouped by
  category when grouping improves scanning.

Do not create an empty section merely to satisfy this list. Omit an
inapplicable optional section and combine closely related required content when
that makes a short proposal clearer.

## Proportionality

Choose the smallest structure that makes the decision reviewable.

- **Short:** use the required decision content in compact sections. Omit a table
  of contents and optional detail.
- **Standard:** use distinct headings where they improve scanning. Include only
  decision-record, risk, migration, or implementation detail supported by the
  sources.
- **Complex:** add a table of contents when document length or multiple expanded
  sections make navigation materially useful. The table of contents links to
  sections, `implementation.md`, and the supporting-sources section; it does
  not repeat every source link.

No sentence, bullet, option, or section count is a completion requirement.

## Plain Markdown

Use sentence-case headings, ordinary paragraphs, and ordinary lists. Do not use
decorative blockquotes, callout boxes, horizontal-rule decoration, or title-case
compound headings to simulate structure. Make each heading name the information
that follows.

Templates contain document structure and normalized placeholders only. Keep
authoring instructions, conditionality rules, and examples in references such
as this one.

## Evidence

A material claim affects the decision, scope, requirement, acceptance
criterion, risk, or rejection of an option. Support each material claim with a
descriptive relative inline link to a copied source at the end of its sentence,
paragraph, or list item. Use one link for adjacent claims only when the source
clearly supports all of them.

Use these labels when appropriate:

- `Assumption: <statement>` for an unverified claim.
- `Evidence Gap: <missing evidence>` when material evidence remains unavailable.
- `Open Question: <question>` only for a decision required from the responsible
  engineer after researchable questions have been resolved.

## Navigation And Related Documents

Link `implementation.md` from the recommendation when the workspace contains an
implementation overview. Keep implementation detail in that document rather
than expanding the decision document with commands, assignments, estimates, or
runbook steps.

List each copied source once in **Supporting sources**. Use relative links only.

## Format Patterns

```markdown
## Scope

- In scope: Replace the fixed presentation rules in the proposal skill.
- Out of scope: Change the plan skill without dependency evidence.

## Requirements

- Generated proposals use sentence-case headings and ordinary lists.

## Acceptance criteria

- A short fixture has no table of contents or empty optional sections.

## Supporting sources

- [Format analysis](./analysis/format-analysis.md)
```

```markdown
## Table of contents

- [Recommendation](#recommendation)
- [Implementation overview](./implementation.md)
- [Supporting sources](#supporting-sources)
```

Use the second example only when the document's complexity justifies navigation.
