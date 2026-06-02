---
id: <unix-timestamp>-<slug>
title: "<Human-readable title>"
status: draft
created_at: "<ISO 8601 timestamp>"
updated_at: "<ISO 8601 timestamp>"
proposal: "../../.proposals/<timestamp>-<proposal-slug>/INDEX.md"
---

# Plan: <title>

This `INDEX.md` is the canonical entry point for a plan workspace. Keep it reviewable on its own and link to supporting files when detail would otherwise make the plan hard to scan.

For small plans, fill the sections below inline instead of creating supporting files. For larger plans, keep a concise summary in `INDEX.md` and link to the supporting file that carries the detail.

## Goal

<One or two sentences describing what this plan accomplishes.>

## Non-Goals

- <Explicitly excluded work.>

## Source Proposal

- Proposal: `<relative path to accepted proposal>`
- Accepted decisions to preserve:
  - <Decision and reason.>

## Accepted Decisions

- <Planning-level decision about sequencing, routing, or constraints.>

## Workspace Contents

| File | Purpose |
| --- | --- |
| `INDEX.md` | Canonical plan entry point and review target. |
| `context.md` | Current state, file scope, constraints, assumptions. |
| `skill-map.md` | Skill/file routing and anti-patterns. |
| `validation.md` | Validation gates and rollback/recovery details. |
| `runbook-handoff.md` | Inputs for the `runbook` skill after approval. |

## Current State Summary

<Summarize only the facts a reviewer must know before approving. For larger plans, put the full inventory in [`context.md`](context.md).>

## Design

<Describe the shape of the intended change. Avoid executable runbook steps.>

## Implementation Strategy

<List coarse phases. For each phase, name files, skill guidance, expected output, and validation.>

## Skill/File Routing Summary

<Include the most important routing rows here. For larger plans, put the full map in [`skill-map.md`](skill-map.md).>

## Artifact Impact

| File / directory | Action | Notes |
| --- | --- | --- |
| `<path>` | create / modify / delete | <Why this artifact changes.> |

## Validation

<Include commands or manual checks with pass/fail conditions. For larger plans, put the full gate list in [`validation.md`](validation.md).>

## Rollback / Recovery

<Include the recovery path for each modification or deletion. For larger plans, put the full recovery table in [`validation.md`](validation.md).>

## Acceptance Criteria

- <Objectively testable completion criterion.>

## Runbook Generation Handoff

See [`runbook-handoff.md`](runbook-handoff.md). The plan does not execute; approved plans are converted into runbooks.
