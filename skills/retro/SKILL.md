---
name: retro
description: Improve the orchestration harness after execution by identifying changes to agents, skills, commands, runbooks, and routing rules.
---

# Retro Skill

Use this skill after review, especially after harness changes, migrations, failed delegations, or ambiguous workflows. The goal is to improve the system that produced the work.

## Inputs

- User request.
- Proposal, runbook, and delegation map.
- Worker outputs.
- Review findings.
- Validation failures or friction encountered during execution.

## Output Format

Return exactly these sections:

## What Worked
List routing decisions, prompts, skills, commands, or validation steps that should be kept.

## Friction
List specific issues that slowed work, caused ambiguity, or created risk.

## Harness Improvements
Recommend changes to orchestrator prompts, Agent Architect behavior, worker routing, or runbook conventions.

## Skill Improvements
Recommend additions, removals, or rewrites to skills.

## Command Improvements
Recommend slash command changes or new command templates.

## Action Items
List concrete follow-up items with priority: high, medium, or low.

## Rules

- Optimize for future reliability, not post-hoc justification.
- Prefer a few high-leverage fixes over many speculative improvements.
- Separate immediate fixes from ideas that need their own proposal and plan.
