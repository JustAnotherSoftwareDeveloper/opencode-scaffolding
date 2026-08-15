---
title: "Separate proposal decisions from implementation changes"
proposal: "standard-proposal/PROPOSAL.md"
slug: "separate-proposal-decisions-from-implementation-changes"
created: "0"
status: draft
---

# Separate proposal decisions from implementation changes

The proposal workflow produces a decision document and a separate implementation
overview. This example records only concrete changes to the proposal skill,
implementation template, and conformance example.

## Proposal skill contract

### `skills/proposal/SKILL.md` — Link the implementation overview from the recommendation

- **Change:** Keep `PROPOSAL.md` as the proposal index, keep decision prose in
  numbered section files, and link `10-implementation.md` from the index and selected
  direction.
- **Reason:** The workspace contract assigns the decision document and implementation
  overview separate responsibilities ([workspace contract](../reference/workspace-contract.md#canonical-artifacts)).

### `skills/proposal/SKILL.md` — Group changes by affected area

- **Change:** Require an H2 for each affected area and an H3 that names each concrete
  target and its modification.
- **Reason:** The implementation format makes affected targets and modifications
  directly reviewable ([implementation format](../reference/implementation-format.md#structure)).

## Proposal templates

### `skills/proposal/templates/10-implementation.md` — Render concrete target sections

- **Change:** Render the implementation title and summary, followed by affected-area
  sections with target-specific change bullets.
- **Reason:** The template structure matches the required H2/H3 implementation
  organization ([implementation template](../templates/10-implementation.md)).

## Example conformance checks

### `skills/proposal/examples/implementation-overview.md` — Demonstrate separated concrete changes

- **Change:** Show multiple concrete changes under the proposal skill contract and
  proposal templates areas, plus a distinct example-conformance area.
- **Reason:** The example coverage requires named targets, concrete modifications,
  multiple changes in one area, and a separate affected area
  ([example coverage](./README.md#example-coverage)).
