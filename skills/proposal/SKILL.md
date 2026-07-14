---
name: proposal
description: "Use when creating a decision-ready proposal from prior workflow analysis, research, requirements, designs, or notes."
tags:
  - proposal-authoring
  - decision-record
  - evidence-synthesis
  - workflow-artifacts
  - implementation-overview
class: operation
---

# Proposal

## Normalize Input

Require a topic or summary and explicit source-document paths.

Accept an optional source category for each path.

Assign uncategorized paths to `other`.

Return `BLOCKED: Missing proposal topic.` when the topic is absent.

Return `BLOCKED: Missing source documents.` when no source paths are supplied.

## Procedure

1. Classify each source document as `analysis`, `research`, `requirements`, `design`, `notes`, or `other`.
2. Resolve each source path and reject a missing path, a non-file path, a path whose resolved target is outside `$CWD`, or a path within the new proposal workspace.
3. Create `$CWD/.proposals/<unix-epoch-timestamp>-<summary-slug>/` without replacing an existing directory.
4. Create the required category directories for supplied source documents and copy each source document without modifying it.
5. Copy `templates/PROPOSAL.md` to the workspace as `PROPOSAL.md` and copy `templates/implementation.md` to the workspace as `implementation.md`.
6. Populate both documents from the copied source documents and replace every template placeholder while preserving their YAML frontmatter contracts.
7. Replace `{{source_document_toc_entries}}` in `PROPOSAL.md` with relative links to every copied source document.
8. Generate the `PROPOSAL.md` table of contents with links to every proposal section, `implementation.md`, and every copied source document.
9. Link each material claim, requirement, option rationale, and implementation step to a copied source document or label it as an assumption or open question.
10. Validate the workspace against the rules in [the workspace contract](./reference/workspace-contract.md).

## Self-Validation

- [ ] The workspace name contains a Unix epoch timestamp and lowercase kebab-case summary slug.
- [ ] Every source document exists under its declared category directory.
- [ ] `PROPOSAL.md` and `implementation.md` contain valid YAML frontmatter.
- [ ] The proposal table of contents links to every required section and copied source document.
- [ ] Every material claim is evidence-linked or explicitly labeled.
- [ ] `implementation.md` contains high-level ordered steps without task-level implementation detail.

## Expected Output

Create `.proposals/<unix-epoch-timestamp>-<summary-slug>/`.

Create `PROPOSAL.md` as the canonical decision document.

Create `implementation.md` as the high-level implementation sequence.

Copy source documents into their top-level category directories.

## Docs

See `./reference/README.md` for workspace, evidence, and proposal-section rules.
