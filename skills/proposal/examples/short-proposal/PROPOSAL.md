---
title: "Adopt Title Case Proposal Headings"
slug: "adopt-title-case-proposal-headings"
created: "0"
created-at: "1970-01-01T00:00:00Z"
status: draft
readiness: review-ready
decision-owner: "responsible engineer"
source-documents:
  - "other/heading-policy.md"
---

# Adopt Title Case Proposal Headings

## Table of Contents

- [Recommendation](#recommendation)
- [Technical Rationale](#technical-rationale)
- [Questions](#questions)
- [Options Considered](#options-considered)
- [Implementation Details](#implementation-details)
- [Verification Criteria](#verification-criteria)
- [Sources](#sources)

## Recommendation

Generated proposal headings will use Title Case for non-core headings, including
optional or domain-specific H2s and H3s. The eight fixed core H2 labels and seven core
table-of-contents entries remain unchanged; only authored non-core headings change.

## Technical Rationale

Title Case distinguishes authored non-core headings while preserving the format's fixed
core labels, technical terminology, identifiers, and Markdown hierarchy. The linked
policy source specifies this boundary, and the existing core H2 and table-of-contents
text remain exact.

Assumption: Reviewers recognize the unchanged Markdown heading levels without title
capitalization.

## Questions

- Evidence Gap: None.
- Open Question: None.

## Options Considered

### Keep Sentence Case

- **Differentiator:** Generated non-core headings retain sentence-style capitalization.
- **Consequence:** Authored optional and domain-specific headings do not follow the
  selected heading policy.
- **Disposition:** Rejected because the linked policy specifies Title Case for non-core
  headings.

### Use Title Case

- **Differentiator:** Authored non-core headings follow the linked policy.
- **Consequence:** Existing sentence-case non-core headings change while the core labels,
  table-of-contents text, and hierarchy remain stable.
- **Disposition:** Selected because it meets the policy with a bounded template edit.

## Implementation Details

### Proposal Template — Render Title Case Headings

- **Change:** Use Title Case for generated non-core headings, including optional or
  domain-specific H2s and H3s.
- **Invariant:** The exact core H2 labels and table-of-contents text, Markdown heading
  levels, and section order remain unchanged.
- **Compatibility and migration:** Existing proposals remain unchanged; only new or
  deliberately revised output uses the rule.
- **Failure behavior:** The Markdown check rejects malformed heading hierarchy.
- **Verification dependency:** Inspect generated headings and run Markdown lint.

## Verification Criteria

- A generated proposal uses Title Case for every non-core heading.
- The generated document retains the exact core H2 labels and order, exact table-of-
  contents entries, and valid Markdown hierarchy.
- Historical proposal workspaces remain unchanged.

## Sources

- [Title Case Heading Policy](./other/heading-policy.md)
