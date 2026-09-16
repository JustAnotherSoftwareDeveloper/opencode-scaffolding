# Dependency And Coupling Decisions

Use this guide in decomposition method pass 5 to make relationship decisions
inspectable. It is human authoring instruction only: it does not define task,
dependency, coupling, atomicity, result, verification, or metadata semantics; own
fields or schemas; or add validation or runtime behavior. Consult the loaded
`task-contract` documentation skill's named **Dependencies and coupling**,
**Atomicity and alignment**, and **Traceability and metadata** references for those
definitions and requirements.

## Make A Relationship Decision

For each candidate pair of concerns, record the observed signal and choose the
first supported disposition below. Do not leave a compound signal undecided.

1. **Shared input — no edge.** When both concerns use the same source, constraint,
   file, topic, destination, skill, or other input but neither requires a result
   from the other, keep them independently reviewable. Record the shared input for
   traceability if material; do not infer an order or retain a compound boundary.
2. **Dependency interface — directed edge.** When a consumer requires an item that
   a predecessor must supply, keep the concerns separate and record the directed
   relationship. The record must name all four facts:
   - **Predecessor:** the task or result that supplies the item.
   - **Supplied item:** the specific artifact, decision, or other material input.
   - **Consumer use:** how the dependent result uses that item.
   - **Readiness condition:** what makes the item available and suitable for the
     consumer to begin or complete its work.

   Put a required predecessor artifact in the consumer's existing read set as the
   shared traceability contract requires. An edge represents order or availability;
   it does not merge the two concerns or authorize missing work.
3. **Coupling review — retain only with three facts.** Begin from separate concerns.
   Retain them in one boundary only when the authoring record states all three
   shared-contract facts: one shared result, one verification boundary, and why
   separation would be unsafe, misleading, or impossible. If a fact is absent or
   unpersuasive, split the concerns; add a dependency interface when an ordered
   supplied item is also required.

## Disposition Every Compound Signal

Treat each signal that suggests a compound task as a review prompt, not proof.
For every signal, record either **split** or **retained coupling** with its evidence.

- **Several questions, changes, operations, or deliverables:** split the separately
  answerable concerns. Retain only with all three coupling facts.
- **One final document, package, release, or destination:** split the independently
  reviewable contributions. A shared destination is not one shared result.
- **Shared file, topic, source, or constraint:** treat it as shared input, not an
  edge or coupling reason. Split unless all three coupling facts support retention.
- **Requested sequence, workflow phase, or topical order:** split and add an edge
  only when all four dependency-interface facts are present. Topical order by
  itself is explicitly not an edge.
- **A predecessor or dependency:** keep the concerns separate. Dependency alone
  cannot justify coupling; retain only with all three coupling facts.
- **Common skill or available skill:** do not shape the boundary around it. Split
  unless all three coupling facts support retention.
- **Several files or outputs:** split independently assignable, rejectable,
  retryable, completable, or verifiable work. Retain only when the three coupling
  facts establish one result and one verification boundary.

When retaining, identify the exact compound signal, the concerns considered, and
the evidence for each of the three facts. When splitting, identify the resulting
separate concerns and any required dependency interface. Revisit the decision after
each split because a new predecessor artifact or independent result may become
visible.

## Carry The Decision Into Existing Records

Carry the outcome into the operation's existing authoring and task metadata without
changing their meaning or adding fields. Record a supported directed relationship
in the existing dependency metadata, including its predecessor and reason; preserve
a material predecessor artifact in the existing read set. Record a supported
retained boundary in the existing coupling rationale with the shared result and
verification boundary, plus the separation risk. Record the reviewed compound
signal and its split or retain disposition in the existing anti-pattern evidence.
Keep purpose, expected output, and verification coverage aligned with the boundary.

These records preserve the decision for review; they do not make an unsupported
edge or coupling valid. Use the decomposition method's boundary mapping and set
review to confirm that every resulting concern, dependency, and retained boundary
remains accounted for.

## Negative Checks

Before finalizing, reject a coupling rationale based only on a shared file, topic,
source, destination, release, final document, skill, predecessor, or dependency.
Reject an edge based only on shared inputs, a shared destination, topical order,
or a desired workflow sequence. In either case, split independently reviewable
work and retain only the explicit, supported relationship decision.
