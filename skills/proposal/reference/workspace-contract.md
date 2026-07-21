# Workspace Contract

## Workspace Structure

Create this workspace structure.

```text
.proposals/<epoch-ms>-<summary-slug>/
  PROPOSAL.md
  implementation.md
  analysis/
  research/
  requirements/
  design/
  notes/
  other/
```

Create only category directories that contain copied source documents.

Require an epoch-millisecond prefix and lowercase kebab-case summary slug.

Copy each supplied source document into its declared category directory.

Follow a symbolic link only when its resolved target is a regular file inside `$CWD`.

Preserve the source filename unless a collision requires a distinct suffix.

Reject a collision that cannot preserve both source documents distinctly.

## YAML Frontmatter

Use YAML frontmatter as the only workspace metadata store.

Set `title`, `slug`, `created`, `created-at`, `status`, `decision-owner`, and `source-documents` in `PROPOSAL.md`.

Set `title`, `proposal`, `slug`, `created`, and `status` in `implementation.md`.

Set `status` to `draft` when creating the workspace.

## Evidence Notation

Link evidence with a relative Markdown link to a copied source document.

Label an unverified statement as `Assumption: <statement>`.

Label material evidence that remains unavailable as `Evidence Gap: <missing evidence>`.

Label only an unresolved decision required from the responsible engineer as `Open Question: <question>`.

Resolve questions answerable through source review, analysis, research, testing, or discovery before drafting the proposal.

Record unavailable evidence as an evidence gap rather than an open question.

Record a material objection and its disposition in `Open Engineering Decisions And Decision Record`.

## Document Requirements

Generate a table of contents in `PROPOSAL.md`.

Include the eight proposal sections defined in the proposal template.

Keep the context box to three one-sentence bullets.

Keep the scope box to five one-sentence bullets.

Keep each option in the options box to four bullets.

Replace `{{source_document_toc_entries}}` with a relative link to every copied source document.

Link the implementation overview and every copied source document from `PROPOSAL.md`.

Use relative links only.

Keep the substantive body of `implementation.md` limited to concrete artifact and behavior changes plus evidence-supported dependencies, decision gates, and validation criteria.

Exclude commands, task assignments, estimates, owners, and runbook detail from `implementation.md`.

Name file or component paths when the sources establish them.

## Implementation Document Structure

Use an H2 heading for each affected area.

Use an H3 heading for each concrete change within that area.

Name the affected artifact, interface, workflow, or policy and its modification in each H3 heading.

Add one or two bullets beneath each H3 heading.

State the precise modification in the first bullet and its reason or intended effect in the second bullet when needed.

Use selective bolding for bullet labels rather than entire sentences.

Do not substitute a generic lifecycle sequence for the concrete changes.
