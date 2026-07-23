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

List every copied source document under `source-documents` by its workspace-relative path.

Set `title`, `proposal`, `slug`, `created`, and `status` in `implementation.md`.

Set `status` to `draft` when creating the workspace.

## Evidence Notation

Use the material-claim and inline-link rules in [proposal-format.md](./proposal-format.md).
Link evidence with a relative Markdown link to a copied source document.

Label an unverified statement as `Assumption: <statement>`.

Label material evidence that remains unavailable as `Evidence Gap: <missing evidence>`.

Label only an unresolved decision required from the responsible engineer as `Open Question: <question>`.

Resolve questions answerable through source review, analysis, research, testing, or discovery before drafting the proposal.

Record unavailable evidence as an evidence gap rather than an open question.

Record a material objection and its disposition in the decision record.

## Document Requirements

Follow the semantic-core, proportionality, plain-Markdown, and navigation rules
in [proposal-format.md](./proposal-format.md).

Require a summary, problem and context, scope, options and recommendation,
requirements, acceptance criteria, decision record, and supporting sources.
Combine compatible required content under clear headings when that makes a short
proposal easier to review.

Omit optional sections that have no applicable evidence. Do not create empty
sections, decorative blockquotes, or presentation-only callout boxes.

Add a table of contents only when document length or expanded structure makes
navigation materially useful. When present, link proposal sections,
`implementation.md`, and the supporting-sources section.

List every copied source document once in **Supporting sources**. Do not repeat
individual source links in the table of contents.

Link `implementation.md` from the recommendation and from the table of contents
when navigation is present.

Use relative links only. Remove authoring instructions and placeholders from
completed documents.

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
