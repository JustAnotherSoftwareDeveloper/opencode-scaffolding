# Progressive Disclosure And Conformance Evidence

Keep `SKILL.md` as a compact entry point. Use it to identify the audience, outcome,
selection profile, procedure when the class requires one, and focused references.
Move detailed rules, examples, fixtures, and maintenance procedures to references.
Link every moved detail with a repository-relative Markdown link.

## Deterministic Policy

The following checks are conformance policy. They are observable checks, not claims
that the metadata validators currently implement them. A checker reports the file,
1-based source line, rule ID, and a short diagnostic. A pass means no diagnostic for
that rule. A policy exception must name the rule, reason, reviewer, and expiry or
permanent disposition; it is not a silent pass.

| Rule | Deterministic condition | Diagnostic evidence |
|---|---|---|
| `H1-001` one H1 | The file contains exactly one ATX level-one heading (`# `). Setext H1 headings also count. | Report every H1 line when the count is not one. |
| `HEAD-001` headings | Headings use ATX syntax, levels do not jump by more than one, and headings other than the H1 use Title Case. A heading must not restate the skill name. | Report the offending heading line and the observed level/text. |
| `TABLE-001` no tables | No Markdown table separator row is present. This policy applies to prose and examples; use bullets instead. | Report the separator line and the nearest table header line when available. |
| `PLACE-001` placeholders | No unresolved template markers remain: `TODO`, `TBD`, `FIXME`, `<...>`, `${...}`, `{{...}}`, or bracketed instructional placeholders such as `[insert ...]`. | Report the exact token and line. Code examples may suppress a token only with an explicit fixture annotation. |
| `STEP-001` numbered steps | A procedure is an ordered list whose markers start at 1 and increase by one. Only a class contract that requires a procedure is checked for a procedure; passive documentation is not forced to have one. | Report the first malformed marker, missing start, or gap with its line. |
| `STEP-002` duplicate numbering | Sibling ordered-list items use unique consecutive numbers. Repeated `2.` markers are an error even when Markdown renders them acceptably. | Report both the repeated marker and its preceding sibling context. |
| `LINK-001` required links | A compact index links each referenced detail file. Each relative target resolves from the source file, stays inside the repository, and has non-empty link text. | Report source line, target, and resolution failure; report an unlinked detail section by heading. |
| `DISC-001` disclosure budget | Entry-point body budgets are class-aware: `operation`/`delegated` ≤ 120 nonblank lines, `inline` ≤ 100, `planning`/`documentation` ≤ 80. Frontmatter, the H1, and link-only reference index lines are excluded. | Report counted lines, class, limit, and the first line beyond the limit. |
| `DISC-002` duplication | A reference must not repeat a contiguous prose block of 3 or more normalized sentences from its entry point. Normalize whitespace and Markdown punctuation before comparison. | Report both source ranges and the normalized duplicate excerpt. |

These thresholds are authoring policy, not schema facts. A reviewer may approve a
documented exception when the larger entry point is itself the required index; the
exception must still preserve links and avoid duplicated canonical rules.

## Source-Oriented Fixtures

Fixtures are small inputs used by a checker or a manual dry run. Diagnostics must
point to source lines rather than only returning a Boolean.

### Compact Index That Passes

```markdown
# Example Authoring Guide

## Purpose

Use this guide to author one profile.

## References

- [Style rules](reference/authoring-style.md)
- [Trigger guidance](reference/trigger-evaluation.md)

## Validation

1. Read the applicable reference.
2. Review the profile against the reference.
3. Record any exception.
```

Expected disposition: `H1-001`, `HEAD-001`, `TABLE-001`, `PLACE-001`, `STEP-001`,
`STEP-002`, `LINK-001`, `DISC-001`, and `DISC-002` pass when both links resolve.

### Defect Fixture And Expected Diagnostics

```markdown
# Bad Index
# Second H1

## details

| Rule | Result |
|---|---|
| one | two |

TODO: add the link to [insert reference].

1. First step.
2. Second step.
2. Duplicate step.
```

Expected diagnostics include `H1-001` on lines 1 and 2, `HEAD-001` on line 4,
`TABLE-001` on line 7, `PLACE-001` on line 11, and `STEP-002` on the repeated
marker line. If the procedure is required, `STEP-001` also fails because numbering
is not strictly consecutive. A missing or unresolved reference link produces
`LINK-001` at its source heading or link line.

### Disclosure And Duplication Fixture

Use a generated or checked-in variant with 81 nonblank body lines for a
`documentation` entry point and repeat three normalized sentences from its linked
reference. Expected disposition: `DISC-001` reports the count and limit, and
`DISC-002` reports both duplicate ranges. A compact index with the same material
represented only by a relative link passes both rules.

## Human Review Boundary

Deterministic checks do not establish meaning. A human reviewer must disposition:

- imperative, active prose and whether each sentence makes one decision;
- whether examples are short, contrastive, and truthful;
- semantic discrimination between owned, neighboring, paraphrased, and unrelated
  requests;
- whether a heading or reference boundary improves progressive disclosure rather
  than merely satisfying a line count; and
- whether a procedure is genuinely executable for its class rather than merely
  numbered.

Record these as `PASS`, `FAIL`, or `MANUAL` with source links. Do not infer selector
quality, scoring, or trigger-manifest coverage from structural conformance. No
trigger manifests are required by this policy.

## Evidence Checklist

For each changed authoring document, retain the checker output or manual review note
covering every rule above. The evidence is complete only when one of these is true
for each rule: a source-oriented diagnostic was emitted, the rule passed against the
source, or a named human disposition explains why it is not applicable. Run the
checks again after edits and compare neighboring headings, links, and duplicate
ranges; do not claim semantic automation from these results.
