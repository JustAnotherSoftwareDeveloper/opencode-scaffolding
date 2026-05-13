---
name: review-work
description: Review completed harness work for correctness, config validity, prompt quality, permission safety, and runbook fidelity.
---

# Review Work Skill

Use this skill after execution and before the orchestrator reports success. The review should identify defects, regressions, missing validation, and harness-quality problems.

## Inputs

- User request.
- Proposal and runbook, if available.
- Files changed.
- Worker outputs.
- Validation results.

## Output Format

Return exactly these sections:

## Findings
List findings first. For each finding include severity, file path, line reference when available, and why it matters. If there are no findings, say `No findings.`

## Runbook Fidelity
State whether execution matched the runbook and note any deviations.

## Config And Schema Validity
Review JSON validity, markdown frontmatter shape, command definitions, skill naming rules, and agent mode/hidden usage.

## Permission Safety
Review task permissions, skill permissions, write permissions, and accidental over-broad access.

## Prompt Quality
Review whether prompts are specific, bounded, non-contradictory, and useful for future agents.

## Missing Verification
List checks that should still be run or could not be run.

## Recommendation
State whether to accept, fix before accepting, or redesign.

## Rules

- Findings are the primary output. Do not bury them after a summary.
- Do not modify files while reviewing.
- Be concrete and cite exact files.
- Distinguish correctness issues from style preferences.
