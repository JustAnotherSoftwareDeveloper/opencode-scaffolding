---
name: proposal
description: "Use when creating an evidence-based decision proposal from source documents."
tags:
  - proposal-authoring
  - decision-record
  - evidence-linking
  - workspace-creation
  - proposal-sources
  - decision-proposal
class: operation
---

# Proposal

## Normalize Input

Require either a topic or summary.

Require explicit source-document paths.

Accept an optional source category for each path.

Assign uncategorized paths to `other`.

Return `BLOCKED: Missing proposal topic.` when the topic is absent.

Return `BLOCKED: Missing source documents.` when no source paths are supplied.

## Procedure

1. Classify each source document under [the workspace contract](./reference/workspace-contract.md).
2. Resolve each source path.
3. Reject invalid source paths under [the workspace contract](./reference/workspace-contract.md).
4. Derive an epoch-millisecond timestamp.
5. Create `$CWD/.proposals/<epoch-ms>-<summary-slug>/` without replacing an existing directory.
6. Create required category directories for supplied source documents.
7. Copy each source document without modifying it.
8. Copy [the proposal template](./templates/PROPOSAL.md) to the workspace as `PROPOSAL.md`.
9. Copy [the implementation template](./templates/implementation.md) to the workspace as `implementation.md`.
10. Populate both documents from copied source documents.
11. Replace every template placeholder.
12. Preserve each document's YAML frontmatter contract.
13. Replace `{{source_document_toc_entries}}` in `PROPOSAL.md` with relative links to every copied source document.
14. Generate the `PROPOSAL.md` table of contents.
15. Link every proposal section from the table of contents.
16. Link `implementation.md` from the table of contents.
17. Link every copied source document from the table of contents.
18. Link each material statement to a copied source document.
19. Label unverified material as `Assumption: <statement>`.
20. Label unresolved material as `Open Question: <question>`.
21. Validate the workspace against [the workspace contract](./reference/workspace-contract.md).

## Self-Validation

- [ ] The workspace name contains an epoch-millisecond timestamp.
- [ ] The workspace name contains a lowercase kebab-case summary slug.
- [ ] Every source document exists under its declared category directory.
- [ ] `PROPOSAL.md` contains valid YAML frontmatter.
- [ ] `implementation.md` contains valid YAML frontmatter.
- [ ] The proposal table of contents links to every required section.
- [ ] The proposal table of contents links to every copied source document.
- [ ] Every material claim is evidence-linked.
- [ ] Every unsupported material claim is explicitly labeled.
- [ ] `implementation.md` contains high-level ordered steps without task-level implementation detail.

## Expected Output

Create `.proposals/<epoch-ms>-<summary-slug>/`.

Create `PROPOSAL.md` as the canonical decision document.

Create `implementation.md` as the high-level implementation sequence.

Copy source documents into their top-level category directories.

## Docs

See `./reference/README.md` for documentation of supporting files.
