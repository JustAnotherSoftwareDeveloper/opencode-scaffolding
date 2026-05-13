---
name: plan
description: Convert an accepted proposal into a concrete orchestration runbook with phases, delegation, parallelization, validation, and recovery.
---

# Plan Skill

Use this skill after a proposal is accepted, or when the user directly provides a sufficiently clear objective and asks for execution. The output is a runbook the orchestrator can follow.

## Required Runbook Format

```md
# Runbook: <short-name>

## Objective
<what success means>

## Proposal Summary
<accepted direction and why>

## Inputs
<files, docs, commands, user requirements, prior worker outputs>

## Constraints
<permissions, compatibility requirements, no-go areas, model/tool limits>

## Delegation Map
| Work | Agent | Skill | Parallel | Expected Output |
| --- | --- | --- | --- | --- |

## Execution Phases
1. Discover
2. Propose
3. Plan
4. Execute
5. Review
6. Retro

## Verification Gates
<specific checks that must pass>

## Rollback / Recovery
<how to recover from partial or failed execution>

## Final Report
<what the orchestrator must report back>
```

## Delegation Rules

- Every delegated item must have one bounded objective.
- Every delegated item must name an existing worker agent and a skill to load when applicable.
- Mark independent work as parallelizable.
- Use `explore` for fast read-only discovery.
- Use `librarian` for sourced synthesis from local files.
- Use `analysis-*` for reasoning, tradeoffs, risk analysis, and final judgment.
- Use `coding-*` for file edits, selected by complexity and risk.
- Use `doc-writer-*` for prompt, skill, command, and documentation prose.
- Use `oracle` for review gates.
- Use `websearch-*` only when current external documentation or source corroboration is required.

## Rules

- Do not implement changes.
- Do not delegate vague work. Rewrite vague items until they are executable.
- Include validation gates for JSON, YAML frontmatter, skill naming, command discovery, and agent discovery when relevant.
- Include a recovery path even when the expected change is small.
