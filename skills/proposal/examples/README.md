# Proposal format examples

These examples support raw-Markdown and rendered-Markdown checks. The accepted
contract is defined by [proposal format](../reference/proposal-format.md), the
[workspace contract](../reference/workspace-contract.md), and the
[implementation format](../reference/implementation-format.md). The
[writing style](../reference/writing-style.md) defines readability and scanability.
The examples are not additional templates.

## Example coverage

| Example | Accepted coverage |
| --- | --- |
| [Short proposal](./short-proposal/PROPOSAL.md) | Compact per-section workspace with a metadata-bearing index and concise numbered artifacts. |
| [Standard proposal](./standard-proposal/PROPOSAL.md) | Per-section workspace with distinct Criteria and Acceptance criteria, evidence links, one source index, and a separate implementation overview linked from the index and selected direction. |
| [Complex proposal](./complex-proposal/PROPOSAL.md) | Per-section workspace with an indexed conditional companion document for risks and revisit conditions, without duplicating canonical section prose. |
| [Implementation overview](./standard-proposal/10-implementation.md) | Proposal-specific implementation boundary: affected-area headings, named artifact targets, concrete modifications, and no generic lifecycle or runbook content. |

## Deterministic contract checks

The examples are checked against the following accepted behaviors:

- **Taxonomy and proportionality:** verify `PROPOSAL.md` indexes nine separate
  canonical section files in order, short examples keep those files compact, and
  complex examples index companion files only when useful
  ([proposal format](../reference/proposal-format.md#canonical-decision-architecture)).
- **Language:** verify each canonical file answers its review question first, uses
  direct actors and stable terms, keeps evidence next to claims, and uses parallel
  lists or genuinely comparable tables
  ([writing style](../reference/writing-style.md#review-test)).
- **Readiness:** accept only `not-ready`, `review-ready`, or `decision-ready`,
  and keep readiness independent from status and acceptance
  ([proposal format](../reference/proposal-format.md#metadata-and-readiness)).
- **Citations and evidence:** every material claim has a descriptive relative
  source link or an explicit `Assumption:` or `Evidence Gap:` label; source
  metadata is not fabricated, citation identity is not duplicated, and evidence
  strength is not implied by citation presence ([proposal format](../reference/proposal-format.md#evidence-labels-and-strength), [workspace contract](../reference/workspace-contract.md#sources-and-citation-identity)).
- **Questions:** `Open Question:` is reserved for an unresolved responsible-
  engineer decision, includes the consequence of deferring it, and is not used
  for researchable uncertainty ([proposal format](../reference/proposal-format.md#owner-choices-and-conditional-follow-up)).
- **Conditional confirmation and revisit:** include these only when the
  direction needs alignment checking or can age, become invalid, or be reversed;
  record the trigger and consequence rather than inventing universal dates or
  gates ([proposal format](../reference/proposal-format.md#owner-choices-and-conditional-follow-up)).
- **Migration:** new or deliberately revised documents use the canonical taxonomy
  forward-only; historical workspaces are not rewritten and legacy heading
  aliases are not retained ([proposal format](../reference/proposal-format.md#normative-language-and-migration)).
- **Implementation boundary:** implementation content names affected targets and
  concrete modifications, keeps decision rationale in the proposal, and excludes
  generic lifecycle phases and operational runbook detail ([implementation format](../reference/implementation-format.md#structure), [workspace contract](../reference/workspace-contract.md#validation-observable-restrictions)).

No example contains authoring instructions, unresolved template placeholders, or a
monolithic `PROPOSAL.md` decision body.
