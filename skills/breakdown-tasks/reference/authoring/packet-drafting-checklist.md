# Packet Drafting And Traceability Checklist

Use this checklist after the decomposition method has stabilized a retained boundary
and before skill assignment. It translates the human concern and boundary
records into the existing packet narrative and metadata. It is authoring guidance
only: it does not add, remove, reinterpret, or change the requiredness of packet
fields. It does not change publication or assignment behavior. The loaded
`task-contract` documentation skill's named **Traceability and metadata** reference
defines metadata meaning; the task schema remains authoritative for the packet
interface.

## Per-Retained-Boundary Checklist

For each retained boundary, complete every applicable item before adding `skills`.

1. **Map the packet to its concern record.** Identify the source concern row or
   rows, its inventory trace, selected disposition, and boundary-decision evidence.
   A standalone or prerequisite-linked concern maps to one packet. A retained-coupled
   packet identifies every coupled concern row and the supported shared result and
   verification boundary. An excluded concern maps to its documented exclusion,
   not to a packet. Return an unmapped, duplicated, opaque, or compound packet
   to the relevant earlier decomposition-method pass. Do not conceal the problem
   in packet wording or metadata.
2. **State one result in the packet narrative.** Populate existing `purpose` and
   `expectedOutput` with the retained boundary's one inspectable result. Purpose,
   expected output, execution instructions, and verification must support one
   observable completion claim from the concern record. Record the alignment
   assessment and its evidence in existing `purposeOutputAlignment`; do not use
   a broad phase, a collection of unrelated actions, or a final destination as the
   claimed result.
3. **Carry completion evidence forward.** Translate the concern record's result
   evidence and completion claim into concrete execution-instruction verification
   and the existing `verification` entries where present. Record observable result
   coverage in existing `verificationCoverage`. These records document coverage;
   they do not replace a review of whether the result is actually complete.
4. **Preserve sources and material inputs.** Put the request subset, constraints,
   proposal decision references, source paths, and boundary rationale needed by
   the worker in existing `context`. Put the material source paths in existing
   `filesToRead`. When a predecessor supplies a needed artifact, include that
   artifact in the consumer's read set and retain its decision route in context.
   Do not turn a shared input into a dependency or use context as a substitute
   for a required read path.
5. **Preserve scope and exclusions.** State material exclusions and their basis
   in existing context when they delimit the retained result. Keep excluded concern
   rows and their basis in the authoring records and boundary mapping. Do not
   represent excluded work as an implied packet obligation or expected output.
6. **Record a supported dependency rationale.** For a prerequisite-linked
   boundary, use existing `dependencies` to retain the directed predecessor and
   reason.
   Ensure the authoring record identifies the predecessor, supplied artifact,
   consumer use, and readiness condition. A dependency preserves sequence or
   availability; it does not merge results or repair a compound packet.
7. **Record compound-signal disposition.** Carry each reviewed compound-task signal
   and its split or retained disposition into existing `antiPatternSignals`. A signal
   is review evidence, not proof that work is atomic, dependent, or coupled. If
   the signal reveals independently reviewable work, return it for splitting
   rather than drafting a compound packet.
8. **Record coupling only when justified.** Populate existing `couplingRationale`
   only for a retained-coupled boundary supported by one shared result, one shared
   verification boundary, and an explanation of why separation would be unsafe,
   misleading, or impossible. Identify the coupled concern rows. Shared files, topics,
   sources, destinations, skills, predecessors, or dependencies alone are not a
   coupling rationale; return unsupported coupling to the earlier boundary or
   relationship decision pass.
9. **Keep the boundary stable through assignment.** Do not add `skills` while this
   checklist is resolving boundary, dependency, coupling, traceability, or completion
   issues. After the packet and concern mapping pass review, perform skill assignment
   using the existing procedure. Skills never repair a boundary: do not merge, split,
   or otherwise reshape a packet to fit an available skill.

## Final Packet Review

Before the set review and skill assignment, confirm that every packet has a visible
concern-record mapping, exactly one observable completion claim, aligned purpose
and expected output, material inputs and exclusions, and applicable existing
metadata for alignment, verification coverage, dependencies, and anti-pattern
signals, plus justified coupling. Return any failed item to the earliest pass
that can correct the underlying concern, boundary, or relationship decision.
This checklist does not change packet fields or the existing publication or
assignment procedure.
