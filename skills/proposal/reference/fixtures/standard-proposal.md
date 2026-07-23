---
title: "Adopt proportional proposal navigation"
slug: "adopt-proportional-proposal-navigation"
created: "0"
created-at: "1970-01-01T00:00:00Z"
status: draft
decision-owner: "responsible engineer"
source-documents:
  - "../proposal-format.md"
---

# Adopt proportional proposal navigation

## Summary

Use a table of contents only when proposal complexity makes navigation useful.
This preserves easy scanning for short documents while helping readers navigate
expanded decisions ([format rules](../proposal-format.md)).

## Problem and context

An unconditional table of contents repeats navigation and source links in short
proposals, but a complex document benefits from direct section links
([format rules](../proposal-format.md)).

## Scope

- In scope: proposal table-of-contents generation and source navigation
  ([format rules](../proposal-format.md)).
- Out of scope: changing source preservation or implementation-detail boundaries
  ([format rules](../proposal-format.md)).

## Options and recommendation

- Always include a table of contents: consistent, but noisy for short proposals
  ([format rules](../proposal-format.md)).
- Never include one: brief output, but difficult to navigate when expanded
  ([format rules](../proposal-format.md)).
- Include it when complexity warrants it: recommended because it is proportional
  to the reader's navigation need ([format rules](../proposal-format.md)). See the
  [implementation overview](./implementation-overview.md).

## Requirements

- Short proposals omit the table of contents
  ([format rules](../proposal-format.md)).
- Complex proposals link sections, the implementation overview, and supporting
  sources without repeating individual source links
  ([format rules](../proposal-format.md)).

## Acceptance criteria

- A short fixture contains no table of contents
  ([format rules](../proposal-format.md)).
- A complex fixture contains one table of contents and one source index
  ([format rules](../proposal-format.md)).
- The implementation overview names concrete changes without duplicating the
  proposal decision ([implementation rules](../implementation-format.md)).

## Decision record

- **Decision:** Make table-of-contents generation conditional on useful
  navigation ([format rules](../proposal-format.md)).
- **Recorded objection:** Assumption: A universal table is easier to generate;
  rejected because it harms short-document readability.
- **Evidence Gap:** The exact complexity threshold is intentionally judgmental;
  authors must explain unusual navigation choices.

## Supporting sources

- [Proposal format](../proposal-format.md)
