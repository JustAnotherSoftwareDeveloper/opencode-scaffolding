---
name: plan
description: Create directory-based markdown engineering plans from accepted proposals. Use when a proposal has been accepted and an execution blueprint is needed. Plans are directory workspace artifacts centered on INDEX.md.
---

# Plan Skill

Use this skill after a proposal is accepted. Planning requires an accepted proposal artifact: prefer a proposal workspace at `.proposals/<timestamp>-<slug>/INDEX.md` with accepted status in `metadata.md`; historical single-file `.proposals/<timestamp>-<slug>.md` artifacts remain readable but must not be migrated. Direct planning from raw user requests is not supported.

**This skill does not implement changes.** It produces a markdown plan artifact. Non-trivial execution proceeds by loading the **runbook** skill after the plan is approved.

## Plan Artifact Contract

Plan artifacts are now directory workspace artifacts:

```text
.plans/<unix-timestamp>-<slug>/INDEX.md
```

Each plan is a **human-readable markdown workspace** — not a JSON executable. It serves as the complete engineering specification that a runbook skill uses to drive execution. Legacy single-file `.plans/*.md` support is not required for this workflow.

The `INDEX.md` file is mandatory. Supporting markdown files are optional and may be added based on complexity when they make the plan easier to review or execute.

### Frontmatter

Every plan markdown file starts with YAML frontmatter:

```yaml
---
id: <unix-timestamp>-<slug>
title: "<Human-readable title>"
status: draft  # draft | approved | superseded
created_at: "<ISO 8601 timestamp>"
updated_at: "<ISO 8601 timestamp>"
proposal: ".proposals/<timestamp>-<proposal-slug>/INDEX.md"
---
```

### Required Sections

The `INDEX.md` file must contain each of these sections. Sections that are not yet filled should state "TBD" rather than being omitted.

| Section | Purpose |
| --- | --- |
| **Goal** | Clear statement of what this plan accomplishes |
| **Non-Goals** | What this plan explicitly does NOT address |
| **Source Proposal** | Link to the accepted proposal and summary of its key decisions |
| **Accepted Decisions** | Record of decisions made during planning itself (worker routing, sequencing, skill selection) |
| **Workspace Contents** | Structure of the plan directory, including all files and subdirectories |
| **Current State Summary** | Summary of relevant existing artifacts, configuration, and context |
| **Design** | Architectural or structural changes the plan will produce |
| **Implementation Strategy** | Phases, ordering, and high-level execution approach |
| **Skill/File Routing Summary** | Mapping of files to skills and workers, including routing logic |
| **Artifact Impact** | Files and directories that will be created, modified, or deleted |
| **Validation** | How correctness will be verified (tests, linting, schema validation, manual review) |
| **Rollback / Recovery** | Steps to undo or recover if execution fails partway through |
| **Acceptance Criteria** | Concrete, verifiable conditions that define plan completion |
| **Runbook Generation Handoff** | Guidance for the runbook skill: worker sizing, skill dependencies, serial sequencing requirements, and step boundaries |

#### Section Detail

**Goal** — One or two sentences. Derive from the proposal's goal. Example: "Migrate the proposal skill from YAML to markdown artifacts while preserving the frontmatter contract and validation pipeline."

**Non-Goals** — Bullet list of things the plan explicitly leaves out. Example: "- No changes to the runbook skill. - No changes to existing proposal markdown files."

**Source Proposal** — Link to `.proposals/<timestamp>-<slug>/INDEX.md` for proposal workspaces, or to a historical `.proposals/<timestamp>-<slug>.md` artifact when planning from an existing legacy proposal. Summarize the accepted decisions that drive this plan.

**Accepted Decisions** — Planning-level decisions: which phase ordering is required, which worker families to use, which skills to load per phase, and any serial sequencing constraints. Record these so the runbook does not have to rediscover them.

**Workspace Contents** — File tree structure of the plan directory, including all files and subdirectories. Example:

```
.plans/1780404291-directory-plan-skill-upgrade/
├── INDEX.md
├── context.md
├── skill-map.md
├── validation.md
└── runbook-handoff.md
```

**Current State Summary** — Summary of relevant existing artifacts, configuration, and context. Focus on high-level context rather than exhaustive inventory.

**Design** — The "what" of the change. For a schema change: the new shapes, removed fields, migration notes. For a skill rewrite: the new prompt structure, contract, and lifecycle. Include diagrams or pseudo-code where helpful.

**Implementation Strategy** — The "how" broken into coarse phases. Each phase lists the files it will touch, the skill guidance it will need, and the validation it must pass. Example:

```
Phase 1: Rewrite plan skill contract — touches `skills/plan/SKILL.md`; use `skill-hygiene` only if frontmatter or local skill framework metadata changes; otherwise use documentation-mode instructions.
Phase 2: Add plan workspace templates — touches `skills/plan/templates/plan-workspace/*.md`; use documentation-mode instructions and keep templates non-executable.
Phase 3: Update lifecycle references — touches prompts or commands found by inventory; use focused harness documentation-editing instructions.
```

**Skill/File Routing Summary** — Mapping of files or workstreams to skills and how to use them. Defer worker sizing to the `delegation` skill during runbook execution: there is a single text worker (`worker-md`) plus optional visual exception support via `multimodal-looker`.

| File / Workstream | Skill | How to use it | Do not use it for |
| --- | --- | --- | --- |
| `skills/plan/SKILL.md` | `skill-hygiene` when frontmatter or skill framework metadata changes | Check name/description/class hygiene and keep the skill concise. | Do not redesign unrelated skills. |
| Plan workspace templates | none, or `skill-hygiene` for framework-sensitive template conventions | Create markdown examples that teach the plan contract. | Do not create executable runbook templates. |
| Runbook handoff | `delegation` during execution | Select the appropriate worker (`worker-md`) for each atomic unit. | Do not hardcode static worker tiers in the plan. |
| Embedded review | `review-work` | Review changed artifacts for prompt quality, scope, permission safety, and missing verification. | Do not turn review into new implementation scope. |

**Artifact Impact** — Table of files with create/modify/delete action:

| File | Action |
| --- | --- |
| `skills/plan/SKILL.md` | modify |
| `skills/plan/templates/plan-workspace/INDEX.md` | create |
| `skills/plan/templates/plan-workspace/skill-map.md` | create if needed |

**Validation** — Concrete commands or procedures. Example: "Search changed files for `.plans/*.md` — active current/future plan instructions must not use the legacy single-file shape. Grep new `SKILL.md` for `init-plan-state` — must find zero matches."

**Rollback / Recovery** — For each file deletion or modification, describe how to undo it. Example: "Restore the previous plan skill contract from git: `git checkout HEAD -- skills/plan/SKILL.md`."

**Acceptance Criteria** — Bullet list of pass/fail conditions, each objectively verifiable.

**Runbook Generation Handoff** — Notes for the runbook skill: work types, dependency ordering, serial sequencing requirements, skill loading instructions, and context packages. This section is consumed by the runbook skill, not by workers directly. Example:

```
- Phase 1: rewrite `skills/plan/SKILL.md`; work type documentation; load `skill-hygiene` only if metadata changes.
- Phase 2: create plan workspace templates; work type documentation; no executable artifacts.
- Phase 3: update path references; work type documentation/config-safe editing; inventory determines file scope.
- Load `delegation` during runbook execution to choose worker sizes for each atomic unit.
```

## Proposal Intake

Before creating a plan, the skill must:

1. Verify the proposal path exists and is either a valid `.proposals/<timestamp>-<slug>/INDEX.md` workspace entry point or a historical `.proposals/<timestamp>-<slug>.md` file.
2. Check that the proposal has `status: accepted` in workspace `metadata.md` or historical file frontmatter.
3. Extract key information from the proposal:
   - Goal → plan **Goal**
   - Non-Goals → plan **Non-Goals**
   - Accepted decisions → plan **Accepted Decisions**
   - Constraints → inform **Implementation Strategy**
   - Risks → inform **Rollback / Recovery**
   - Acceptance criteria → feed into **Acceptance Criteria**

## Authoring Standard

Plans must follow senior-dev-to-intern authoring standard:

- Write so a competent intern can execute the plan with minimal supervision.
- Include concrete examples for every required section.
- Specify exact file paths, command syntax, and expected outputs.
- Avoid vague terms like "various", "some", or "several" — use specific counts or lists.
- For worker sizing in runbook handoff, use dynamic sizing via the delegation skill rather than hardcoding static sizes.

## Rules

- Do not implement changes while using this skill.
- Do not create `.plans/*.json` executable artifacts.
- Do not reference `schema_version`, `init-plan-state`, or plan state schemas — these were removed from the plan skill in the plan-runbook-lifecycle change (May 2026).
- Do not delegate vague work; rewrite vague sections until a worker could execute them.
- Do not create separate review artifacts.
- Do not write new artifacts outside `.proposals/`, `.plans/`, or `.lessons/` unless explicitly authorized.
- For non-trivial execution routing, load the **runbook** skill after the plan is approved.
- Include validation gates, rollback and recovery even for small changes.
- Use **skill-hygiene** for skill metadata and frontmatter changes.
- Use **review-work** for reviewing completed work.
- Use **delegation** for dynamic worker sizing and task routing during runbook execution.
- Use **runbook** skill only after plan approval and validation.
