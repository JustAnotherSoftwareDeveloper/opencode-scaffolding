---
name: plan
description: Create human-readable markdown engineering plans from accepted proposals. Use when a proposal has been accepted and an execution blueprint is needed.
---

# Plan Skill

Use this skill after a proposal is accepted. Planning requires an accepted proposal artifact (`.proposals/<timestamp>-<slug>.md` with `status: accepted`). Direct planning from raw user requests is not supported.

**This skill does not implement changes.** It produces a markdown plan artifact. Non-trivial execution proceeds by loading the **runbook** skill after the plan is approved.

## Plan Artifact Contract

Plan artifacts live at:

```text
.plans/<unix-timestamp>-<slug>.md
```

Each plan is a **human-readable markdown file** — not a JSON executable. It serves as the complete engineering specification that a runbook skill uses to drive execution.

### Frontmatter

Every plan markdown file starts with YAML frontmatter:

```yaml
---
id: <unix-timestamp>-<slug>
title: "<Human-readable title>"
status: draft  # draft | approved | superseded
created_at: "<ISO 8601 timestamp>"
updated_at: "<ISO 8601 timestamp>"
proposal: ".proposals/<timestamp>-<proposal-slug>.md"
---
```

### Required Sections

The plan body must contain each of these sections. Sections that are not yet filled should state "TBD" rather than being omitted.

| Section | Purpose |
| --- | --- |
| **Goal** | Clear statement of what this plan accomplishes |
| **Non-Goals** | What this plan explicitly does NOT address |
| **Source Proposal** | Link to the accepted proposal and summary of its key decisions |
| **Accepted Decisions** | Record of decisions made during planning itself (worker routing, sequencing, skill selection) |
| **Current State** | Inventory of relevant existing files, artifacts, and configuration |
| **Design** | Architectural or structural changes the plan will produce |
| **Implementation Strategy** | Phases, ordering, and high-level execution approach |
| **Artifact Impact** | Files and directories that will be created, modified, or deleted |
| **Validation** | How correctness will be verified (tests, linting, schema validation, manual review) |
| **Rollback / Recovery** | Steps to undo or recover if execution fails partway through |
| **Acceptance Criteria** | Concrete, verifiable conditions that define plan completion |
| **Runbook Generation** | Guidance for the runbook skill: worker sizing, skill dependencies, parallelization opportunities, and step boundaries |

#### Section Detail

**Goal** — One or two sentences. Derive from the proposal's goal. Example: "Migrate the proposal skill from YAML to markdown artifacts while preserving the frontmatter contract and validation pipeline."

**Non-Goals** — Bullet list of things the plan explicitly leaves out. Example: "- No changes to the runbook skill. - No changes to existing proposal markdown files."

**Source Proposal** — Link: `.proposals/<timestamp>-<slug>.md`. Summarize the accepted decisions that drive this plan.

**Accepted Decisions** — Planning-level decisions: which phases run in parallel, which worker families to use, which skills to load per phase, any ordering constraints. Record these so the runbook does not have to rediscover them.

**Current State** — File tree, relevant config snippets, existing schema keys, dependency versions. Enough that a worker can orient without browsing the entire repository.

**Design** — The "what" of the change. For a schema change: the new shapes, removed fields, migration notes. For a skill rewrite: the new prompt structure, contract, and lifecycle. Include diagrams or pseudo-code where helpful.

**Implementation Strategy** — The "how" broken into coarse phases. Each phase lists the files it will touch and the skills it will need. Example:

```
Phase 1: Rewrite SKILL.md — touches skills/plan/SKILL.md, needs doc-writer worker.
Phase 2: Delete old schemas — touches skills/plan/schema.json, skills/plan/schemas/*.json.
Phase 3: Update templates — touches skills/plan/templates/delegation-packet.md.
```

**Artifact Impact** — Table of files with create/modify/delete action:

| File | Action |
| --- | --- |
| `skills/plan/SKILL.md` | modify |
| `skills/plan/schema.json` | delete |
| `skills/plan/schemas/*.json` | delete |

**Validation** — Concrete commands or procedures. Example: "Run `ls skills/plan/schema.json` — must report 'No such file'. Grep new `SKILL.md` for 'init-plan-state' — must find zero matches."

**Rollback / Recovery** — For each file deletion or modification, describe how to undo it. Example: "Restore deleted schemas from git: `git checkout HEAD -- skills/plan/schema.json`."

**Acceptance Criteria** — Bullet list of pass/fail conditions, each objectively verifiable.

**Runbook Generation** — Notes for the runbook skill: preferred worker sizes, parallel groups, dependency ordering, skill loading instructions. This section is consumed by the runbook skill, not by workers directly. Example:

```
- Phase 1 (doc-writer, size sm): rewrite SKILL.md
- Phase 2 (bash, size xs): delete schema.json and state schemas
- Phases 1 and 2 are serial (Phase 2 depends on Phase 1)
- Load lesson-writer after all phases complete
```

## Proposal Intake

Before creating a plan, the skill must:

1. Verify the proposal path exists and is a valid `.proposals/<timestamp>-<slug>.md` file.
2. Check that the proposal has `status: accepted` in its frontmatter.
3. Extract key information from the proposal:
   - Goal → plan **Goal**
   - Non-Goals → plan **Non-Goals**
   - Accepted decisions → plan **Accepted Decisions**
   - Constraints → inform **Implementation Strategy**
   - Risks → inform **Rollback / Recovery**
   - Acceptance criteria → feed into **Acceptance Criteria**

## Rules

- Do not implement changes while using this skill.
- Do not create `.plans/*.json` executable artifacts.
- Do not reference `schema_version`, `init-plan-state`, `skills/plan/schema.json`, or plan state schemas — these were removed from the plan skill in the plan-runbook-lifecycle change (May 2026).
- Do not delegate vague work; rewrite vague sections until a worker could execute them.
- Do not create separate review artifacts.
- Do not write new artifacts outside `.proposals/`, `.plans/`, or `.lessons/` unless explicitly authorized.
- For non-trivial execution routing, load the **runbook** skill after the plan is approved.
- Include validation gates, rollback and recovery even for small changes.
