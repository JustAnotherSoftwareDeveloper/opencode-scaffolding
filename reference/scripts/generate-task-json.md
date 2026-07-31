# Generate Task JSON Routing Guidance

## Candidate Contract

Generate task JSON from a frozen inventory and normalized skill metadata.
Render candidate relationships, facets, canonical values, and relevant aliases explicitly.
Keep the primary owned operation visible for owner candidates.

## Selection Procedure

1. Validate task input, registries, and candidate metadata through the shared validator.
2. Render deterministic task fields and candidate evidence.
3. Apply the configured context safety cap before model access.
4. Score candidates through the selected model or explicit lexical path.
5. Preserve inventory order for ties and publish only inventory names.
6. Record owner, support, or reference evidence with confidence diagnostics.

## Evaluation

Evaluate owner tasks against nearest competitors, unrelated tasks, paraphrases, and low-overlap requests.
Measure precision, recall, exact-set accuracy, clipping, and token impact.
Review frequent cues as diagnostics rather than invalidation conditions.

## Extension

Load repository-owned namespaced facet and value declarations before rendering.
Reject undeclared facets, foreign namespaces, built-in redefinitions, and canonical collisions.
Allow valid repository extensions without changing core code.
