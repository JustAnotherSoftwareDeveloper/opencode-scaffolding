---
title: "Migrate proposal workspaces to proportional formatting"
slug: "migrate-proposal-workspaces-to-proportional-formatting"
created: "0"
created-at: "1970-01-01T00:00:00Z"
status: draft
decision-owner: "responsible engineer"
source-documents:
  - "../proposal-format.md"
  - "../implementation-format.md"
---

# Migrate proposal workspaces to proportional formatting

## Table of contents

- [Summary](#summary)
- [Problem and context](#problem-and-context)
- [Scope](#scope)
- [Options and recommendation](#options-and-recommendation)
- [Migration considerations](#migration-considerations)
- [Risks and mitigations](#risks-and-mitigations)
- [Requirements](#requirements)
- [Acceptance criteria](#acceptance-criteria)
- [Decision record](#decision-record)
- [Implementation overview](./implementation-overview.md)
- [Supporting sources](#supporting-sources)

## Summary

Migrate the proposal skill to a compact semantic core with optional expansion.
The change removes decorative structure while retaining evidence and decision
traceability ([format rules](../proposal-format.md)).

## Problem and context

The former format couples semantic completeness to fixed presentation rules,
which makes raw Markdown noisy and does not control proposal size
([format rules](../proposal-format.md)).

## Scope

- In scope: proposal templates, validation contract, references, and fixtures
  ([format rules](../proposal-format.md)).
- Out of scope: changing planning skills without evidence of a dependency
  ([format rules](../proposal-format.md)).

## Options and recommendation

- Preserve the old layout: retain presentation noise
  ([format rules](../proposal-format.md)).
- Relax only sentence limits: reduce one constraint but retain duplicate
  navigation and boxes ([format rules](../proposal-format.md)).
- Adopt a compact semantic core: recommended because it keeps decision content
  while allowing proportional presentation ([format rules](../proposal-format.md)).
  See the [implementation overview](./implementation-overview.md).

## Migration considerations

Assumption: Existing proposal workspaces remain historical artifacts and require
no bulk rewrite. Consumers of old heading anchors must be identified before a
compatibility migration is needed.

## Risks and mitigations

### Unknown anchor consumers

Evidence Gap: External automation that references former headings is unknown.
Search repository consumers before release and retain semantic names where
useful.

### Under-specified short proposals

Removing fixed sections can omit important decisions. Mitigate this by
requiring the semantic core regardless of proposal size ([format rules](../proposal-format.md)).

## Requirements

- Generated proposals use sentence-case headings and ordinary lists
  ([format rules](../proposal-format.md)).
- A table of contents appears only when complexity makes it useful
  ([format rules](../proposal-format.md)).
- Each copied source appears once in supporting sources
  ([format rules](../proposal-format.md)).

## Acceptance criteria

- Short, standard, and complex fixtures demonstrate the same evidence rules
  ([format rules](../proposal-format.md)).
- The complex fixture uses a table of contents without repeating individual
  source links ([format rules](../proposal-format.md)).
- The linked implementation overview names concrete artifact changes
  ([implementation rules](../implementation-format.md)).

## Decision record

- **Decision:** Use proportional formatting for new proposal workspaces
  ([format rules](../proposal-format.md)).
- **Decision:** Preserve source copying and relative evidence links
  ([format rules](../proposal-format.md)).
- **Evidence Gap:** External consumers of former anchors are not yet known.
- **Recorded objection:** Assumption: A fixed layout is simpler to validate;
  rejected because it confuses presentation consistency with decision
  completeness.

## Supporting sources

- [Proposal format](../proposal-format.md)
- [Implementation format](../implementation-format.md)
