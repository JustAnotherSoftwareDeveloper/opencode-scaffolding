# Workspace Contract

## Workspace Structure

Create this workspace structure.

```text
.proposals/<unix-epoch-timestamp>-<summary-slug>/
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

Label an unresolved item as `Open Question: <question>`.

Record a material objection and its disposition in `Open Questions And Decision Record`.

## Document Requirements

Generate a table of contents in `PROPOSAL.md`.

Replace `{{source_document_toc_entries}}` with a relative link to every copied source document.

Link the implementation overview and every copied source document from `PROPOSAL.md`.

Use relative links only.

Keep `implementation.md` limited to ordered high-level sequence steps, outcomes, dependencies, decision gates, and validation summary.

Exclude commands, task assignments, source-file changes, estimates, owners, and runbook detail from `implementation.md`.
