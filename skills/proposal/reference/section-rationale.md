# Proposal section rationale

The one-document sequence gives reviewers one stable path from decision to evidence of
completion. Core sections remain explicit even when concise because recommendation,
rationale, uncertainty, alternatives, implementation, and verification answer different
engineering questions.

## Table of Contents

The table of contents exposes the technical scan path without requiring cross-file
navigation. It lists all H2 sections once in order and includes only major H3 workstreams.
It never links to itself.

## Recommendation

Review begins with the selected architecture or behavior, affected boundary, decisive
constraint, and material consequence. Putting the answer first lets informed readers
stop early and gives skeptical readers a clear claim to test against later evidence.

## Technical Rationale

Rationale explains why the recommendation follows from evidence, constraints, and
trade-offs. It owns decision drivers and assumptions without repeating the recommendation
or confusing option-evaluation criteria with completion tests.

## Questions

One heading keeps unresolved uncertainty visible without pretending that all uncertainty
belongs to an authority. `Evidence Gap:` identifies unavailable research evidence;
`Open Question:` identifies only a residual engineering decision after research;
`Assumption:` identifies an unverified dependency. Stable labels preserve planning and
audit traceability while the broader heading remains readable.

## Options Considered

Credible alternatives and rejection reasons demonstrate that the selected direction
survived comparison. Parallel presentation makes meaningful differences visible without
repeating rationale already established above.

## Implementation Details

Implementation remains explicit because a decision that cannot identify affected
components, interfaces, invariants, compatibility effects, and behavior changes is not
ready for reliable task planning. Keeping this detail in the same document avoids a
fragmented companion record. It remains a boundary description, not an execution runbook.

## Verification Criteria

Verification maps intended results to tests, inspections, metrics, observations, or
bounded human review. It remains distinct from criteria used to choose among options.
Structural checks prove deterministic conformance only; human review owns correctness,
researchability, prose quality, and comprehension.

## Sources

Sources closes the traceability path. Copied internal entries reconcile exactly with
frontmatter `source-documents`; external bibliography entries remain identifiable but
outside the copied-source manifest.

## Optional technical subsections

Add a subsection only when its concern changes the decision or review:

- **Interfaces and data flow:** contracts, schemas, state transitions, or boundaries.
- **Compatibility and migration:** preserved behavior, adapters, sequencing, or data
  conversion.
- **Security and privacy:** trust boundaries, permissions, exposure, or abuse cases.
- **Performance and scalability:** measured budgets, load behavior, or capacity risks.
- **Reliability and failure handling:** failure modes, recovery, retry, or degradation.
- **Rollout and rollback:** staged activation or reversal constraints.
- **Operational impact:** observability, support, or ongoing maintenance consequences.

Short proposals omit unsupported optional subsections. Complex proposals add depth
inside the same document rather than creating companion decision files. No fixed length
or section quota substitutes for decision-relevant content.

Readiness describes evidence and decision closure, not approval. This taxonomy applies
forward to new or deliberately revised documents and does not rewrite historical
`.proposals/` workspaces or create active legacy aliases.
