---
name: plan
description: Convert an accepted proposal into a concrete orchestration runbook with phases, delegation, parallelization, validation, and recovery.
---

# Plan Skill

Use this skill after a proposal is accepted, or when the user directly authorizes planning from a sufficiently clear objective. The output is an executable orchestration plan artifact in structured YAML format.

## Plan Artifact Contract

Plan artifacts live at:

```text
.plans/<unix-timestamp>-slug.yaml
```

The artifact is a pure YAML file (no markdown body or separate frontmatter) whose structure is defined by `skills/plan/schema.yaml` — the **source of truth** for plan validity. A separate example/template is at `skills/plan/templates/plan.yaml`.

New YAML plans use `schema_version: 3`.

Proposal paths remain `.proposals/*.md` (markdown files). The proposal field may also be `direct-user-request` when no proposal exists.

## Required YAML Plan Keys

Every plan artifact must include the following top-level keys, as defined by `skills/plan/schema.yaml`:

| Key | Type | Description |
| --- | --- | --- |
| `artifact_type` | `"plan"` (const) | Discriminator for plan artifacts |
| `schema_version` | `3` (const) | Version for migration tracking |
| `id` | string | `<unix-timestamp>-slug` unique identifier |
| `title` | string | Human-readable title |
| `status` | enum | `draft` / `approved` / `executing` / `blocked` / `complete` / `superseded` |
| `created_at` | ISO 8601 datetime | Creation timestamp |
| `updated_at` | ISO 8601 datetime | Last-updated timestamp |
| `proposal` | path or `"direct-user-request"` | Path to the accepted proposal or `direct-user-request` |
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

These keys are required by `skills/plan/schema.yaml`. `templates/plan.yaml` demonstrates all keys with realistic values. Additional keys are not permitted (`additionalProperties: false` in the schema).

## Orchestrator-Aware Step Contract

Every step in the `steps` array is a YAML object with the following required keys (defined in `skills/plan/schema.yaml`):

| Key | Type | Description |
| --- | --- | --- |
| `id` | string | Unique step identifier (`01-step-slug` format) |
| `depends_on` | array of strings | Step IDs this step depends on |
| `parallel_group` | string | Group identifier for concurrency control |
| `worker` | object | `{family, size}` — worker family and tier |
| `skill` | string or null | Skill to load or `null` |
| `minimum_capable_tier` | string | Minimum worker tier (xs/sm/md/lg/xl) |
| `context_package` | object | User requirement slice, relevant sections, files in/out scope, expected return format |
| `objective` | string | Bounded objective for this step |
| `expected_output` | string | What this step should produce |
| `state_updates` | array of strings | State files this step updates |
| `acceptance_criteria` | array of strings | Success criteria |
| `verification` | string | How to verify this step |
| `recovery` | string | What to do if this step fails |

Recommended step shape:

```yaml
- id: "01-step-slug"
  depends_on: []
  parallel_group: A
  worker:
    family: generic    # one of: generic, analysis, coding, doc-writer, websearch, multimodal-looker
    size: sm           # one of: xs, sm, md, lg, xl
  skill: null          # or: proposal, plan, lesson-writer, review-work, retro
  minimum_capable_tier: sm
  context_package:
    user_requirement_slice: "Slice of user requirements relevant to this step"
    relevant_proposal_sections:
      - "Goal"
    relevant_state_files: []
    files_in_scope:
      - "path/to/target/files"
    files_out_scope:
      - "node_modules/"
    expected_return_format: "Findings as structured text"
  objective: "Bounded objective for this step"
  expected_output: "What this step should produce"
  state_updates:
    - ".state/<plan_slug>/01-step-slug.md"
  acceptance_criteria:
    - "Criterion one"
    - "Criterion two"
  verification: "How to verify this step"
  recovery: "What to do if this step fails"
```

See `skills/plan/templates/plan.yaml` for a complete multi-step example. See `skills/plan/schema.yaml` for exact type, enum, and pattern constraints on every field.

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

The `dependency_graph` key maps each step ID to an array of step IDs it depends on. Steps with no dependency relationship may run concurrently. Steps that write the same file, mutate the same state record, or require another step's output must be serialized.

The `parallel_groups` key maps group identifiers to step ID arrays, making safe concurrency obvious to the orchestrator.

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

`metadata.json` tracks plan path (pointing to `.plans/<plan_slug>.yaml`), proposal path, status, active step, steps, dependency graph, parallel groups, blockers, and latest verification. `MAIN.md` is the human-readable dashboard. Each step file records objective, inputs, context package, delegation, work log, outputs, verification, blockers, and next action.

The orchestrator owns `metadata.json` and `MAIN.md`. Workers may write only explicitly assigned step files. After worker updates, the orchestrator reconciles state.

## Embedded Quality Check

Plans must include a quality check performed by an appropriately sized `analysis-*` worker. The check is recorded in the plan's `embedded_quality_check` key and must validate step granularity, worker routing, dependency graph correctness, state initialization, verification gates, and recovery.

## Rules

- Do not implement changes while using this skill.
- Do not delegate vague work; rewrite vague steps until they are executable.
- Do not create separate review artifacts.
- Do not write new artifacts outside `.proposals/`, `.plans/`, `.state/`, or `.lessons/` unless explicitly authorized.
- Validate every plan artifact against `skills/plan/schema.yaml` — the schema is the source of truth for required keys, types, enums, patterns, and constraints.
- Include validation gates for YAML structure, schema conformance, worker availability, step dependency correctness, and artifact paths when relevant.
- Include rollback and recovery even for small changes.
