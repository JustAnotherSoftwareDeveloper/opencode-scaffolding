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

Proposal-derived scope, constraints, decisions, and acceptance conditions remain
recognizable in task context.

Proposal section references and supporting source paths preserve the route from
the task result back to the decision record.

An implementation overview or acceptance condition does not become a generic workflow
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
  despite multiple concerns or files.
- **`antiPatternSignals`** records compound-task signals considered during
  authoring; a signal is not proof of independence by itself.
- **`taskId`** preserves stable identity when the authoring and packet contract
  expose it.

Metadata records the author's boundary reasoning.

Metadata does not prove conceptual atomicity, grant authority, or replace review
of the purpose, result, verification, dependencies, and coupling evidence together.

## Structural Boundary

The task schemas remain the structural source for field types, requiredness, patterns,
and allowed properties.

This reference defines the meaning of the metadata without reproducing those runtime
interfaces.
