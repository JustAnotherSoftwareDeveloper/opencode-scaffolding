# Dependencies And Coupling

Dependencies and coupling answer different questions about a task boundary.

## Dependency Semantics

A dependency is a directed relationship that expresses order or artifact availability.

The dependent task identifies the predecessor and includes the predecessor artifact
in its `filesToRead` when that artifact is required for the dependent result.

A dependency does not make two concerns one task.

Separate tasks remain separate when one must follow the other.

Dependency edges do not authorize a consumer to infer missing work, alter a result,
or load unrelated context.

## Coupling Evidence

Retained coupling is one outcome-linked atomicity disposition. Multiple concerns
belong together under that disposition only when all of these conditions hold:

- the evidence states one shared result;
- the evidence states one verification boundary; and
- the evidence states the separation risk: why separating execution, review, retry,
  or verification would be unsafe, misleading, or impossible.

Where `couplingRationale` records retained coupling, it records all three facts. The
semantic requirement does not add a field, change a schema, or prescribe a runtime
validator.

Dependencies, shared files, topics, releases, destinations, skills, ordering, final
documents, and lifecycle labels are insufficient coupling evidence and are not
coupling rationale.

## Boundary Review

If a concern can be independently assigned, rejected, retried, completed, or verified,
the dependency or shared destination does not justify merging it.

If separation would make the one result or its verification boundary unsafe,
misleading, or impossible, the rationale preserves the shared result, verification
boundary, and separation risk for review.

Absent, ambiguous, or contradictory evidence does not support retained coupling; the
boundary remains unresolved rather than atomicity-approved. A dependency can still
express order while the concerns remain separate.
