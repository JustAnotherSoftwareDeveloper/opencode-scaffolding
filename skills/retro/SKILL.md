---
name: retro
description: Improve the orchestration harness after execution by identifying changes to agents, skills, commands, runbooks, and routing rules.
---

# Retro Skill

Use this skill after meaningful harness work to identify what should be preserved, what should change, and which harness improvements should be made before future runs.

Retro complements `lesson-writer`: retro identifies harness improvements, while `lesson-writer` captures reusable session guidance in durable `.lessons/` artifacts.

## Inputs

- User request and accepted proposal or plan.
- State workspace summary.
- Worker outputs.
- Validation results.
- Review findings from embedded quality checks.
- Any recovery steps taken.

## Output Format

Return exactly these sections:

## What Worked
List routing patterns, prompts, skills, commands, validation steps, or state practices that should be kept.

## What Should Change
List concrete harness improvements needed before similar future work.

## Harness Guidance
Describe updates to agents, skills, commands, runbooks, state practices, or routing rules.

## Validation Improvements
List checks that should be added, removed, clarified, or run earlier.

## Lesson Feed
State whether the retro output should feed `lesson-writer` and summarize the durable lesson to capture.

## Follow-Up Actions
List bounded follow-up tasks, each with an owner or suggested worker family when appropriate.

## Rules

- Focus on improving the orchestration harness, not re-summarizing every completed task.
- Keep recommendations concrete and actionable.
- Do not modify files while writing the retro.
- Do not propose model, provider, or generated-runtime changes unless explicitly requested.
- If a durable session lesson is warranted, recommend invoking `lesson-writer` for a `.lessons/` artifact.
