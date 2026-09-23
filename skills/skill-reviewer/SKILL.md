---
name: skill-reviewer
description: "Use when assessing one existing skill workspace for evidence-linked conformance findings and a bounded disposition."
selection:
  role: owner
  tags:
    actions: [assess, review]
    inputs: [existing skill workspace, class contract, selection profile]
    outputs: [conformance analysis]
    topics: [skill conformance, validation evidence]
    constraints: [read-only review, one workspace]
  use_when:
    - a maintainer needs findings and a pass/fail recommendation for one existing skill
  not_for:
    - creating or editing a skill, migrating a family, choosing taxonomy, or replacing validators
class: operation
---

# Skill Reviewer

Assess one existing skill workspace against its applicable contracts and publish one
evidence-linked conformance analysis without changing the workspace.

## Normalize Input

Identify the existing skill path, intended class, applicable profile rules, templates,
style guidance, and maintenance checks. Load `skill-authoring-guide` as the canonical
prose-policy owner when semantic form selection and `TABLE-001` apply.

## Procedure

1. Identify the skill class and applicable contracts.
2. Inspect the complete skill workspace and referenced local resources.
3. Run available deterministic validation without changing the skill.
4. Compare observed content with the applicable contracts and templates. Check that
   bullets represent peer rules, ordered lists represent order-dependent procedures,
   paragraphs carry connected reasoning, definition lists map terms to definitions,
   subsection headings separate reviewable concerns, and filled content contains no
   Markdown tables.
5. Separate deterministic conformance evidence from human clarity judgment. Do not
   treat lint as proof of readability, comprehension, navigation quality, or task
   success.
6. Publish one analysis with findings, evidence links, disposition, and unavailable or
   inapplicable checks.

## Self-Validation

- The review covers one existing workspace and does not modify it.
- Every finding has a source path, evidence, severity, and bounded recommendation.
- Applicable findings distinguish deterministic prose-policy conformance from human
  clarity judgment.
- The disposition is `PASS`, `PASS WITH FINDINGS`, or `FAIL`.
- Unobserved runtime behavior, selector scoring, comprehension, navigation quality,
  and task success are not claimed.

## Expected Output

One evidence-linked conformance analysis grouped by contract, metadata, structure,
style, and workflow behavior, with a complete disposition and explicit evidence gaps.
