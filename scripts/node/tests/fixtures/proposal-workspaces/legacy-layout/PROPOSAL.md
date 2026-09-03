---
title: Legacy Layout Proposal
slug: legacy-layout
created: 2025-04-01
created-at: 2025-04-01T07:00:00Z
status: draft
readiness: not-ready
decision-owner: tester
source-documents:
  - 01-requirements.md
---

## Table of Contents

- [Recommendation](#recommendation)
- [Technical Rationale](#technical-rationale)
- [Questions](#questions)
- [Options Considered](#options-considered)
- [Implementation Details](#implementation-details)
- [Verification Criteria](#verification-criteria)
- [Sources](#sources)

## Recommendation

Support legacy numbered files alongside PROPOSAL.md.

## Technical Rationale

Migration may leave old numbered files in the workspace.

## Questions

Should we warn about legacy files?

## Options Considered

Silently accept legacy files for now.

## Implementation Details

No special handling needed.

## Verification Criteria

- Validator does not reject legacy layout

## Sources

- [Requirements](01-requirements.md)