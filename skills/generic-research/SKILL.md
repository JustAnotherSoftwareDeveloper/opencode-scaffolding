---
name: generic-research
description: "Use when a user asks to discover external evidence and produce a bounded, source-grounded answer or descriptive findings synthesis."
selection:
  role: owner
  tags:
    actions: [research, synthesize]
    inputs: [bounded question, external evidence]
    outputs: [source-grounded answer, research artifact bundle]
    topics: [external evidence]
    constraints: [external discovery required, no subdelegation]
  use_when:
    - The requested result is an answer or descriptive findings synthesis that requires discovering external evidence.
  not_for:
    - Descriptive synthesis of only user-supplied sources when no external discovery is requested; generic-analysis owns this case.
    - Evidence-calibrated assessment or recommendations; generic-analysis owns those results.
    - A durable decision proposal; proposal owns that result.
class: operation
---

# Research Workflow

Use this operation for one bounded request whose terminal result is a source-grounded answer or descriptive findings synthesis based on external evidence discovery. It does not subdelegate, decide among options, recommend action, or create a durable decision proposal.

## Normalize Input

Record the question, intended use when material, domain and scope, time boundary, supplied materials or source restrictions, and requested depth or form. Clarify or stop if missing scope prevents a useful answer. When the user supplies all sources and requests no external discovery, leave the request with `generic-analysis`.

## Procedure

1. Normalize the request and identify the material claims needed to answer it.
2. Set task-relative evidence needs and identify claims essential to the answer or materially relevant to its stated use. Use [task-sensitive source quality](reference/source-quality.md).
3. Search EXA first, inspect returned source pages, and apply only the bounded fallback triggers in [search routing](reference/search-routing.md).
4. Synthesize inspected evidence into a direct answer; trace material claims and disclose uncertainty using [evidence synthesis](reference/evidence-synthesis.md).
5. Persist the completed answer and its source-to-claim record as a new bundle under `.research/`, following [research artifacts](reference/research-artifacts.md). Do not overwrite a prior run.
6. Check that the answer addresses the normalized question, material claims trace to inspected passages, limits are visible, and every required artifact is persisted.

## Self-Validation

- Does the result answer the normalized question without changing research into assessment, recommendation, or proposal?
- Is each material claim supported by inspected evidence or explicitly marked as interpretation, uncertainty, or unsupported?
- Were EXA-first routing and any fallback attempt recorded with unavailable provenance fields left explicitly unavailable?
- Does the complete bundle exist at a unique path under `.research/` without changing existing files or tracking policy?
- If evidence is insufficient or persistence fails, is the gap reported instead of claiming completion?

## Expected Output

Return the source-grounded answer or descriptive findings, important disagreements and limits, and the durable bundle path. Do not report completion if the answer or required bundle is incomplete.

## References

- [Reference index](reference/README.md)
- [Search routing](reference/search-routing.md)
- [Evidence synthesis](reference/evidence-synthesis.md)
- [Research artifacts](reference/research-artifacts.md)
- [Source quality](reference/source-quality.md)
