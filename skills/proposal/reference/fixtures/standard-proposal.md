---
title: "Adopt proportional proposal navigation"
slug: "adopt-proportional-proposal-navigation"
created: "0"
created-at: "1970-01-01T00:00:00Z"
status: draft
decision-owner: "responsible engineer"
readiness: decision-ready
citation-style: chicago
source-documents:
  - "../proposal-format.md"
  - "../implementation-format.md"
---

# Adopt proportional proposal navigation

## Summary

Adopt proportional navigation: omit a table of contents for short proposals and
add one when expanded structure materially improves navigation. This keeps short
proposals easy to scan while making complex decisions findable (Evidence; strong
support: [proposal format guidance](../proposal-format.md)).[^1] The trade-off is
a small authoring judgment about complexity instead of a uniform layout.

## Problem and rationale

An unconditional table of contents repeats navigation in short proposals, while a
complex proposal benefits from direct links to its sections, implementation
overview, and source index (Evidence; strong support: [proposal format guidance](../proposal-format.md)).[^1]
Repeated claims may cite the same source again, but the source index should contain
one canonical entry rather than duplicate entries (Evidence; strong support:
[source and citation rules](../proposal-format.md#sources-and-citations)).[^2]

## Scope

- In scope: proportional table-of-contents use, descriptive section links, and one
  supporting-source index (Evidence; strong support: [proposal format guidance](../proposal-format.md)).[^1]
- Out of scope: source preservation and implementation-detail boundaries (Evidence;
  strong support: [implementation format](../implementation-format.md)).[^3]
- Success measure: each material claim has a descriptive source link or an explicit
  evidence label, and each copied source appears once in Supporting sources
  (Evidence; strong support: [citation rules](../proposal-format.md#sources-and-citations)).[^2]

## Criteria

These criteria judge the alternatives; they are not completion outcomes:

- **Scanability:** short proposals should not carry navigation that adds noise
  (Evidence; strong support: [quick-reading guidance](../proposal-format.md)).[^1]
- **Findability:** expanded proposals should make sections, implementation context,
  and sources easy to reach (Evidence; strong support: [quick-reading guidance](../proposal-format.md)).[^1]
- **Traceability:** material claims should be attributable through descriptive links,
  notes, and a non-duplicated source index (Evidence; strong support: [citation rules](../proposal-format.md#sources-and-citations)).[^2]

## Alternatives and trade-offs

| Alternative | Benefits | Costs and risks | Assessment |
|---|---|---|---|
| Always include a table of contents | Consistent navigation | Adds noise to short proposals | Reject because the format guidance makes navigation proportional to complexity (Evidence; strong support: [proposal format guidance](../proposal-format.md)).[^1] |
| Never include one | Brief output | Makes expanded proposals harder to navigate | Reject because expanded structure can materially benefit from direct links (Evidence; strong support: [proposal format guidance](../proposal-format.md)).[^1] |
| Include it when complexity warrants it | Matches navigation to reader need | Requires a small authoring judgment | Recommended on the cited proportionality guidance (Evidence; strong support: [proposal format guidance](../proposal-format.md)).[^1] |

## Selected direction

Use the conditional option and link the separate [implementation overview](./implementation-overview.md). Implementation detail remains outside this decision document (Evidence; strong support: [implementation format](../implementation-format.md)).[^3]

## Design constraints

- Internal copied sources retain descriptive relative links and one canonical source
  identity in Supporting sources (Evidence; strong support: [source and citation rules](../proposal-format.md#sources-and-citations)).[^2]
- External research retains its stable URL and complete available Chicago metadata
  (Evidence; strong support: [Chicago Manual of Style citation guide](https://www.chicagomanualofstyle.org/tools_citationguide/citation-guide-1.html)).[^4]
- A repeated citation reuses the source identity and may use a shortened note; it
  does not create another source entry (Evidence; strong support: [source and citation rules](../proposal-format.md#sources-and-citations)).[^2]

## Open owner choices

No owner choice remains open for this fixture. The responsible engineer selected
conditional navigation, so deferral has no unresolved consequence (Evidence; strong
support: [proposal format guidance](../proposal-format.md)).[^1]

## Acceptance criteria

- The fixture contains the nine canonical decision sections, distinct evaluation
  criteria, and distinct acceptance criteria (Evidence; strong support: [decision architecture](../proposal-format.md#canonical-decision-architecture)).[^1]
- The recommendation links the [implementation overview](./implementation-overview.md),
  and proposal-specific implementation detail remains outside this decision document
  (Evidence; strong support: [implementation format](../implementation-format.md)).[^3]
- Internal copied sources use descriptive relative links and complete Chicago notes
  and bibliography entries; external research uses a stable URL and complete
  available metadata (Evidence; strong support: [source and citation rules](../proposal-format.md#sources-and-citations)).[^2]
- A repeated use of an internal source uses a shortened note and does not duplicate
   that source's canonical Supporting sources entry (Evidence; strong support: [source and citation rules](../proposal-format.md#sources-and-citations)).[^2]
- The same internal source is cited again with a shortened note in this fixture.[^8]
- Citation completeness is recorded separately from evidence strength in this
  proposal (Evidence; strong support: [evidence strength guidance](../proposal-format.md#evidence-labels-and-strength)).[^5]

The selected direction also records the durable decision evidence:

- **Decision:** Make table-of-contents generation conditional on useful navigation
  (Evidence; strong support: [proportionality guidance](../proposal-format.md#proportionality-and-quick-reading)).[^1]
- **Resolved owner choice:** The responsible engineer selected the conditional option;
  no owner decision remains open for this fixture (Evidence; strong support: [owner choices guidance](../proposal-format.md#owner-choices-and-conditional-follow-up)).[^6]
- **Citation completeness:** Complete for the material claims in this fixture because
  each has a descriptive source link or an explicit label (Evidence; strong support:
  [citation completeness guidance](../proposal-format.md#evidence-labels-and-strength)).[^5]
- **Evidence strength:** Strong for the internal format rules; citation presence does
  not by itself establish evidence strength (Evidence; strong support: [evidence strength guidance](../proposal-format.md#evidence-labels-and-strength)).[^5]
- **Readiness:** This fixture is `decision-ready`; readiness is independent of
  `status: draft` and does not record approval or acceptance (Evidence; strong support:
  [readiness rules](../proposal-format.md#metadata-and-readiness)).[^7]

## Readiness-case coverage

The following are documentation-only fixture cases. They describe metadata and
expected classification; they are not additional proposal content.

### Valid not-ready case

```yaml
status: draft
readiness: not-ready
```

This is valid when the decision path, evidence, or owner choices are insufficient
for review. The fixture records the specific `Evidence Gap:` or `Open Question:` and
keeps the proposal `not-ready`; it does not invent a decision, approval, or
acceptance. `status: draft` remains a separate lifecycle field (Evidence; strong
support: [readiness rules](../proposal-format.md#metadata-and-readiness)).[^7]

### Valid review-ready case

```yaml
status: draft
readiness: review-ready
```

This is valid only after every owner choice is resolved and the path and evidence
are reviewable. It is still not approval or acceptance (Evidence; strong support:
[readiness rules](../proposal-format.md#metadata-and-readiness)).[^7]

### Valid decision-ready case

The frontmatter and selected direction above are the valid `decision-ready` case. Its
`status: draft` is intentionally preserved to show that readiness does not replace
status and does not imply approval or acceptance (Evidence; strong support:
[readiness rules](../proposal-format.md#metadata-and-readiness)).[^7]

### Invalid or inconsistent cases

The following snippets are negative fixtures only. They MUST NOT be treated as
valid proposal metadata or silently converted into valid proposal content.

```yaml
# Invalid value: not in the accepted readiness contract.
status: draft
readiness: ready

# Invalid without an explicitly established acceptance authority and workflow.
status: draft
readiness: accepted

# Inconsistent: an unresolved owner choice prevents review-ready.
status: draft
readiness: review-ready
open-owner-choice: "Which option should the responsible engineer select?"
```

Expected handling is observable in the fixture: classify the first two snippets as
invalid readiness metadata, and classify the third as inconsistent readiness. None
counts as `review-ready`, `decision-ready`, approval, or acceptance; preserve the
actual `status` separately rather than inferring readiness from it (Evidence; strong
support: [readiness rules](../proposal-format.md#metadata-and-readiness)).[^7]

## Supporting sources

### Internal copied sources

- [Proposal format](../proposal-format.md) — canonical internal source identity for the proposal-format guidance cited in notes 1, 2, 5, 6, and 7.
- [Implementation format](../implementation-format.md) — canonical internal source identity for the implementation-boundary guidance cited in note 3.

### External research

- [Chicago Manual of Style Online, “Notes and Bibliography: Sample Citations”](https://www.chicagomanualofstyle.org/tools_citationguide/citation-guide-1.html) — canonical external source identity for note 4.

## Notes

1. Proposal format, “Proportionality and Quick Reading,” [copied source](../proposal-format.md).
2. Proposal format, “Sources and Citations,” [copied source](../proposal-format.md).
3. Implementation format, [copied source](../implementation-format.md).
4. Chicago Manual of Style Online, “Notes and Bibliography: Sample Citations,” accessed August 13, 2026, https://www.chicagomanualofstyle.org/tools_citationguide/citation-guide-1.html.
5. Proposal format, “Evidence, Labels, and Strength,” [copied source](../proposal-format.md).
6. Proposal format, “Owner Choices and Conditional Follow-up,” [copied source](../proposal-format.md).
7. Proposal format, “Metadata and Readiness,” [copied source](../proposal-format.md).
8. Proposal format, “Sources and Citations.” This shortened note repeats the canonical source identity from notes 1, 2, 5, 6, and 7; it does not create a second source.

## Bibliography

Chicago Manual of Style Online. “Notes and Bibliography: Sample Citations.”
Accessed August 13, 2026.
https://www.chicagomanualofstyle.org/tools_citationguide/citation-guide-1.html.

Implementation format. “Implementation Format.” Internal copied source. [Implementation format](../implementation-format.md).

Proposal format. “Proposal Format.” Internal copied source. [Proposal format](../proposal-format.md).
