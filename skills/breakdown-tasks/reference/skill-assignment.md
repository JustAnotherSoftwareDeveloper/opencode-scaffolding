# Skill Assignment Procedure

Use one frozen inventory and one explicit assignment mode.

## Candidate Evidence

Render each candidate's name, description, normalized structured cues, relationships, and class.
Render canonical values with relevant aliases and facet identities.
Keep owner, support, and reference relationships distinct from cue values.
Exclude candidate source and path from model text.

## Qwen Mode

1. Validate the complete draft, frozen inventory, registries, and candidate metadata before model initialization.
2. Render complete task fields and candidates in stable order.
3. Count every complete pair with the pinned tokenizer.
4. Reject pairs above the configured context bound before HTTP access.
5. Score candidates sequentially with the checked local profile.
6. Stable-sort finite scores by descending value and inventory order.
7. Select the top candidate and apply the configured confidence policy for additional candidates.
8. Publish only names supplied by the frozen inventory.

## Lexical Mode

Use normalized canonical values and aliases directly.
Apply lexical mode only through an explicit assignment decision.
Keep selection policy separate from cue validation.

## Read-Only Audit

1. Reuse the frozen inventory.
2. Verify canonical names, registry membership, relationship roles, semantic fit, atomicity, and cross-task consistency.
3. Block invalid assignments without rewriting generated assignments.

## Output

Write one schema-valid `BreakdownTasksOutput` object.
Preserve every non-skill draft field.
Record routing evidence and confidence diagnostics without mutating the task after generation.
