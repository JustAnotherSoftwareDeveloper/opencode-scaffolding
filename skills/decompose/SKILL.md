---
name: decompose
description: Break work into atomic units when scope, steps, or file boundaries are unclear. May delegate to worker for analysis when the work structure is ambiguous.
class: planning
---

# Decompose Skill

Use this skill when you need to analyze, classify, or break down work into atomic units but are uncertain about scope boundaries, step sequencing, or file groupings.

## When to Use

- You are unsure how to decompose a task or phase into atomic units.
- The work spans unclear boundaries or multiple capability domains.
- You need to validate that your decomposition is sufficiently atomic.
- The task has mixed complexity levels or intertwined concerns.

## Output Format

```markdown
## Analysis

Brief summary of the work and key considerations.

## Recommended Phase

proposal | plan | runbook | execute | none

## Atomic Units

| Unit | Objective | Files | Skill | Risk |
|------|-----------|-------|-------|------|
| 01 | <one objective> | <bounded files> | <skill or none> | <high/med/low> |
```

## Decomposition Patterns

### Single-file changes
- Identify the file and the required change.
- Return one atomic unit scoped to that file.

### Multi-file implementation
- Group files by similar change type (edits, creates, deletes).
- Separate unrelated file sets into distinct units.

### Cross-cutting changes
- Identify the core change and its dependencies.
- Return units in dependency order if sequential work is needed.

### Ambiguous scope
- Delegate analysis to `worker` with this skill loaded.
- The worker may run discovery to clarify boundaries.

## Delegation Guidance

When uncertainty is high:
1. Load this skill with `worker` using analysis-mode instructions.
2. Include the original user request and any available context.
3. Request: recommended phase, atomic breakdown, and risk assessment.
4. Review the worker's analysis, then proceed with actual delegation.

## Rules

- Do not create artifacts while using this skill.
- Focus on analysis, not implementation.
- Each unit must have a single objective and bounded files.
- Workers may use discovery skills if needed to inform the analysis.