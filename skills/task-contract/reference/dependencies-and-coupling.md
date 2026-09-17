# Dependencies And Coupling

Dependencies and coupling answer different questions about a task boundary.

## Dependency Semantics

A dependency is a directed relationship that expresses order or artifact availability.

The dependent task identifies the predecessor and includes the predecessor artifact
in its `filesToRead` when that artifact is required for the dependent result.

A dependency does not make two concerns one task.

Separate tasks remain separate when one must follow the other.

Independence is tested with predecessor outputs fixed and available. If a consumer
can be retried, rejected, completed, or verified without repeating its predecessor,
the two results remain separate even though the consumer cannot start first.

Dependency edges do not authorize a consumer to infer missing work, alter a result,
or load unrelated context.

## Coupling Evidence

Multiple apparent results belong in one task only when all of these conditions hold:

- the evidence states one shared result;
- the evidence states one verification boundary; and
- the evidence states the separation risk: why separating execution, review, retry,
  or verification would be unsafe, misleading, or impossible.

Where `couplingRationale` records retained coupling, it records all three facts.
This semantic requirement does not alter schemas or prescribe a runtime validator.

Necessary work is not automatically coupled. Investigation that establishes a
finding or decision for later use is a predecessor. Investigation that only helps
produce an already-defined result may remain an internal step.

Dependencies, shared files, topics, releases, destinations, skills, ordering, final
documents, and lifecycle labels are insufficient coupling evidence and are not
coupling rationale.

## Boundary Review

If a concern can be independently assigned, rejected, retried, completed, or
verified, the dependency or shared destination does not justify merging it.

If separation would make the one result or its verification boundary unsafe,
misleading, or impossible, the rationale preserves the shared result, verification
boundary, and separation risk for review.

Absent, ambiguous, or contradictory evidence does not support retained coupling.
The boundary remains unresolved; a dependency can still express order between the
separate concerns.
