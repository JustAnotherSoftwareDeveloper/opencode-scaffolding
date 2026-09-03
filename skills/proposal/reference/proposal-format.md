# Proposal format

Author one metadata-bearing `PROPOSAL.md`. It is the decision, implementation,
verification, and source-traceability artifact. Do not split new proposals into
numbered decision files or separate implementation and source indexes.

## Core document order

Every proposal contains these H2 sections exactly once and in this order:

1. **Table of Contents** — a non-recursive navigation surface.
2. **Recommendation** — the selected architecture or behavior and affected boundary.
3. **Technical Rationale** — decisive evidence, constraints, and trade-offs.
4. **Questions** — unresolved research evidence and residual engineering decisions.
5. **Options Considered** — credible alternatives and rejection rationale.
6. **Implementation Details** — concrete affected components and behavior changes.
7. **Verification Criteria** — tests and observations demonstrating completion.
8. **Sources** — copied-source identity and bounded external bibliography.

A domain-specific H2 may appear between `Questions` and `Options Considered` when it
adds substantial decision-relevant design detail. Every H2 appears in the table of
contents. Include H3 entries only for major technical review workstreams; never list
the table of contents itself.

### Recommendation

State the selected architecture or behavior in the first two sentences. Name the
affected system boundary, decisive constraint, material compatibility consequence,
and principal trade-off without repeating the option history.

### Technical Rationale

Explain why the recommendation follows from evidence. Keep evaluation criteria here
or with option comparison: they judge a direction and are not completion evidence.
Identify assumptions, dependencies, invariants, and material objections.

### Questions

Use the stable labels below; do not introduce `Research Question:` or
`Decision Question:` aliases.

- `Assumption: <statement>` records an unverified decision dependency.
- `Evidence Gap: <missing evidence>` records research that inspection, analysis,
  testing, prototyping, or external research could not supply. State whether it blocks
  decision readiness.
- `Open Question: <question>` records only a residual engineering decision. Name the
  decision-maker, choices, and consequence of deferral.

Resolve researchable uncertainty before asking an owner to decide. Use `None.` when
no question of a type remains.

### Options Considered

Compare only credible alternatives. Give comparable options parallel differentiators,
consequences, trade-offs, evidence, and dispositions. A table is permitted when rows
and columns are genuinely comparable; otherwise use parallel bullets or prose.

### Implementation Details

Group changes by concrete component, interface, file, schema, or workflow. For each
change, state the target, behavior, preserved invariant, dependency, compatibility or
migration effect, failure behavior, and verification dependency when applicable.
Provide enough detail for task planning without commands, assignments, estimates, or
generic lifecycle/runbook steps. Follow [the implementation format](./implementation-format.md).

### Verification Criteria

Map every intended result to an observable test, inspection, metric, or human review.
Completion verification is distinct from criteria used to choose an option. Structural
lint cannot establish technical correctness, prose quality, question researchability,
or reader comprehension.

### Sources

List every copied source exactly once with a descriptive relative link whose path
matches one frontmatter `source-documents` entry. External bibliography entries may
also appear but are not copied-source manifest entries. Preserve available source
metadata and never fabricate missing authors, dates, publishers, or URLs.

## Metadata and readiness

`PROPOSAL.md` YAML frontmatter defines `title`, `slug`, `created`, `created-at`,
`status`, `readiness`, `decision-owner`, and `source-documents`. New workspaces start
with `status: draft`. Use only:

- `not-ready` — the decision path or evidence is not reviewable;
- `review-ready` — the path and evidence are reviewable and residual owner decisions
  are resolved; or
- `decision-ready` — blocking evidence gaps are resolved and the explicit decision
  record is ready for the decision authority.

Status, readiness, acceptance, and approval are independent facts. Neither
`review-ready` nor `decision-ready` means approval. Do not infer or manufacture a
lifecycle transition.

## Proportional engineering detail

- **Short:** keep the core sections compact and omit unsupported optional subsections.
- **Standard:** expose multiple affected areas, compatibility behavior, and test
  dependencies with descriptive subsections.
- **Complex:** add justified security, performance, reliability, data-flow, migration,
  rollback, operational, or failure-mode subsections inside the same document.

No word, sentence, bullet, table, or section-length quota applies. Add detail only when
it changes review, implementation, risk, or verification.

## Complete skeleton

```markdown
---
title: "<proposal title>"
slug: "<lowercase-kebab-case-slug>"
created: "<epoch-ms>"
created-at: "<ISO-8601 timestamp>"
status: draft
readiness: not-ready
decision-owner: "<responsible engineer>"
source-documents:
  - "analysis/<copied-source>.md"
---

# <Proposal title>

## Table of Contents

- [Recommendation](#recommendation)
- [Technical Rationale](#technical-rationale)
- [Questions](#questions)
- [Options Considered](#options-considered)
- [Implementation Details](#implementation-details)
- [Verification Criteria](#verification-criteria)
- [Sources](#sources)

## Recommendation
## Technical Rationale
## Questions
## Options Considered
## Implementation Details
## Verification Criteria
## Sources
```

The skeleton is authoring guidance. Published proposals contain substantive content,
no placeholders or authoring comments, and no legacy authored artifacts.
