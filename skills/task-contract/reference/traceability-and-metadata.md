# Traceability And Metadata

Traceability connects a task's stated result to the source and proposal material
that justifies it.

## Source Traceability

Source-derived requirements remain represented in `context` and point to the relevant
source paths in `filesToRead`.

The read set includes a predecessor artifact when a dependency supplies material
input to the task.

Source traceability identifies evidence; it does not turn every source concern into
one task.

## Proposal Traceability

Proposal-derived scope, constraints, decisions, and verification criteria remain
recognizable in task context.

Proposal section references and supporting source paths preserve the route from
the task result back to the decision record.

An implementation detail or verification criterion does not become a generic workflow
stage merely because it appears in a proposal.

Unsupported claims remain distinct from sourced requirements, assumptions, evidence
gaps, and open decisions.

## Authoring Metadata

- **`purposeOutputAlignment`** records whether the purpose and expected output align
  and states the evidence for that assessment.
- **`verificationCoverage`** records observable checks and their stated coverage;
  it is evidence about the result rather than a replacement for verification.
- **`dependencies`** records directed predecessors and, when present, the reason
  for the edge.
- **`couplingRationale`** records why one shared result has one verification boundary
  despite multiple concerns or files; when it records retained coupling, it states
  the shared result, verification boundary, and separation risk.
- **`antiPatternSignals`** records compound-task signals considered during
  authoring; a signal is not proof of independence by itself.
- **`taskId`** preserves stable identity when the authoring and packet contract
  expose it.

Metadata records the author's boundary reasoning.

Metadata does not prove conceptual atomicity, grant authority, or replace review
of the purpose, result, verification, dependencies, and coupling evidence together.

## Result Traceability

Every smaller result maps to one task, a predecessor handoff, or an explicit
exclusion. Every task maps back to the requested outcome or a necessary intermediate
result. This exposes missing work, duplicate work, and compound tasks before
assignment.

For retained coupling, traceability identifies the one shared result, one
verification boundary, and separation risk. Dependencies, shared files, skills,
ordering, final documents, and lifecycle labels can provide context, but do not
prove coupling.

This is semantic guidance, not a packet field or runtime-validation requirement.

## Structural Boundary

The task schemas remain the structural source for field types, requiredness, patterns,
and allowed properties.

This reference defines the meaning of the metadata without reproducing those runtime
interfaces.
