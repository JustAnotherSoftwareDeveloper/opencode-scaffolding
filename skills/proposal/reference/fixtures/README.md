# Proposal format fixtures

These fixtures are concrete examples for raw-Markdown and rendered-Markdown
checks. The accepted contract is defined by [proposal format](../proposal-format.md),
the [workspace contract](../workspace-contract.md), and the
[implementation format](../implementation-format.md); the fixtures are not
additional templates.

## Fixture coverage

| Example | Accepted coverage |
| --- | --- |
| [Short proposal](./short-proposal.md) | Compact answer-first decision content; the nine-section taxonomy may be compactly combined where compatible; sentence-case headings; no table of contents, empty sections, or decorative syntax; descriptive inline citations and one supporting-sources index. |
| [Standard proposal](./standard-proposal.md) | Distinct Criteria and Acceptance criteria; inline evidence links; one source index; a recommendation linked to [implementation overview](./implementation-overview.md); assumptions and evidence gaps placed in their canonical sections; conditional follow-up when confirmation or revisit details apply. |
| [Complex proposal](./complex-proposal.md) | Expanded nine-section taxonomy; justified table of contents linking proposal sections, implementation, and supporting sources without repeating source links; migration considerations; risks and mitigations; evidence gaps and owner-choice dispositions. |
| [Implementation overview](./implementation-overview.md) | Proposal-specific implementation boundary: affected-area headings, named artifact targets, concrete modifications, evidence-linked reasons, multiple changes in one area, and a separate affected area; no generic lifecycle, command, assignment, estimate, owner, or runbook content. |

## Deterministic contract checks

The examples are checked against the following accepted behaviors:

- **Taxonomy and proportionality:** verify the nine canonical sections remain
  independently findable, while short examples stay compact and complex examples
  use navigation only when useful ([proposal format](../proposal-format.md#canonical-decision-architecture)).
- **Readiness:** accept only `not-ready`, `review-ready`, or `decision-ready`,
  and keep readiness independent from status and acceptance
  ([proposal format](../proposal-format.md#metadata-and-readiness)).
- **Citations and evidence:** every material claim has a descriptive relative
  source link or an explicit `Assumption:` or `Evidence Gap:` label; source
  metadata is not fabricated, citation identity is not duplicated, and evidence
  strength is not implied by citation presence ([proposal format](../proposal-format.md#evidence-labels-and-strength), [workspace contract](../workspace-contract.md#sources-and-citation-identity)).
- **Questions:** `Open Question:` is reserved for an unresolved responsible-
  engineer decision, includes the consequence of deferring it, and is not used
  for researchable uncertainty ([proposal format](../proposal-format.md#owner-choices-and-conditional-follow-up)).
- **Conditional confirmation and revisit:** include these only when the
  direction needs alignment checking or can age, become invalid, or be reversed;
  record the trigger and consequence rather than inventing universal dates or
  gates ([proposal format](../proposal-format.md#owner-choices-and-conditional-follow-up)).
- **Migration:** new or deliberately revised documents use the canonical taxonomy
  forward-only; historical workspaces are not rewritten and legacy heading
  aliases are not retained ([proposal format](../proposal-format.md#normative-language-and-migration)).
- **Implementation boundary:** implementation content names affected targets and
  concrete modifications, keeps decision rationale in the proposal, and excludes
  generic lifecycle phases and operational runbook detail ([implementation format](../implementation-format.md#structure), [workspace contract](../workspace-contract.md#validation-observable-restrictions)).

No fixture contains authoring instructions or unresolved template placeholders.
