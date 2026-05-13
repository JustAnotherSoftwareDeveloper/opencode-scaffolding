---
name: plan
description: Convert an accepted proposal into a concrete orchestration runbook with phases, delegation, parallelization, validation, and recovery.
---

# Plan Skill

Use this skill after a proposal is accepted, or when the user directly authorizes planning from a sufficiently clear objective. The output is an executable orchestration plan artifact.

## Plan Artifact Contract

Plan artifacts live at:

```text
.plans/<unix-timestamp>-slug.md
```

Plan frontmatter:

```yaml
---
artifact_type: plan
schema_version: 2
id: <unix-timestamp>-slug
title: <human title>
status: draft | approved | executing | blocked | complete | superseded
created_at: <iso timestamp>
updated_at: <iso timestamp>
proposal: ../.proposals/<unix-timestamp>-slug.md | direct-user-request
state_dir: ../.state/<plan_slug>/
active_step: null | <step-id>
---
```

## Required Plan Sections

```md
# Plan: <title>

## Objective
## Proposal Summary
## Inputs
## Constraints
## Execution Strategy
## Delegation Map
## Dependency Graph
## Parallel Groups
## Step List
## State Initialization
## Verification Gates
## Embedded Quality Check
## Rollback / Recovery
## Final Report Contract
```

## Orchestrator-Aware Step Contract

Every executable step must be a delegation unit with:

- stable step id,
- dependencies expressed as step ids,
- parallel group,
- worker family and exact size,
- skill to load or `none`,
- minimum capable tier,
- orchestrator context package,
- expected output,
- state file path,
- acceptance criteria,
- verification method,
- recovery notes.

Recommended step shape:

```md
### Step 01: <small unit of work>

- Step ID: `01-step-slug`
- Depends on: []
- Parallel group: A
- Worker: `coding-xs | coding-sm | analysis-sm | doc-writer-md | generic-sm | ...`
- Skill: none | proposal | plan | lesson-writer | review-work | retro
- Minimum capable tier: xs | sm | md | lg | xl
- Orchestrator context package:
  - User requirement slice:
  - Relevant proposal/plan sections:
  - Relevant state files to read:
  - Files in scope:
  - Files out of scope:
  - Expected return format:
- Objective:
- Expected output:
- State updates:
- Acceptance criteria:
- Verification:
- Recovery:
```

## Worker Routing And Sizing

Use current sized worker families only:

| Work Type | Worker Family | Sizing Guidance |
| --- | --- | --- |
| Local discovery and inventory | `generic-*` | xs/sm for small scope; md for broader multi-file audits |
| Local synthesis and tradeoff analysis | `analysis-*` or `generic-*` | choose by reasoning depth |
| Critique and quality checks | `analysis-*` | sm for bounded checks; md/lg for higher risk |
| File edits and validation commands | `coding-*` | xs for tiny edits; sm/md for larger or riskier edits |
| Skill, prompt, command, and documentation prose | `doc-writer-*` | xs for tiny patches; sm/md for larger artifacts |
| External research | `websearch-*` | use only when current external evidence is required |
| Visual, screenshot, diagram, or PDF analysis | `multimodal-looker` | use only for visual/PDF/image work |

Choose the smallest capable tier for each independent step. The goal is not to force every task to `xs` or `sm`; the goal is to split independent work so each piece can use the cheapest reliable worker. A step is too large if it bundles independent files, unrelated skills, unrelated context, or mixed complexity levels that could be delegated separately.

## Dependency Graph And Parallelization

- Represent dependencies by step id.
- Steps with no dependency relationship may run concurrently.
- Steps that write the same file, mutate the same state record, or require another step's output must be serialized.
- Parallel groups should make safe concurrency obvious to the orchestrator.

## State Initialization

Each approved or executing plan must define:

```text
.state/<plan_slug>/
  metadata.json
  MAIN.md
  01-step-slug.md
  02-step-slug.md
  ...
```

`metadata.json` tracks plan path, proposal path, status, active step, steps, dependency graph, parallel groups, blockers, and latest verification. `MAIN.md` is the human-readable dashboard. Each step file records objective, inputs, context package, delegation, work log, outputs, verification, blockers, and next action.

The orchestrator owns `metadata.json` and `MAIN.md`. Workers may write only explicitly assigned step files. After worker updates, the orchestrator reconciles state.

## Embedded Quality Check

Plans must include a quality check performed by an appropriately sized `analysis-*` worker. The check is recorded in the plan or plan state and must validate step granularity, worker routing, dependency graph correctness, state initialization, verification gates, and recovery.

## Rules

- Do not implement changes while using this skill.
- Do not delegate vague work; rewrite vague steps until they are executable.
- Do not create separate review artifacts.
- Do not write new artifacts outside `.proposals/`, `.plans/`, `.state/`, or `.lessons/` unless explicitly authorized.
- Include validation gates for JSON, markdown frontmatter, skill naming, command frontmatter, worker availability, and artifact paths when relevant.
- Include rollback and recovery even for small changes.
