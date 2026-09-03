# One-document proposal examples

These authored fixtures demonstrate the active [proposal format](../reference/proposal-format.md),
[workspace contract](../reference/workspace-contract.md),
[implementation format](../reference/implementation-format.md), and
[writing style](../reference/writing-style.md). They are examples, not templates or
evidence that the format improves reader comprehension.

## Example workspaces

- **[Short proposal](./short-proposal/PROPOSAL.md):** One bounded template change with
  compact implementation and verification detail and no unnecessary optional sections.
- **[Standard proposal](./standard-proposal/PROPOSAL.md):** A cross-component CLI and
  library change with compatibility behavior, typed Questions, and test dependencies.
- **[Complex proposal](./complex-proposal/PROPOSAL.md):** A systems change with justified
  security, performance, reliability, migration, rollback, and failure-mode depth.

Each workspace contains one authored `PROPOSAL.md` plus only the copied source files
declared in its frontmatter. The examples retain `Assumption:`, `Evidence Gap:`, and
`Open Question:` as stable labels under `Questions`.

## Deterministic checks

Workspace and Markdown validation can establish observable contract properties:

- required metadata and allowed readiness values;
- unique required H2 headings in the documented order;
- complete, ordered, non-recursive table-of-contents links;
- safe copied-source paths and exact manifest-to-`Sources` identity;
- valid relative links and proposal-profile table handling;
- absence of placeholders, authoring comments, unsupported aliases, and legacy
  authored artifacts; and
- stable diagnostics and exit behavior.

A passing check does not establish technical correctness, prose quality, question
researchability, architecture quality, or reader comprehension.

## Formal engineering review

A reviewer should be able to identify and accurately paraphrase:

1. the recommended architecture or behavior;
2. the decisive constraints, evidence, and trade-offs;
3. affected components, interfaces, and invariants;
4. compatibility, migration, rollback, and failure implications where material;
5. the difference between unavailable research and residual owner decisions;
6. the concrete implementation boundary; and
7. the tests, inspections, metrics, or observations demonstrating completion.

Review also checks that each section adds decision-relevant information, terminology is
stable, implementation detail is sufficient for planning without becoming a runbook,
and completion evidence maps to intended results. Record uncertainty rather than using
lint success as a proxy for these judgments.

Measured comprehension claims require matched reader testing. Structural conformance
and example quality alone do not prove that readers are faster or more accurate.
