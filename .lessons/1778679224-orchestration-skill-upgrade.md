---
artifact_type: lesson
schema_version: 1
id: 1778679224-orchestration-skill-upgrade
session_id: null
created_at: 2026-05-13
source_plan: ../.plans/1778673424-orchestration-skill-upgrade.md
source_state: ../.state/1778673424-orchestration-skill-upgrade/
---

# Lesson: Orchestration Skill Upgrade

## Context

This session upgraded the global OpenCode orchestration harness to use timestamped proposal, plan, state, and lesson artifacts. It also aligned routing with the current sized worker families and added a durable lesson-writing skill.

## What Happened

The plan successfully produced the target harness changes, but several delegated apply workers returned tool-call stubs instead of actually editing files. The orchestrator used the plan recovery path, applied bounded edits directly, recorded the runbook deviation in state, and continued through embedded quality check and targeted validation.

## Lesson

For harness changes, keep apply steps small and independently verifiable, but expect recovery when a worker returns instructions instead of edits. State should explicitly record the planned worker, actual executor, verification performed, and reason for recovery. This preserves transparency without blocking progress.

## Future Guidance

- Treat worker output that only describes a tool call as a failed apply step.
- Escalate or recover immediately rather than repeatedly retrying the same broken apply pattern.
- Validate changed active harness files with grep-style checks for removed routing names and legacy concepts before proceeding.
- Keep state current even when execution deviates from the runbook.
- Prefer direct bounded recovery only after delegation has been attempted and the failure mode is clear.

## Applies To

- Artifact-driven harness upgrades.
- Plan execution with per-step state files.
- Worker routing migrations.
- Sessions where apply workers fail to make concrete file changes.
