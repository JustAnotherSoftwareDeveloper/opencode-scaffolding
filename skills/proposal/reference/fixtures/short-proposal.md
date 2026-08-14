---
title: "Adopt sentence-case proposal headings"
slug: "adopt-sentence-case-proposal-headings"
created: "0"
created-at: "1970-01-01T00:00:00Z"
status: draft
readiness: review-ready
decision-owner: "responsible engineer"
source-documents:
  - "../proposal-format.md"
---

# Adopt sentence-case proposal headings

## Summary

**Decision:** Use sentence-case headings in generated proposals. The expected
outcome is clearer plain-text scanning without changing decision content; the
trade-off is that familiar title-case styling is not retained. Evidence: the
format defines sentence-case headings and proportional structures as the
readability contract ([Proposal format](../proposal-format.md)).

## Problem and rationale

Title-case compound headings add visual noise in raw Markdown without adding
decision information. Evidence: headings should be descriptive, sentence-case,
and deliberate ([Proposal format](../proposal-format.md)).

## Scope

- **Goal:** Make generated proposal headings sentence-case.
- **Decision drivers:** plain-text scanability and preserved information hierarchy
  ([Proposal format](../proposal-format.md)).
- **Constraints:** Keep the nine canonical sections independently findable; omit
  decorative syntax and unsupported optional structure ([Proposal format](../proposal-format.md)).
- **Out of scope:** Other skill formats without dependency evidence.

## Criteria

- **Scanability:** Headings should be descriptive, sentence-case, and deliberate
  ([Proposal format](../proposal-format.md)).
- **Information hierarchy:** The heading structure should preserve decision meaning
  without decorative syntax ([Proposal format](../proposal-format.md)).

## Alternatives and trade-offs

- **Keep title case:** Rejected because it retains the scanability problem
  ([Proposal format](../proposal-format.md)).

## Selected direction

- **Selected direction:** Use sentence case because it preserves hierarchy with
  less visual noise ([Proposal format](../proposal-format.md)).
- **Decision:** Use sentence case for generated proposal headings
  ([Proposal format](../proposal-format.md)).

## Design constraints

- Proposal headings use sentence case and retain the canonical section meaning
  ([Proposal format](../proposal-format.md)).

## Open owner choices

No unresolved owner choice remains for this fixture.

## Acceptance criteria

- The short proposal has nine answer-first sections in canonical order, uses no
  placeholders or table of contents, and gives each material claim a descriptive
  source link or evidence label ([Proposal format](../proposal-format.md)).

- **Assumption:** The existing proposal source is sufficient to judge heading
  readability; no additional comparison is required.
- **Evidence Gap:** No measured scan-time comparison is available; this does not
  block review of the format decision.

## Supporting sources

- [Proposal format](../proposal-format.md). “Proposal format.” Internal reference
  document.
