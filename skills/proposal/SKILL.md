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

Return `BLOCKED: Missing proposal topic.` when the input contains no topic or summary.

Return `BLOCKED: Missing source documents.` when the input contains no source paths.

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
12. Remove every authoring instruction and every optional section that does not apply.
13. Preserve each document's YAML frontmatter contract.
14. Replace `{{source_document_toc_entries}}` in `PROPOSAL.md` with relative links to every copied source document.
15. Generate the `PROPOSAL.md` table of contents.
16. Link every proposal section from the table of contents.
17. Link `implementation.md` from the table of contents.
18. Link every copied source document from the table of contents.
19. Link each material statement to a copied source document.
20. Label unverified material as `Assumption: <statement>`.
21. Resolve questions answerable through source review, analysis, research, testing, or discovery.
22. Label material evidence that remains unavailable as `Evidence Gap: <missing evidence>`.
23. Label only unresolved decisions required from the responsible engineer as `Open Question: <question>`.
24. Populate `implementation.md` with proposal-specific artifact and behavior changes under the structure in [the implementation format](./reference/implementation-format.md).
25. Name each known target, such as a file, component, data structure, API endpoint, workflow, or policy, and state its intended modification.
26. Reject implementation claims that lack proposal evidence or an explicit assumption label.
27. Reject generic lifecycle phases that lack proposal evidence.
28. Validate the completed workspace against [the workspace contract](./reference/workspace-contract.md).

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
- [ ] Every researchable unresolved matter is labeled as an evidence gap rather than an open question.
- [ ] Each concise box complies with its item and sentence limits.
- [ ] Each open question requires an engineer decision rather than further investigation.
- [ ] `implementation.md` groups proposal-specific changes by affected area and names each known target and modification.
- [ ] Every implementation claim is evidence-linked or explicitly labeled as an assumption.
- [ ] `implementation.md` contains no generic lifecycle phase unsupported by proposal evidence.
- [ ] Every concrete change uses the heading and bullet structure in the implementation format.
- [ ] Neither generated document contains a template placeholder or authoring instruction.
- [ ] Optional implementation sections appear only when proposal evidence supports their content.

## Expected Output

Create `.proposals/<epoch-ms>-<summary-slug>/`.

Create `PROPOSAL.md` as the canonical decision document.

Create `implementation.md` as the concrete implementation-change document with affected-area headings, concrete-change subheadings, and concise change details.

Copy source documents into their top-level category directories.

## Docs

See `./reference/README.md` for documentation of supporting files.
