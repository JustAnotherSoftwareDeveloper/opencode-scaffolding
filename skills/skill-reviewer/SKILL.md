---
name: skill-reviewer
description: "Use when assessing one existing skill workspace for evidence-linked conformance findings and a bounded disposition."
selection:
  role: owner
  tags:
    actions: [assess, review]
    inputs: [existing skill workspace, class contract, selection profile]
    outputs: [conformance report]
    topics: [skill conformance, validation evidence]
    constraints: [read-only review, one workspace]
  use_when:
    - a maintainer needs findings and a pass/fail recommendation for one existing skill
  not_for:
    - creating or editing a skill, migrating a family, choosing taxonomy, or replacing validators
    - ordinary analysis unrelated to a skill-conformance review
class: operation
---

# Skill Reviewer

Assess one existing skill workspace against its applicable contracts and publish one
evidence-linked conformance report without changing the workspace.

## Normalize Input

Identify the existing skill path, intended class, applicable profile rules, templates,
style guidance, and maintenance checks. Load `skill-authoring-guide` as the canonical
prose-policy owner when semantic form selection and `TABLE-001` apply. When reviewing
authored prose or drafting the conformance report, load `markdown-writing-guide` as
passive context and read `markdown-writing-guide -> reference/writing-quality.md`
before relying on it.
Apply the guide to prose under review and report prose being authored, only where
compatible with the skill-specific semantic-form and `TABLE-001` policy, evidence
links, severity, report route, and read-only scope. In a canonical packet, use the guide
only if it is declared and already loaded; do not self-load it.

## Procedure

1. Identify the skill class and applicable contracts.
2. Inspect the complete skill workspace and referenced local resources.
3. Run available deterministic validation without changing the skill.
4. Compare observed content with the applicable contracts and templates. Assess prose
   form against `skill-authoring-guide -> reference/authoring-style.md`
   (`Choose prose structure by meaning` and `Do not use Markdown tables`) and
   `skill-authoring-guide -> reference/progressive-disclosure.md` (`TABLE-001 — No Tables`).
5. Separate deterministic conformance evidence from human clarity judgment. Do not
   treat lint as proof of readability, comprehension, navigation quality, or task
   success.
6. Publish one conformance report with findings, evidence links, disposition, and
   unavailable or inapplicable checks to repository-root
   `.audit/<epoch-ms>-<slug>.md`. Set `<epoch-ms>` to the report creation time in
   milliseconds since the Unix epoch. Set `<slug>` to a lowercase, hyphen-separated
   summary of the reviewed skill and report. Create repository-root `.audit/` if it is
   absent. Choose an unused destination rather than overwriting an existing report.
   Do not use this destination for ordinary analyses; this operation produces only its
   conformance review report.

## Self-Validation

- The review covers one existing workspace and does not modify it; only its report is
  written outside that workspace.
- The conformance report is under repository-root `.audit/` and includes the review
  findings and disposition.
- Every finding has a source path, evidence, severity, and bounded recommendation.
- Applicable findings distinguish deterministic prose-policy conformance from human
  clarity judgment.
- The disposition is `PASS`, `PASS WITH FINDINGS`, or `FAIL`.
- Unobserved runtime behavior, selector scoring, comprehension, navigation quality,
  and task success are not claimed.

## Expected Output

One evidence-linked conformance report grouped by contract, metadata, structure,
style, and workflow behavior, with a complete disposition and explicit evidence gaps.
