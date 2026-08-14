---
title: "Adopt proportional proposal formatting"
slug: "adopt-proportional-proposal-formatting"
created: "0"
created-at: "1970-01-01T00:00:00Z"
status: draft
decision-owner: "responsible engineer"
readiness: decision-ready
citation-style: chicago
source-documents:
  - "../proposal-format.md"
  - "../workspace-contract.md"
---

# Adopt proportional proposal formatting

## Table of contents

- [Summary](#summary)
- [Problem and rationale](#problem-and-rationale)
- [Scope](#scope)
- [Criteria](#criteria)
- [Alternatives and trade-offs](#alternatives-and-trade-offs)
- [Selected direction](#selected-direction)
- [Design constraints](#design-constraints)
- [Open owner choices](#open-owner-choices)
- [Acceptance criteria](#acceptance-criteria)
- [Implementation overview](./implementation-overview.md)
- [Supporting sources](#supporting-sources)

## Summary

Adopt proportional proposal formatting for new and deliberately revised proposal
documents. The expected outcome is a readable, evidence-traceable decision document
whose structure expands only when the decision needs it. The material trade-off is
that authors must make a bounded judgment about complexity instead of applying one
uniform layout ([proportionality and quick-reading guidance](../proposal-format.md#proportionality-and-quick-reading);
Proposal format, “Proportionality and Quick Reading,” internal copied source).

## Problem and rationale

Fixed presentation rules make short decisions noisy and can obscure the decision
path, while an expanded decision needs navigation, explicit alternatives, and a
source index. The format therefore needs to preserve semantic completeness without
requiring every document to carry every optional presentation element ([canonical
decision architecture](../proposal-format.md#canonical-decision-architecture);
Proposal format, “Canonical Decision Architecture,” internal copied source).

Evidence Gap: No comparative measurement is available for reader effort across
fixed and proportional layouts. The recommendation relies on the format rationale
and remains weaker than a direct usability study.

## Scope

- In scope: the nine decision areas, proportional navigation, explicit option
  comparison, evidence labels, owner-question handling, conditional follow-up,
  scoped normative language, and forward migration of new proposal documents
  ([proposal format](../proposal-format.md); OpenCode project, “Proposal Format,”
  internal copied source).
- Out of scope: execution detail and changes to historical proposal workspaces
  ([workspace contract](../workspace-contract.md); OpenCode project, “Workspace
  Contract,” internal copied source).
- Success measure: a reviewer can identify the recommendation, trade-off, evidence
  gaps, unresolved engineer decision, conditional revisit trigger, acceptance tests,
  and canonical source identities without relying on an alternate heading name
  ([workspace contract](../workspace-contract.md#validation-observable-restrictions);
  OpenCode project, “Workspace Contract,” internal copied source).

## Criteria

The evaluation criteria are decision traceability, proportional readability,
evidence honesty, and forward compatibility with the current taxonomy. These are
evaluation criteria, not acceptance outcomes ([criteria and acceptance criteria](../proposal-format.md#criteria-and-acceptance-criteria);
OpenCode project, “Proposal Format,” internal copied source).

## Alternatives and trade-offs

| Option | Benefits | Consequences and trade-offs | Evidence state |
| --- | --- | --- | --- |
| Preserve a fixed expanded layout | Predictable shape and simple visual scanning | Short proposals carry unnecessary sections and navigation; the layout treats presentation as completeness | Evidence: The format guidance distinguishes proportional structure from semantic completeness ([proportionality and quick-reading guidance](../proposal-format.md#proportionality-and-quick-reading); OpenCode project, “Proposal Format,” internal copied source). |
| Remove expanded structure entirely | Compact output and fewer authoring choices | Complex decisions lose direct navigation and may hide alternatives, evidence gaps, and owner choices | Evidence Gap: No direct study establishes when navigation ceases to help; the consequence follows from the documented navigation rationale ([proportionality and quick-reading guidance](../proposal-format.md#proportionality-and-quick-reading); OpenCode project, “Proposal Format,” internal copied source). |
| Use a proportional semantic core | Preserves the canonical decision path while allowing useful navigation and conditional subsections | Authors must judge whether complexity warrants expansion, and readers may see different presentation sizes | Evidence: The format defines a nine-section taxonomy and proportional presentation ([canonical decision architecture](../proposal-format.md#canonical-decision-architecture); OpenCode project, “Proposal Format,” internal copied source). |

## Selected direction

**Recommendation:** Select the proportional semantic core. It best balances
traceability and readability, rejects fixed noise, and retains navigation when the
decision is genuinely complex. The recommendation is conditional on retaining the
canonical section purposes and the source-index identity rules ([canonical decision
architecture](../proposal-format.md#canonical-decision-architecture); OpenCode
project, “Proposal Format,” internal copied source).

See [implementation overview](./implementation-overview.md) for concrete
proposal-specific targets and behavior changes.

- **Decision:** Adopt the proportional semantic core for new and deliberately revised
  proposal documents ([canonical decision architecture](../proposal-format.md#canonical-decision-architecture);
  OpenCode project, “Proposal Format,” internal copied source).
- **Decision architecture:** Preserve decision meaning, compare options explicitly,
  separate evaluation criteria from acceptance criteria, and keep implementation
  detail outside the decision document ([section rationale](../section-rationale.md);
  OpenCode project, “Section Rationale,” internal copied source).
- **Recorded objection:** Assumption: a fixed layout is easier to validate. It was
  rejected because validation of structure does not require uniform presentation;
  the assumption is not evidence for the recommendation ([proportionality and
  quick-reading guidance](../proposal-format.md#proportionality-and-quick-reading);
  OpenCode project, “Proposal Format,” internal copied source).
- **Evidence Gap:** Reader-effort evidence comparing the options is unavailable.
  This gap limits confidence in the readability trade-off but does not prevent the
  format decision because the documented taxonomy and boundaries remain available
  ([evidence, labels, and strength](../proposal-format.md#evidence-labels-and-strength);
  OpenCode project, “Proposal Format,” internal copied source).
- **Conditional confirmation:** The responsible engineer confirms the recommended
  direction only while the nine canonical decision purposes remain independently
  findable and the source index retains one identity per copied source ([sources and
  citations](../proposal-format.md#sources-and-citations); OpenCode project,
  “Proposal Format,” internal copied source).
- **Revisit condition:** Revisit the direction if later evidence shows that
  proportional presentation routinely hides a material decision, evidence gap, or
  owner choice. The consequence is a reconsideration of the presentation rule, not
  an automatic rewrite or compatibility layer ([owner choices and conditional
  follow-up](../proposal-format.md#owner-choices-and-conditional-follow-up);
  OpenCode project, “Proposal Format,” internal copied source).
- **Readiness:** `decision-ready` records that the decision path is prepared for the
  decision authority; it is not approval or acceptance ([metadata and readiness](../proposal-format.md#metadata-and-readiness);
  OpenCode project, “Proposal Format,” internal copied source).
- **Citation completeness and strength:** Citation completeness is represented by
  links, labels, and the single source index; evidence strength remains strong for
  the internal format rules and limited for the unmeasured readability trade-off
  ([evidence, labels, and strength](../proposal-format.md#evidence-labels-and-strength);
  OpenCode project, “Proposal Format,” internal copied source).

## Design constraints

- A proposal format **MUST** preserve the nine canonical decision areas: Summary,
  Problem and rationale, Scope, Criteria, Alternatives and trade-offs, Selected
  direction, Design constraints, Open owner choices, and Acceptance criteria
  ([canonical decision architecture](../proposal-format.md#canonical-decision-architecture);
  OpenCode project, “Proposal Format,” internal copied source).
- A complex proposal **SHOULD** include a table of contents when expanded structure
  materially improves navigation, and **SHOULD** use descriptive links rather than
  repeating individual source links in navigation ([proportionality and quick-reading
  guidance](../proposal-format.md#proportionality-and-quick-reading); OpenCode
  project, “Proposal Format,” internal copied source).
- Each material claim **MUST** have a supporting citation or an explicit Evidence,
  Assumption, or Evidence Gap label; each copied source **MUST** have one canonical
  Supporting sources entry ([evidence, labels, and strength](../proposal-format.md#evidence-labels-and-strength);
  [workspace contract](../workspace-contract.md#sources-and-citation-identity);
  OpenCode project, “Proposal Format,” internal copied source; OpenCode project,
  “Workspace Contract,” internal copied source).
- Normative language **MUST** be scoped to this proposal format: **MUST** states an
  enforced format or workspace rule, while **SHOULD** states review guidance. Neither
  term applies to assumptions, evidence gaps, or unrelated workflow conventions
  ([normative language and migration](../proposal-format.md#normative-language-and-migration);
  OpenCode project, “Proposal Format,” internal copied source).
- New or deliberately revised documents **MUST** migrate forward to the current
  taxonomy without retaining legacy heading aliases, compatibility behavior, or
  alternate section names ([normative language and migration](../proposal-format.md#normative-language-and-migration);
  OpenCode project, “Proposal Format,” internal copied source).

## Open owner choices

- **Open Question:** The responsible engineer must confirm whether a proposal with a
  materially expanded proposal should use a table of contents when the links
  improve navigation without repeating source identities. **Deferral consequence:**
  leaving this choice unresolved makes the fixture's navigation behavior ambiguous
  and prevents a stable review judgment ([proportionality and quick-reading guidance](../proposal-format.md#proportionality-and-quick-reading);
  OpenCode project, “Proposal Format,” internal copied source).

## Acceptance criteria

- The fixture has all nine answer-first sections, including distinct rationale and
  scope, evaluation criteria, a comparison of viable options with consequences and
  trade-offs, a recommendation, design constraints, owner choices, and acceptance
  tests ([canonical decision architecture](../proposal-format.md#canonical-decision-architecture);
  OpenCode project, “Proposal Format,” internal copied source).
- The fixture distinguishes an unavailable comparative study as an Evidence Gap and
  does not present citation presence as evidence strength ([evidence, labels, and
  strength](../proposal-format.md#evidence-labels-and-strength); OpenCode project,
  “Proposal Format,” internal copied source).
- The fixture contains an engineer-only `Open Question:` whose consequence of
  deferral is explicit, and does not turn researchable uncertainty into an owner
  question ([owner choices and conditional follow-up](../proposal-format.md#owner-choices-and-conditional-follow-up);
  OpenCode project, “Proposal Format,” internal copied source).
- The fixture records both conditional confirmation and a trigger-based revisit with
  its consequence; it does not add a universal review date or lifecycle gate
  ([owner choices and conditional follow-up](../proposal-format.md#owner-choices-and-conditional-follow-up);
  OpenCode project, “Proposal Format,” internal copied source).
- The fixture remains a decision artifact and excludes execution detail ([workspace
  contract](../workspace-contract.md#workspace-boundaries); OpenCode project,
  “Workspace Contract,” internal copied source).

## Supporting sources

- [Proposal format](../proposal-format.md) — OpenCode project. “Proposal Format.”
  Internal reference document. Publication date not stated. Workspace-relative path:
  `skills/proposal/reference/proposal-format.md`.
- [Workspace contract](../workspace-contract.md) — OpenCode project. “Workspace
  Contract.” Internal reference document. Publication date not stated.
  Workspace-relative path: `skills/proposal/reference/workspace-contract.md`.
- [Section rationale](../section-rationale.md) — OpenCode project. “Section
  Rationale.” Internal reference document. Publication date not stated.
  Workspace-relative path: `skills/proposal/reference/section-rationale.md`.
- [UK Government Green Book](https://www.gov.uk/government/publications/the-green-book-appraisal-and-evaluation-in-central-government/the-green-book-2020)
  — HM Treasury. “The Green Book: Central Government Guidance on Appraisal and
  Evaluation.” GOV.UK. Publication date not stated in the cited source. Accessed
  August 14, 2026. https://www.gov.uk/government/publications/the-green-book-appraisal-and-evaluation-in-central-government/the-green-book-2020.
- [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html) —
  International Organization for Standardization, International Electrotechnical
  Commission, and Institute of Electrical and Electronics Engineers. “ISO/IEC/IEEE
  29148:2018: Systems and Software Engineering — Life Cycle Processes —
  Requirements Engineering.” ISO. Publication date not stated in the cited source.
  Accessed August 14, 2026. https://www.iso.org/standard/72089.html.
- [RFC 7282](https://datatracker.ietf.org/doc/html/rfc7282) — IETF. “On Consensus
  and Humming in the IETF.” RFC Editor. Publication date not stated in the cited
  source. Accessed August 14, 2026. https://datatracker.ietf.org/doc/html/rfc7282.
