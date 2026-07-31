# Cross-domain skill-routing evaluation

## Evidence package

This repeatable suite is `scripts/python/tests/test_skill_routing_evaluation.py`
with inventory fixture
`scripts/python/tests/fixtures/skill_routing/evaluation.json`. The fixture
contains 6 candidates and 10 adjudicated cases across business, agriculture,
healthcare, and arts. It explicitly covers owner versus reference, unrelated
domains, near-neighbors, absent lexical overlap, aliases, hierarchy,
repository-local facets, namespace failures, and a three-skill task.

The render identity tested by both paths is `task-skill-routing-signature-v2`.
The repository-local `orchard:crop-stage` facet is declared in the fixture and
is observed in deterministic cue text and Qwen skill rendering; no core-code
branch is added for it. Namespace collision and foreign-namespace fixtures are
also required to fail with actionable routing-contract errors.

## Metrics

The test computes precision, recall, and exact-set accuracy for the
deterministic path from the production lexical selector. Qwen diagnostics use
the captured scorer boundary and record render identity, token counts, prompt
hashes, and clipped labels. The checked evaluation run records:

| Path | Precision | Recall | Exact-set accuracy | Clipping | Token impact |
| --- | ---: | ---: | ---: | --- | --- |
| deterministic | 0.700 | 0.727 | 0.500 | not applicable | routing cues included; measured by test preflight |
| Qwen diagnostic | 1.000 | 1.000 | 1.000 | `no` label captured | 211 tokens per captured pair |

These are targeted fixture results, not a cutover gate or a claim about an
uncaptured model run. The selection-policy thresholds remain the existing
`additional_skill_threshold=0.8`, `low_confidence_threshold=0.8`, and
`max_skills=3`; the suite does not alter them.

## Inventory identity and reproducibility

- Fixture schema: `1`
- Render version: `task-skill-routing-signature-v2`
- Inventory: 6 candidates; 4 domains; 10 cases; 10 case IDs are unique
- Case families: owner/reference, unrelated-domain, near-neighbor,
  absent-lexical-overlap, aliases, hierarchy, repository-local-facet,
  namespace-failure, multi-skill-task
- Qwen diagnostics: captured model identity `captured-qwen`, prompt version
  `qwen3-reranker-4b-classifier-v1`, 60 clipped-label entries, and token count
  `211` per pair

Run with `cd scripts/python && pytest -q tests/test_skill_routing_evaluation.py`.
