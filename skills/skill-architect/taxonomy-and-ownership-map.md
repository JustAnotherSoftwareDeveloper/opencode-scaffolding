# Taxonomy and Ownership Map

## Purpose

Define the approved five-class taxonomy and the ownership-map authority for the
skill-authoring family.

## Applicability

Applies to architecture context for `skill-architect`, `skill-factory`,
`skill-reviewer`, and the three passive documentation stores.

## Non-goals

This document does not select a skill, assign implementation work, perform a
migration, or authorize a procedure, tool, write, delegation, or completion result.

## Authority source

The authoritative source for this concern is the approved local architecture represented
by [class taxonomy](class-taxonomy.md), [class boundary rules](class-boundary-rules.md),
and the indexed six-concern scope. Supporting material is descriptive context only.

## Scope

The valid classes are exactly `operation`, `delegated`, `inline`, `planning`, and
`documentation`. `skill-architect` is the single passive planning authority;
`skill-factory` owns creation or update of one skill workspace; `skill-reviewer`
owns one evidence-linked conformance analysis; and `skill-authoring-guide`,
`skill-template-library`, and `skill-maintenance-reference` remain passive stores.
Migration is a workflow concern, not a standalone migration skill. Each canonical
rule has one owner; stale proposed inventory names are not approved substitutes.

## Evidence status

Approved target architecture, with repository-observed class facts recorded in the
architecture decision. Ownership-ledger completion and subsequent migration evidence
remain implementation gates.

## Shared passive-contract verification

This concern is coupled to the indexed scope and contains reference context only.
It grants no execution authority, implicit loading, tool use, file change, delegation,
or completion authority.
