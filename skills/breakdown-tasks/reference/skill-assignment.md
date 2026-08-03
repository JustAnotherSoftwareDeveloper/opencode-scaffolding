# Direct Skill Selection

Both planning and plan workflows use this contract.

## One Frozen Inventory

Collect one complete inventory before selection. It is the sole authority for names, classes, profiles, source roots, and collector-winning absolute `SKILL.md` paths. Do not recollect or infer identity from filenames, paths, scores, or stale metadata.

## Planning Selection

Show the request and all planning-class profiles to the LLM. Load every materially relevant profile, with no numeric cap. Load only selected names, exactly once, through the skill tool. A planning load is passive context and does not grant execution or write authority. An empty selection is valid when no planning concern exists.

## Task Assignment

Show the complete draft and operation/documentation profiles to the LLM. Select one to three semantically fitting skills per task. A no-match decision blocks rather than inventing a name or using a fallback. Inspect selected contracts and reconcile each name, class, cardinality, and winning path before generation.

## Prohibited Semantics

Do not use a selector, reranker, lexical or path fallback, score, rank, threshold, confidence policy, clipping, popularity, or model-specific assignment mode. Do not manually add, remove, reorder, or repair assignments.

## Audit And Publication

Reconcile the generated packet against the unchanged snapshot and selected contracts. Preserve every non-skill field and authored order. The generator validates final membership and publishes atomically; any mismatch, schema error, or publication error fails closed.
