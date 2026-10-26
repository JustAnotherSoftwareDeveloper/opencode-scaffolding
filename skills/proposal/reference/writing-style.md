# Proposal writing style

Write concise, neutral engineering prose. Preserve technical meaning over stylistic
uniformity. These are review rules, not lexical bans, readability scores, or quotas.

## Lead with the decision

- State the selected architecture, contract, or behavior first.
- Name the affected component or boundary before background.
- Put the decisive constraint or trade-off before secondary evidence.
- State material compatibility, migration, and operational consequences early.
- Keep each section's first substantive block responsive to its review purpose.

## Use direct engineering prose

- Name the actor and action: “The proposal validator rejects unsafe source paths,”
  not “Unsafe source paths are subject to rejection.”
- Prefer direct verbs such as `validate`, `parse`, and `reject` over nominalizations.
- Use established engineering terminology when it improves precision; define
  repository-specific terms on first use and keep component names stable.
- Use present tense for current behavior. Use normative words only for enforced
  contract requirements.
- Use first person only for explicit project decisions and second person only for
  procedures. Do not default to contractions or casual copywriting.

## Maximize information density

- Give each sentence one primary technical claim and each paragraph one review
  function. Keep clauses together when their relationship carries technical meaning.
- Remove process narration, repeated rationale, ornamental qualification, and
  background that does not alter scope, risk, or the recommendation.
- Put evidence and qualifications next to the claim they support. Prefer one
  descriptive decision-changing link over citation clusters.
- Use examples for interfaces, state transitions, edge cases, or failure modes—not to
  restate the rule.
- Never compress away an invariant, caveat, uncertainty, or compatibility consequence.

## Expose technical landmarks

- Start headings and bullets with component names, interfaces, constraints, or outcomes.
- Use code formatting for paths, symbols, commands, schemas, and configuration keys.
- Distinguish current behavior, proposed behavior, and compatibility impact.
- Surface interfaces, invariants, dependencies, migration, rollback, security,
  performance, reliability, failure modes, and verification evidence when material.
- Use bullets for independent parallel points and numbers for sequences.
- Use bold labels only when they help comparison or retrieval.
- Do not use Markdown tables in proposal content. Use bullets, ordered lists,
  paragraphs, definition lists, or subsection headings according to semantic purpose.
  `TABLE-001` remains the sole authority for its exact `display-tasks` exception; this
  proposal reference grants no table exception.
- Use Title Case for non-core proposal headings, including optional or domain-specific
  H2s and H3s. Preserve established technical terminology, identifiers, and other
  capitalization that carries technical meaning.
- Keep the exact wording, capitalization, and order of the eight required core H2
  labels from `proposal-format.md`: `Table of Contents`, `Recommendation`,
  `Technical Rationale`, `Questions`, `Options Considered`, `Implementation Details`,
  `Verification Criteria`, and `Sources`. Preserve the seven fixed core TOC labels and
  link text exactly as shown there, and do not include `Table of Contents` in its own
  contents.
- This guidance does not authorize rewriting historical `.proposals/` workspaces.

## Preserve evidence meaning

Keep `Assumption:`, `Evidence Gap:`, and `Open Question:` stable and distinct. Distinguish
direct source facts, cross-source synthesis, interpretation, and the proposal's local
recommendation; do not present an inference or local choice as a source fact or external
requirement. Put attribution and qualifications beside the claim. A citation shows
provenance, not evidence strength. State material limitations and contrary or qualifying
evidence, and distinguish unavailable, silent, and contradictory evidence when relevant.
Bound claims to their sources' scope and time; distinguish formal standards from
project-specific templates and recurring conventions. Do not infer general prevalence or
a universal standard from local or repeated practice. Never turn unavailable research
into an owner decision or make weak evidence look stronger through emphasis.

## Engineering review passes

1. **Decision:** Is the selected direction explicit?
2. **Completeness:** Are components, interfaces, invariants, compatibility, risks, and
   questions represented where material?
3. **Order:** Does each section answer the next engineering review question?
4. **Compression:** Is repeated rationale and process narration removed?
5. **Precision:** Are terms, identifiers, units, thresholds, and normative claims exact?
6. **Scanability:** Do headings, labels, lists, and paragraphs expose landmarks?
7. **Verification:** Does each intended result map to evidence of completion?
8. **Final read:** Does the prose avoid template-generated or bureaucratic phrasing?

## Before and after

**Robotic prose**

- Before: “Validation of source path correctness will be performed by the validator.”
- After: “The validator rejects source paths outside the proposal workspace.”
- Why: The rewrite names the component, action, boundary, and failure behavior.

**Weak implementation detail**

- Before: “Update proposal handling.”
- After: “`lint-md` accepts a proposal directory, parses `PROPOSAL.md`, and reports
  malformed frontmatter as a stable workspace violation.”
- Why: The rewrite identifies the target, interface behavior, and observable result.

**Ambiguous uncertainty**

- Before: “Open Question: Is the source list complete?”
- After: “Evidence Gap: Repository discovery has not confirmed every active consumer;
  completion remains blocked until the search is classified.”
- Why: Inspection can answer the question, so it is research rather than owner policy.

## Human evidence boundary

Markdown and workspace checks establish deterministic conformance only. A human review
assesses technical correctness, information density, researchability, and whether a
reader can identify the recommendation, constraints, affected interfaces, unresolved
questions, implementation boundary, and completion evidence. Claims about improved
reader comprehension require measured reader evidence, not example conformance.
