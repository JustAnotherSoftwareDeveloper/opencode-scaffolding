---
title: "Adopt proportional proposal navigation implementation overview"
proposal: "standard-proposal.md"
slug: "adopt-proportional-proposal-navigation"
created: "0"
status: draft
---

# Adopt proportional proposal navigation implementation overview

Implement the [recommended conditional navigation](./standard-proposal.md#options-and-recommendation)
while retaining source and evidence traceability.

## Proposal skill contract

### `skills/proposal/SKILL.md` — Generate conditional navigation

- **Change:** Require a table of contents only when proposal complexity makes it useful
  ([proposal decision](./standard-proposal.md#options-and-recommendation)).
- **Reason:** Keep short proposals easy to scan in raw Markdown
  ([format rules](../proposal-format.md)).

### `skills/proposal/SKILL.md` — Generate one source index

- **Change:** List copied sources once under supporting sources instead of in navigation and references
  ([proposal requirements](./standard-proposal.md#requirements)).
- **Reason:** Repeated source links add visual noise without adding evidence
  ([format rules](../proposal-format.md)).

## Proposal templates

### `skills/proposal/templates/PROPOSAL.md` — Use semantic-core headings

- **Change:** Replace decorative boxes with sentence-case headings and ordinary lists
  ([format rules](../proposal-format.md)).
- **Reason:** Separate document structure from authoring guidance
  ([format rules](../proposal-format.md)).

## Validation

### Proposal fixtures — Check proportional navigation

- **Change:** Verify short fixtures omit navigation and complex fixtures use one
  non-duplicative table of contents
  ([proposal acceptance criteria](./standard-proposal.md#acceptance-criteria)).
