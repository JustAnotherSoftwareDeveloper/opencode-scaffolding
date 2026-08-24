# Proposal writing style

Use these standards to make proposal language readable in full and scannable during
review. They are observable review rules, not word-count quotas.

## Readable prose

Readable prose lets a reviewer understand the claim, its consequence, and its
evidence without reconstructing the author's reasoning.

- Lead with a concrete subject and verb. Prefer “The validator rejects compound
  tasks” over “There is rejection behavior for compound tasks.”
- Use one main claim per sentence when practical. Keep multiple clauses together
  only when their relationship is necessary to understand the decision.
- Keep one connected idea per paragraph. Start a new paragraph when the claim,
  evidence, decision state, consequence, or audience question changes.
- Define an uncommon term or acronym on first use. Use one stable term for one
  concept; do not alternate synonyms merely for variety.
- Name the actor, artifact, or policy instead of relying on vague references such as
  “it,” “this,” “the system,” or “the process” when more than one referent exists.
- Prefer direct statements over throat-clearing, chronology, and meta-commentary.
  State what is true or proposed before describing how the author reached it.
- Put qualifications next to the claim they limit. Do not hide a material exception,
  uncertainty, or consequence several paragraphs later.
- Remove repetition. A later section may link to an earlier decision instead of
  restating its full rationale.

## Scannable structure

Scannable structure lets a reviewer locate the decision path without reading every
sentence first.

- The first substantive block in every canonical section answers that section's
  question. It does not begin with history, process narration, or definitions unless
  one is required to understand the answer.
- **Summary** exposes the proposed decision, expected outcome, and material trade-off.
- **Problem and rationale** exposes the current state, problem, consequence, and why
  change is warranted.
- **Scope** exposes included work, excluded work, and the success boundary.
- **Criteria** exposes how alternatives and the selected shape are judged.
- **Alternatives and trade-offs** exposes viable options, meaningful differences,
  consequences, and disposition.
- **Selected direction** exposes the recommendation and decisive rationale before
  supporting detail.
- **Design constraints** exposes non-negotiable boundaries and their consequences.
- **Open owner choices** exposes only decisions requiring an owner and the consequence
  of deferral; use `None.` when no owner choice remains.
- **Acceptance criteria** exposes observable states and how each state can be checked.
- Front-load comparable list items with short descriptive labels. Use parallel bullets
  for parallel decision roles: alternatives can expose a **Differentiator:**,
  **Consequence:**, **Disposition:**, and **Evidence:**; scope can expose included,
  excluded, and success boundaries; constraints can expose a boundary and its effect.
  Keep the grammar and role consistent across the items being compared.
- Use short bold labels as selective scan cues for adjacent decision units, such as
  **Recommendation:**, **Consequence:**, **Differentiator:**, **Disposition:**, and
  evidence-state labels such as **Assumption:**, **Evidence Gap:**, and **Open
  Question:**. Bold the label or decisive value, not the supporting claim, rationale,
  or whole paragraph. Emphasis must not imply evidence strength.
- Keep connected reasoning in focused prose. Use prose for recommendation rationale,
  causal sequences, evidence synthesis, and unequal caveats; keep one connected idea
  per paragraph and start a new paragraph when the claim, evidence, decision state,
  consequence, or audience question changes.
- Do not use Markdown tables in authored proposal documents. Choose headings for
  independent roles that need room to develop, selective bold labels for concise
  adjacent roles, parallel bullets for comparable roles, and focused prose for
  connected or unequal reasoning.
- Use descriptive sentence-case headings. Do not add headings solely to break up
  text, and do not use decorative separators or callout boxes.

## Evidence and uncertainty language

- Put a descriptive source link at the end of the sentence, paragraph, bullet, or
  labeled block it supports. Keep the link adjacent to the material claim.
- State evidence strength separately from citation presence when strength affects the
  decision.
- Use `Assumption: <statement>` for an unverified claim.
- Use `Evidence Gap: <missing evidence>` for unavailable material evidence.
- Use `Open Question: <decision>` only when the responsible owner must choose after
  researchable uncertainty has been resolved. State the consequence of deferral.
- Do not use emphasis, certainty words, or repeated citations to make weak evidence
  appear stronger.

## Verb and modality choices

- Use present tense for current behavior and evidence.
- Use “will” for an expected consequence only when the proposal establishes the
  causal path; otherwise use “is expected to” and label the assumption when material.
- Use **MUST** only for an enforced proposal or workspace contract.
- Use **SHOULD** for review guidance with a recognized exception.
- Use ordinary declarative prose for rationale, evidence, and recommendations.
- Avoid “obviously,” “simply,” “clearly,” “just,” “easy,” and similar words that hide
  reasoning or dismiss trade-offs.

## Review test

A proposal passes the language review when a reviewer can answer all of these from
the index and the first substantive block of each canonical file:

1. What decision is proposed, and what changes if it is accepted?
2. What problem and consequence justify the decision?
3. What is included and excluded?
4. How were alternatives judged, and why was this direction selected?
5. What constraints, evidence gaps, and owner choices remain?
6. What observable conditions demonstrate completion?

The review also checks that terms are stable, evidence is adjacent to claims, list
items are parallel, and no paragraph mixes unrelated claims. These are semantic
choices, not formatting quotas: do not impose heading, bullet, paragraph, sentence,
or bold-span counts.
