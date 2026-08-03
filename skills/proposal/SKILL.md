---
name: proposal
description: "Use when creating an evidence-based decision proposal from source documents."
selection:
  role: owner
  tags:
    actions: [author proposal]
    inputs: [source documents]
    outputs: [evidence-based proposal]
    topics: [decision proposal]
    constraints: [evidence preserving]
  use_when: [source documents must become a durable decision proposal]
  not_for: [general assessment or executable task planning]
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
10. Populate both documents from copied source documents under the [proposal format](./reference/proposal-format.md).
11. Expand the `{{source_document}}` template entry into one YAML list item per copied source and replace every remaining placeholder.
12. Combine compatible required sections for short proposals and remove every optional section that does not apply.
13. Preserve each document's YAML frontmatter contract and list every copied source under `source-documents`.
14. Use descriptive relative inline links for material claims and list copied sources once in **Supporting sources**.
15. Link `implementation.md` from the recommendation and add a table of contents only when document length or structure materially improves navigation.
16. Label unverified material as `Assumption: <statement>`.
17. Resolve questions answerable through source review, analysis, research, testing, or discovery.
18. Label material evidence that remains unavailable as `Evidence Gap: <missing evidence>`.
19. Label only unresolved decisions required from the responsible engineer as `Open Question: <question>`.
20. Populate `implementation.md` with proposal-specific artifact and behavior changes under the structure in [the implementation format](./reference/implementation-format.md).
21. Name each known target, such as a file, component, data structure, API endpoint, workflow, or policy, and state its intended modification.
22. Reject implementation claims that lack proposal evidence or an explicit assumption label.
23. Reject generic lifecycle phases that lack proposal evidence.
24. Validate the completed workspace against [the workspace contract](./reference/workspace-contract.md).

## Self-Validation

- [ ] The workspace name contains an epoch-millisecond timestamp.
- [ ] The workspace name contains a lowercase kebab-case summary slug.
- [ ] Every source document exists under its declared category directory.
- [ ] `PROPOSAL.md` contains valid YAML frontmatter.
- [ ] `implementation.md` contains valid YAML frontmatter.
- [ ] `PROPOSAL.md` contains the required semantic decision content with only applicable optional sections.
- [ ] `PROPOSAL.md` uses sentence-case headings, ordinary Markdown structures, and one supporting-sources index.
- [ ] `PROPOSAL.md` links the implementation overview from the recommendation.
- [ ] A table of contents appears only when it materially improves navigation and does not repeat source links.
- [ ] Every material claim is evidence-linked.
- [ ] Every unsupported material claim is explicitly labeled.
- [ ] Every researchable unresolved matter is labeled as an evidence gap rather than an open question.
- [ ] Each open question requires an engineer decision rather than further investigation.
- [ ] `implementation.md` groups proposal-specific changes by affected area and names each known target and modification.
- [ ] Every implementation claim is evidence-linked or explicitly labeled as an assumption.
- [ ] `implementation.md` contains no generic lifecycle phase unsupported by proposal evidence.
- [ ] Every concrete change uses the heading and bullet structure in the implementation format.
- [ ] Neither generated document contains a template placeholder or authoring instruction.
- [ ] Optional implementation sections appear only when proposal evidence supports their content.
- [ ] The completed documents conform to the applicable short, standard, or complex guidance and [format fixtures](./reference/fixtures/README.md).

## Expected Output

Create `.proposals/<epoch-ms>-<summary-slug>/`.

Create `PROPOSAL.md` as the canonical decision document.

Create `implementation.md` as the concrete implementation-change document with affected-area headings, concrete-change subheadings, and concise change details.

Copy source documents into their top-level category directories.

## Docs

See `./reference/README.md` for documentation of supporting files.
