# Workflow Document Semantics

## Purpose

Define the meaning of a workflow document supplied as passive planning context and
where its authority ends.

## Applicability

Applies to skill-family planning, skill creation or review context, migration context,
and validation or release descriptions when supplied as passive references.

## Non-Goals

This document does not prescribe executable steps, invoke tools, make writes,
delegate work, produce an operation output, or establish completion.

## Authority Source

The authority is the local [dependency direction and non-transitivity](dependency-direction-and-non-transitivity.md)
and [class boundary rules](class-boundary-rules.md), interpreted within this passive scope.

## Scope

A workflow document may describe purpose, trigger, descriptive sequence, artifacts,
validation context, prerequisites, and notes. Its descriptive sequence is not an
executable procedure. The consuming operation owns imperative steps, tools, writes,
delegation, output, and completion validation. Passive workflow context cannot add
authority, cause a transitive load, or count as completion evidence.

## Evidence Status

The passive artifact contract is approved. A workflow document's presence as context
does not establish that its consuming operation or the workflow it describes has been
completed.

## Shared Passive-Contract Verification

This concern is coupled to the indexed scope and contains reference context only.
It grants no execution authority, implicit loading, tool use, file change, delegation,
or completion authority.
