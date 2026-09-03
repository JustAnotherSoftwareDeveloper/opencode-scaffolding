---
title: "Adopt sentence-case proposal headings"
slug: "adopt-sentence-case-proposal-headings"
created: "0"
created-at: "1970-01-01T00:00:00Z"
status: draft
readiness: review-ready
decision-owner: "responsible engineer"
source-documents:
  - "other/heading-policy.md"
---

# Adopt sentence-case proposal headings

## Table of Contents

- [Recommendation](#recommendation)
- [Technical Rationale](#technical-rationale)
- [Questions](#questions)
- [Options Considered](#options-considered)
- [Implementation Details](#implementation-details)
- [Verification Criteria](#verification-criteria)
- [Sources](#sources)

## Recommendation

Generated proposal headings will use sentence case. The change affects the proposal
template only and preserves the existing Markdown heading hierarchy.

## Technical Rationale

Sentence case exposes the first meaningful words without adding title-style visual
noise. The source policy requires sentence-case headings and treats heading hierarchy,
not capitalization, as the structural invariant.

Assumption: Reviewers recognize the unchanged Markdown heading levels without title
capitalization.

## Questions

- Evidence Gap: None.
- Open Question: None.

## Options Considered

### Keep title case

- **Differentiator:** Existing capitalization remains unchanged.
- **Consequence:** Compound headings retain unnecessary visual emphasis.
- **Disposition:** Rejected because capitalization adds no structural information.

### Use sentence case

- **Differentiator:** Headings read like concise engineering labels.
- **Consequence:** Existing title capitalization changes while hierarchy remains stable.
- **Disposition:** Selected because it meets the policy with a bounded template edit.

## Implementation Details

### Proposal template — render sentence-case headings

- **Change:** Replace title-case generated headings with sentence-case labels.
- **Invariant:** Markdown heading levels and section order remain unchanged.
- **Compatibility and migration:** Existing proposals remain unchanged; only new or
  deliberately revised output uses the rule.
- **Failure behavior:** The Markdown check rejects malformed heading hierarchy.
- **Verification dependency:** Inspect generated headings and run Markdown lint.

## Verification Criteria

- A generated proposal uses sentence case for every section heading.
- The generated document retains the required H2 order and valid Markdown hierarchy.
- Historical proposal workspaces remain unchanged.

## Sources

- [Sentence-case heading policy](./other/heading-policy.md)
