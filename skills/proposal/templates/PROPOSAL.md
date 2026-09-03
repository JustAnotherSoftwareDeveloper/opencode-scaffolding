---
title: "{{title}}"
slug: "{{slug}}"
created: "{{epoch_milliseconds}}"
created-at: "{{utc_timestamp}}"
status: draft
readiness: not-ready
decision-owner: "{{decision_owner}}"
source-documents:
  - "{{source_document}}"
---

# {{title}}

## Table of Contents

- [Recommendation](#recommendation)
- [Technical Rationale](#technical-rationale)
- [Questions](#questions)
- [Options Considered](#options-considered)
- [Implementation Details](#implementation-details)
- [Verification Criteria](#verification-criteria)
- [Sources](#sources)

## Recommendation

{{selected_architecture_or_behavior_and_affected_boundary}}

<!-- State the decision first. Include its decisive constraint, material trade-off,
and compatibility consequence when applicable. Remove this comment before output. -->

## Technical Rationale

{{evidence_constraints_and_tradeoffs_supporting_the_recommendation}}

<!-- Name affected invariants and dependencies. Keep option-evaluation criteria
distinct from completion evidence. Remove this comment before output. -->

## Questions

- Assumption: {{unverified_decision_dependency_or_none}}
- Evidence Gap: {{unavailable_research_evidence_and_readiness_impact_or_none}}
- Open Question: {{residual_engineering_decision_owner_choices_and_deferral_or_none}}

<!-- Resolve researchable matters before drafting. Keep the three labels unchanged;
do not add research-question or decision-question aliases. Remove this comment before
output. -->

## Options Considered

### {{credible_option}}

- **Differentiator:** {{material_difference}}
- **Consequence:** {{benefit_cost_or_risk}}
- **Disposition:** {{selected_rejected_or_deferred_and_why}}

<!-- Repeat only for credible alternatives. Use a table only for genuinely comparable
rows and columns. Remove this comment before output. -->

## Implementation Details

### `{{affected_component_interface_or_path}}` — {{required_behavior_change}}

- **Change:** {{concrete_modification}}
- **Invariant:** {{behavior_or_boundary_that_must_remain_true}}
- **Compatibility and migration:** {{effect_or_not_applicable}}
- **Failure behavior:** {{material_failure_mode_or_not_applicable}}
- **Verification dependency:** {{test_inspection_or_observation}}

<!-- Add security, performance, reliability, rollback, data-flow, or operational
subsections only when the decision affects them. Describe the planning boundary, not
an execution runbook. Remove this comment before output. -->

## Verification Criteria

- **{{intended_result}}** — {{test_inspection_metric_observation_or_human_review}}

<!-- Map every intended result to completion evidence. Do not claim that structural
lint proves technical correctness, prose quality, or comprehension. Remove this
comment before output. -->

## Sources

- [{{descriptive_copied_source_name}}](./{{source_document}})

<!-- Every copied source appears exactly once here and once in frontmatter with the
same safe relative path. External bibliography entries are not copied-source manifest
entries. Remove this comment before output. -->
