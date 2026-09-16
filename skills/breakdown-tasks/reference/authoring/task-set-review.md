# Task-Set Review And Rework Protocol

Use this human review after every retained boundary has a draft task record and
has passed the [packet drafting checklist](packet-drafting-checklist.md). It is
the final authoring check in decomposition-method pass 8, before the separate
skill-assignment and publication procedures. It records review evidence; it does
not add packet fields, change schemas or structural validation, assign skills, or
prove conceptual atomicity.

Structural validation can establish structural conformance only. Review task
identity, atomicity, result alignment, dependencies, coupling, traceability, and
metadata using the named references exposed by the loaded `task-contract`
documentation skill.

## Review Record

Create one set-review record for the complete current draft. Identify the normalized
request, concern inventory, boundary-decision log, boundary mapping, draft-task
records, and dependency decisions reviewed. For every check below, record **pass**
or **fail**, the evidence, and—on failure—the named rework route. The record is final
publication-review evidence: preserve it with the draft and published packet without
adding a packet field or selecting its storage representation. Do not leave a signal,
candidate result, concern, or exception without a disposition.

## Set-Review Checklist

1. **Coverage and intentional exclusion.** Every concern in the normalized request
   and inventory maps once to a retained draft task, a required predecessor
   relationship, or an explicit exclusion with its basis. Confirm that each requested
   result and constraint has coverage, and that an exclusion is intentional rather
   than unresolved work.
2. **No duplicate or synthesis-only merges.** No two draft tasks claim the same
   independently reviewable result. A final document, package, release, or synthesis
   does not merge independently reviewable analysis, decisions, changes, or
   deliverables unless the shared coupling evidence supports one result and one
   verification boundary.
3. **One completion claim per task.** Each draft has one inspectable purpose and
   expected output, one honest completion claim, and verification evidence that
   addresses that result. A broad phase, list of actions, or separately reviewable
   verification artifact is not concealed as one completion claim.
4. **Usable interfaces.** Every task has the material request context, source paths,
   constraints, exclusions, and predecessor artifacts needed to perform its result.
   For each dependency, identify the predecessor, supplied artifact, consumer use,
   and readiness condition; ensure the consumer reads the required artifact.
5. **Order without false edges.** Each dependency represents a real directed
   availability or ordering need and does not combine concerns. A shared source,
   file, topic, destination, constraint, skill, workflow phase, or topical order
   is a shared input, not a dependency edge, unless a predecessor must supply
   a material item for the consumer.
6. **Outcome-linked disposition and signal disposition.** Every candidate result has
   exactly one visible disposition—split, dependency, integral evidence, intentional
   exclusion, or retained coupling—linked to its result, boundary, and source trace.
   Every anti-pattern or compound signal has a visible split
   or retained-coupling disposition with evidence. Retention must establish one
   shared result, one verification boundary, and why separation is unsafe,
   misleading, or impossible. Signals and metadata prompt review; they are not
   proof of conceptual atomicity, dependence, or coupling. Missing, ambiguous, or
   contradictory candidate-result evidence identifies an unresolved boundary: record
   its candidate-result ID, fail this check, and do not report the structurally valid
   packet as atomicity-assessed.

Pass only when every applicable check passes and every candidate result, inventory
concern, and signal has a documented, inspectable disposition. Preserve the reviewed
records and rationale so a later reviewer can trace each publication decision. A
structural validator can establish schema conformance but cannot turn this semantic
failure into atomicity assessment.

## Failure Routes And Rerun

Return failed work to the earliest decomposition-method pass that can correct its
cause. Preserve the failed record and its evidence; do not repair a failure by
rewriting only packet wording or by assigning a skill.

- **Missing concern, requested result, clear scope, or supported exclusion:** return
  to pass 1 **Normalize the request**, then pass 2 **Inventory concerns**; rerun
  passes 3–8.
- **Uncovered, duplicated, or concealed concern:** return to pass 2 **Inventory
  concerns**; rerun passes 3–8.
- **Multiple, vague, or unobservable result or completion claim:** return to
  pass 3 **State candidate results**; rerun passes 4–8.
- **Unsupported compound or synthesis-only merge:** return to pass 4 **Propose
  boundaries**; rerun passes 5–8.
- **Unsupported coupling, missing dependency interface, false shared-input edge,
  or invalid order:** return to pass 5 **Decide independence, order, and coupling**;
  rerun passes 6–8.
- **Missing task context, inputs, traceability, exclusions, completion evidence,
  or metadata disposition:** return to pass 6 **Draft task records**; rerun
  passes 7–8.
- **Invalid concern-to-task mapping after a boundary or relationship change:** return
  to pass 7 **Review boundary mappings**; rerun pass 8.
- **Absent, ambiguous, or contradictory candidate-result disposition evidence:** name
  the unresolved boundary and return to pass 3 **State candidate results**, pass 4
  **Propose boundaries**, or pass 5 **Decide independence, order, and coupling**, as
  applicable; rerun passes 6–8.

Any boundary change—including a split, merge rejection, coupling revision, or
dependency change—requires rerunning the affected later passes, the boundary-mapping
review, and this complete task-set review. Do not enter skill assignment or
publication until the rerun passes. This human aid complements, but does not replace,
the later structural-validation procedure.
