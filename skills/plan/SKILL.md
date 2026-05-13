---
name: plan
description: Convert an accepted proposal into a concrete orchestration runbook with phases, delegation, parallelization, validation, and recovery.
---

# Plan Skill

Use this skill after a proposal is accepted. Planning requires an accepted proposal artifact (.proposals/<timestamp>-<slug>.md with status: accepted). Direct planning from raw user requests is not supported.

## Plan Artifact Contract

Plan artifacts live at:

```text
.plans/<unix-timestamp>-slug.json
```

The artifact is a pure JSON file whose structure is defined by `skills/plan/schema.json` — the **source of truth** for plan validity. A complete example/template is at `skills/plan/templates/plan.json`.

Validate plan JSON syntax and schema conformance with:

```text
uv run --project scripts/python validate-json <plan-file> --schema skills/plan/schema.json
```

New JSON plans use `schema_version: 3`.

> **Historical note:** Prior plans used `.yaml` format with `skills/plan/schema.yaml` and `skills/plan/templates/plan.yaml`. Those files remain in the repository for archival reference but **new plans must use the JSON format**. The YAML validator (`validate-yaml`) is still available for reviewing legacy plans.

Planning requires an accepted proposal artifact at `.proposals/<unix-timestamp>-<slug>.md`. The `proposal` field in the plan artifact must point to a valid accepted proposal path. Direct-user-request planning is not supported.

## Required JSON Plan Keys

Every plan artifact must include the following top-level keys, as defined by `skills/plan/schema.json`:

| Key | Type | Description |
| --- | --- | --- |
| `artifact_type` | `"plan"` (const) | Discriminator for plan artifacts |
| `schema_version` | `3` (const) | Version for migration tracking |
| `id` | string | `<unix-timestamp>-slug` unique identifier |
| `title` | string | Human-readable title |
| `status` | enum | `draft` / `approved` / `executing` / `blocked` / `complete` / `superseded` |
| `created_at` | ISO 8601 datetime | Creation timestamp |
| `updated_at` | ISO 8601 datetime | Last-updated timestamp |
| `proposal` | path | Path to the accepted proposal artifact. Planning hard-blocked without one. |
| `state_dir` | path | Relative path to `.state/<plan_slug>/` |
| `active_step` | step ID or `null` | Current executing step |
| `objective` | string | Clear statement of what this plan accomplishes |
| `proposal_summary` | string | Brief summary of the accepted proposal |
| `inputs` | array of strings | Input resources and file paths |
| `constraints` | array of strings | Constraints affecting plan execution |
| `execution_strategy` | string | High-level execution approach |
| `delegation_map` | object | Maps workflow roles to worker family+size strings |
| `steps` | array of objects | Execution step definitions (see step contract below) |
| `dependency_graph` | object | Step dependency map (ID → array of dependency IDs) |
| `parallel_groups` | object | Group identifier → array of step IDs |
| `state_initialization` | object | Expected `.state/<plan_slug>/` structure |
| `verification_gates` | array of objects | Named gates with criteria lists |
| `embedded_quality_check` | object | Quality check performed_by, findings, and status |
| `rollback_recovery` | string | Steps to undo or recover from execution |
| `final_report_contract` | string | What the final report must include |

These keys are required by `skills/plan/schema.json`. `templates/plan.json` demonstrates all keys with realistic values. Additional keys are not permitted (`additionalProperties: false` in the schema).

## Proposal Intake Validation

The plan skill must validate that the proposal artifact exists and has an `accepted` status before creating an executable plan. This hard-blocker ensures that planning always starts from a valid, agreed-upon decision artifact.

The plan skill should:
1. Verify the proposal path exists and is a valid `.proposals/<timestamp>-<slug>.md` file
2. Check that the proposal has `status: accepted` in its frontmatter
3. Extract key information from the proposal:
   - Objective (from proposal's goal section)
   - Constraints (from proposal's constraints section)
   - Decisions (from proposal's accepted decisions section)
   - Risks (from proposal's risks section)
   - Acceptance criteria (from proposal's acceptance criteria section)

## Planning Analysis Phase

The planning skill must perform an analysis-first workflow that decomposes the accepted proposal into executable steps:

1. **Problem breakdown** - Identify the core problem or objective from the proposal
2. **Workstream identification** - Break the problem into distinct workstreams or sub-tasks
3. **Skill mapping** - Map each workstream to appropriate skills based on the proposal's suggested delegation
4. **Worker family/size mapping** - Assign appropriate worker families and sizes to each workstream
5. **Dependency analysis** - Determine step dependencies based on workstream relationships
6. **Parallelization analysis** - Identify which steps can run concurrently
7. **File/state/artifact impact analysis** - Determine what files, state, and artifacts will be affected
8. **Delegation packet inventory** - List any delegation packets needed for complex steps

This analysis should be documented in the optional `planning_analysis` field of the plan artifact, which helps trace how the plan was derived from the proposal.

## Orchestrator-Aware Step Contract

Every step in the `steps` array is a JSON object with the following required keys (defined in `skills/plan/schema.json`):

| Key | Type | Description |
| --- | --- | --- |
| `id` | string | Unique step identifier (`01-step-slug` format) |
| `depends_on` | array of strings | Step IDs this step depends on |
| `parallel_group` | string | Group identifier for concurrency control |
| `worker` | object | `{family, size}` — worker family and tier |
| `skill` | string or null | Skill to load (lowercase-hyphenated name) or `null`. Runtime validates skill existence. |
| `minimum_capable_tier` | string | Minimum worker tier (xs/sm/md/lg/xl) |
| `context_package` | object | User requirement slice, relevant sections, files in/out scope, expected return format |
| `objective` | string | Bounded objective for this step |
| `expected_output` | string | What this step should produce |
| `state_updates` | array of strings | State files this step updates (use `.json` paths) |
| `acceptance_criteria` | array of strings | Success criteria |
| `verification` | string | How to verify this step |
| `recovery` | string | What to do if this step fails |

Recommended step shape:

```json
{
  "id": "01-step-slug",
  "depends_on": [],
  "parallel_group": "A",
  "worker": {
    "family": "generic",
    "size": "sm"
  },
  "skill": null,
  "minimum_capable_tier": "sm",
  "context_package": {
    "user_requirement_slice": "Slice of user requirements relevant to this step",
    "relevant_proposal_sections": ["Goal"],
    "relevant_state_files": [],
    "files_in_scope": ["path/to/target/files"],
    "files_out_scope": ["node_modules/"],
    "expected_return_format": "Findings as structured text"
  },
  "objective": "Bounded objective for this step",
  "expected_output": "What this step should produce",
  "state_updates": ["../.state/<plan_slug>/01-step-slug.json"],
  "acceptance_criteria": ["Criterion one", "Criterion two"],
  "verification": "How to verify this step",
  "recovery": "What to do if this step fails"
}
```

See `skills/plan/templates/plan.json` for a complete multi-step example. See `skills/plan/schema.json` for exact type, enum, and pattern constraints on every field.

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

## Context Examples By Worker Size

| Size | Good fit | Context package shape | Avoid |
| --- | --- | --- | --- |
| `xs` | Supplied-context checks, extraction, naming, tiny summaries | Exact input, exact expected output, no open-ended discovery | Broad search, ambiguous judgment, file edits |
| `sm` | Bounded synthesis, simple comparisons, narrow discovery | Short file list, concrete acceptance criteria, small state update | Multi-file refactors, architecture decisions |
| `md` | Multi-file investigation, moderate implementation, schema/template edits | Proposal slice, relevant state files, file scope, validation commands | Vague objectives or unbounded repository changes |
| `lg` | Architecture-sensitive analysis, complex implementation, embedded review | Detailed rationale, risks, alternatives, explicit pass/fail criteria | Mechanical edits that can be sliced smaller |
| `xl` | Highest-risk judgment, conflicting evidence, expensive failure cases | Complete decision context, known conflicts, expected judgment standard | Routine drafting, small fixes, or work better split across smaller workers |

## Delegation Packets

Use delegation packets when a step has enough context that inline `context_package` fields are insufficient. The canonical packet template is:

```text
skills/delegation/templates/delegation-packet.md
```

The plan template reference is:

```text
skills/plan/templates/delegation-packet.md
```

Delegation packets are OpenCode-specific. They should name the target worker, optional skill, objective, files in and out of scope, expected return format, assigned state updates, result-consumption convention, verification, and recovery/escalation. Load the `delegation` skill when constructing or consuming non-trivial worker packets.

## Dependency Graph And Parallelization

The `dependency_graph` key maps each step ID to an array of step IDs it depends on. Steps with no dependency relationship may run concurrently. Steps that write the same file, mutate the same state record, or require another step's output must be serialized.

The `parallel_groups` key maps group identifiers to step ID arrays, making safe concurrency obvious to the orchestrator.

## State Initialization

Each approved or executing plan must have a `.state/<plan_slug>/` directory with the following files:

```text
.state/<plan_slug>/
  metadata.json       # Orchestrator-owned plan metadata (schema: skills/plan/schemas/state-metadata.schema.json)
  MAIN.json           # Orchestrator-owned human-readable dashboard (schema: skills/plan/schemas/state-main.schema.json)
  01-step-slug.json   # Step-owned state file (schema: skills/plan/schemas/state-step.schema.json)
  02-step-slug.json   # Step-owned state file
  ...
```

### Automatic Initialization (Preferred)

After creating a valid plan JSON artifact at `.plans/<plan_slug>.json`, run the state initializer script:

```text
uv run --project scripts/python init-plan-state <plan.json>
```

The script:
1. Validates the plan JSON against `skills/plan/schema.json`.
2. Creates the `.state/<plan_slug>/` directory and fails safely if that directory already contains files.
3. Seeds `metadata.json`, `MAIN.json`, and step `.json` files from the plan definition.
4. Validates each generated file against the corresponding state JSON schema.

Example:

```text
uv run --project scripts/python init-plan-state .plans/1778710681-example-plan.json
```

### Manual Initialization (Fallback)

If the initialization script is unavailable, manually create the files:

- **`metadata.json`** — follows `skills/plan/schemas/state-metadata.schema.json`. Tracks plan path (pointing to `.plans/<plan_slug>.json`), proposal path, status, active step, step statuses, dependency graph, parallel groups, blockers, and latest verification. Validate with: `uv run --project scripts/python validate-json <file> --schema skills/plan/schemas/state-metadata.schema.json`

- **`MAIN.json`** — follows `skills/plan/schemas/state-main.schema.json`. Human-readable dashboard with plan_id, title, objective, status, active step, step_statuses, blockers, latest verification, and worker_assignments. Validate with: `uv run --project scripts/python validate-json <file> --schema skills/plan/schemas/state-main.schema.json`

- **Step files** (`<step-id>.json`) — follow `skills/plan/schemas/state-step.schema.json`. Each records step_id, status, objective, inputs, context_summary, work_log, outputs, verification, blockers, next_action, worker, timestamps, and findings. Validate with: `uv run --project scripts/python validate-json <file> --schema skills/plan/schemas/state-step.schema.json`

### Ownership

The orchestrator owns `metadata.json` and `MAIN.json`. Workers may write only explicitly assigned step `.json` files. After worker updates, the orchestrator reconciles `metadata.json` and `MAIN.json` to reflect the new step status.

## Embedded Quality Check

Plans must include a quality check performed by an appropriately sized `analysis-*` worker. The check is recorded in the plan's `embedded_quality_check` key and must validate step granularity, worker routing, dependency graph correctness, state initialization, verification gates, and recovery.

## Rules

- Do not implement changes while using this skill.
- Do not delegate vague work; rewrite vague steps until they are executable.
- Do not create separate review artifacts.
- Do not write new artifacts outside `.proposals/`, `.plans/`, `.state/`, or `.lessons/` unless explicitly authorized.
- Validate every plan artifact against `skills/plan/schema.json` — the schema is the source of truth for required keys, types, enums, patterns, and constraints. Use `uv run --project scripts/python validate-json <plan-file> --schema skills/plan/schema.json` for schema conformance.
- Validate state files (`metadata.json`, `MAIN.json`, step `.json` files) against the corresponding schemas in `skills/plan/schemas/`. The initialization script (`init-plan-state`) runs these checks automatically.
- Include validation gates for JSON structure, schema conformance, worker availability, step dependency correctness, and artifact paths when relevant.
- Include rollback and recovery even for small changes.
