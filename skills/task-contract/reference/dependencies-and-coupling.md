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

Multiple concerns belong together only when all of these conditions hold:

- they produce one shared result;
- they have one verification boundary; and
- separating execution, review, retry, or verification would be unsafe,
  misleading, or impossible.

`couplingRationale` records that evidence in terms of the shared result and its
verification boundary.

Shared files, topics, releases, destinations, skills, dependencies, or a final
document are insufficient coupling evidence by themselves.

## Boundary Review

If a concern can be independently assigned, rejected, retried, completed, or verified,
the dependency or shared destination does not justify merging it.

If separation would make the one result or its verification boundary unsafe,
misleading, or impossible, the rationale preserves that coupling fact for review.
