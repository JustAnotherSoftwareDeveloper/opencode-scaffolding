# Section rationale

Use the smallest proportional content that makes the decision reviewable. The
canonical taxonomy is an answer-first set of nine semantic sections, and each
section owns one numbered file. Short proposals keep those files concise rather
than merging them. `PROPOSAL.md` is the ordered index, not a second copy of the
decision. Do not add decorative structure or a fixed length in place of content.

## Summary

The **Summary** gives the answer first: the proposed decision, expected outcome,
and material trade-off. It lets a reader quickly determine what is being asked
and why the choice matters before reading the supporting reasoning.

## Problem and rationale

**Problem and rationale** establishes the current state, the problem, its
consequence, and why the proposed direction follows from the evidence. It supplies
only the context needed to understand the decision and prevents the recommendation
from appearing detached from the need it addresses.

## Scope

**Scope** defines goals, exclusions, boundaries, included work, and success
measures. It limits what the decision claims to settle and makes clear which
effects or concerns are outside the decision.

## Criteria

**Criteria** defines the drivers, constraints, trade-offs, and evidence used to
judge viable approaches and the proposed shape. Evaluation criteria are not
completion tests.

## Alternatives and trade-offs

**Alternatives and trade-offs** compares viable alternatives on differentiators,
consequences, and evidence. It makes the rejected options and the cost of the
recommendation reviewable.

## Selected direction

**Selected direction** states the recommendation and decisive rationale. Link
proposal-specific implementation detail separately rather than turning this section
into an execution plan.

## Design constraints

**Design constraints** states what the format or decision must preserve or cannot
import, including governing principles, boundaries, and dependencies.

## Open owner choices

**Open owner choices** records only unresolved decisions requiring the responsible
owner, including the consequence of deferral. Researchable uncertainty belongs in
evidence work or an evidence gap, not as an owner decision.

## Acceptance criteria

**Acceptance criteria** states observable completion tests for the decision or
proposal-specific change. Keep these distinct from evaluation criteria and do not
present them as an implementation task list.

For a conditional direction, record the confirmation needed and the evidence or
trigger that would cause a revisit. Confirmation and revisit conditions support
review by making conditional commitment explicit without inventing universal
gates, dates, or lifecycle steps.

## Cross-cutting review guidance

Quick-read guidance exists to improve navigation and scanning, not to remove
material reasoning. Lead major sections with their answer, decision, or
consequence; use concise prose, descriptive sentence-case headings, deliberate
whitespace, and bullets for parallel choices or conditions. Add navigation only
when the proposal's length or structure makes it useful.

Readiness describes whether the decision path, evidence, and owner choices are
sufficient for review or for the decision authority; it is not approval,
acceptance, or a lifecycle transition. Support every material claim affecting the
decision, scope, requirement, acceptance criterion, risk, trade-off, or option
rejection with a descriptive relative source link and citation, or label it as an
assumption or evidence gap. Citation completeness does not imply strong evidence;
record evidence strength honestly.

Supporting sources is the required `11-supporting-sources.md` index, not an additional
decision section. Keep implementation detail in its separate implementation document, and
keep the proposal taxonomy forward-only: do not introduce alternate section names,
compatibility behavior, historical migration guidance, or unrelated operational
workflow.

Apply these public references when their guidance is relevant to the proposal domain.

- [UK Government Green Book](https://www.gov.uk/government/publications/the-green-book-appraisal-and-evaluation-in-central-government/the-green-book-2020)
- [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html)
- [RFC 7282](https://datatracker.ietf.org/doc/html/rfc7282)
