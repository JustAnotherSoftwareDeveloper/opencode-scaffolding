# Error Handling And Testing

Integration tests must prove the shared direct-selection workflow.

## Required Checks

- Inventory collection occurs exactly once and both workflows use that snapshot.
- No planning reranker, selector, score/rank/threshold policy, or fallback path is invoked.
- Planning loads are uncapped and task assignment is one to three.
- Names, classes, and collector-winning paths are reconciled before and after execution.
- Copied plan sources and non-skill task fields are preserved.
- Invalid assignments, contract mismatches, validation errors, and publication errors fail closed.
- Existing outputs are not replaced and no partial output remains.

Use deterministic LLM-selection fixtures or stubs; tests must validate orchestration behavior rather than pretend a Python scorer proves semantic selection.
