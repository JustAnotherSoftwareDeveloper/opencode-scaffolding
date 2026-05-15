---
name: runbook
description: Generate executable runbook directory workspaces from approved markdown plans. Use for .runbooks/<id>/main.toon (v2 default) or .runbooks/<id>/runbook.json (v1 legacy) creation, validation, state initialization, and runbook-driven execution handoff.
---

# Runbook Skill

Use this skill after a markdown plan has been approved and before execution begins. The runbook is the machine-readable execution contract for orchestrators and workers.

This skill does **not** implement the requested changes directly. It converts an approved human engineering plan into an executable runbook workspace, validates that workspace, and prepares it for runbook-keyed state initialization.

## Artifact Contract (v2 Default)

Runbook workspaces follow the **v2 TOON format** by default:

```text
.runbooks/<unix-timestamp>-slug/
  main.toon              # required: runbook manifest with steps index
  steps/
    01-<step-slug>.toon  # required per step: full step definition
    02-<step-slug>.toon
    ...
```

The primary manifest is `main.toon`. Each step is defined in its own file under `steps/`, referenced by the `steps` index array in `main.toon`.

### v2 Step Index Shape

The `steps` array in `main.toon` contains objects with:

| Field   | Required | Description                                                      |
|---------|----------|------------------------------------------------------------------|
| `id`    | yes      | Step identifier matching the step filename stem (e.g. `01-test`) |
| `file`  | yes      | Relative path to the step file, must be `steps/<step-id>.toon`   |
| `path`  | no       | Tolerated alias for `file`; examples should use `file`           |

The loader enforces:
- `file` (or `path`) must start with `steps/` and end with `.toon`
- No parent directory traversal (`..`)
- No absolute paths
- Step filename stem must equal the step `id`

### Example: Complete `main.toon`

```yaml
artifact_type: runbook
format_version: 2
id: 1778843937-upgrade-runbooks-to-toon
title: Upgrade Runbooks to TOON Format
status: draft
created_at: 2026-05-15T00:00:00Z
updated_at: 2026-05-15T00:00:00Z
proposal: ../../.proposals/1778843937-upgrade-runbooks-to-toon.md
plan: ../../.plans/1778843937-upgrade-runbooks-to-toon.md
state_dir: ../../.state/1778843937-upgrade-runbooks-to-toon/
active_step: null
objective: Migrate the runbook skill from v1 JSON to v2 TOON workspace format
plan_summary: Convert runbook skill guidance, templates, and validation to use .runbooks/<id>/main.toon plus steps/*.toon as the default workspace layout
inputs[0]:
constraints[0]:
execution_strategy: Incremental migration with dual-format support (v2 TOON default, v1 JSON legacy)
delegation_map:
  doc-writer: doc-writer-md
  coding: coding-xl
steps[7]{id,file}:
  01-dependency-parser,steps/01-dependency-parser.toon
  02-toon-loader-invariants,steps/02-toon-loader-invariants.toon
  03-state-init-compat,steps/03-state-init-compat.toon
  04-runbook-skill-examples,steps/04-runbook-skill-examples.toon
  05-commands-prompts-review,steps/05-commands-prompts-review.toon
  06-fixtures-verification,steps/06-fixtures-verification.toon
  07-embedded-quality-review,steps/07-embedded-quality-review.toon
dependency_graph:
  01-dependency-parser[0]:
  02-toon-loader-invariants[1]: 01-dependency-parser
  03-state-init-compat[1]: 02-toon-loader-invariants
  04-runbook-skill-examples[1]: 03-state-init-compat
  05-commands-prompts-review[1]: 03-state-init-compat
  06-fixtures-verification[2]: 04-runbook-skill-examples,05-commands-prompts-review
  07-embedded-quality-review[1]: 06-fixtures-verification
parallel_groups:
  group-a[2]: 04-runbook-skill-examples,05-commands-prompts-review
state_initialization:
  metadata_schema_version: 1
  require_step_files: true
  step_file_extension: .json
  main_dashboard: MAIN.json
verification_gates[0]:
embedded_quality_check:
  performed_by: null
  findings: null
  status: pending
rollback_recovery: Revert all .runbooks/<id>/ files to previous state, remove .state/<id>/ directory
final_report_contract: Summary of all files changed, validation results per step, and any blockers encountered
```

### Example: Complete `steps/01-dependency-parser.toon`

```yaml
id: 01-dependency-parser
depends_on[0]:
parallel_group: default
worker:
  family: coding
  size: xl
skill: null
minimum_capable_tier: md
context_package:
  user_requirement_slice: Create a TOON dependency parser that understands the step index shape with id/file references
  relevant_proposal_sections[0]:
  relevant_state_files[0]:
  files_in_scope[2]: scripts/python/pyproject.toml,scripts/python/lib/runbook_toon.py
  files_out_scope[2]: skills/runbook/SKILL.md,skills/runbook/schema.json
  expected_return_format: Working dependency parser with tests, committed to repository
objective: Build the dependency parser for v2 TOON runbooks with step index support
expected_output: scripts/python/lib/runbook_toon.py with load_runbook, load_step_files, and dependency validation
state_updates[1]: .state/1778843937-upgrade-runbooks-to-toon/01-dependency-parser.json
acceptance_criteria[3]:
  - Parser loads main.toon and resolves step file references
  - Dependency cycle detection works correctly
  - Invalid step references produce clear error messages
verification: Run validate-runbook against test fixtures; all invariants must pass
recovery: Identify which fixture fails and fix the parser; rerun validation
```

## Legacy v1 Compatibility

The original v1 JSON format is preserved for backward compatibility but is **deprecated** and clearly labeled as legacy.

```text
.runbooks/<unix-timestamp>-slug/
  runbook.json           # v1 legacy: primary executable manifest (deprecated)
```

Legacy artifacts:
- **`runbook.json`** — v1 JSON manifest; validated against `schema.json`
- **`skills/runbook/schema.json`** — v1 JSON Schema; **not** used for v2 TOON validation
- **`skills/runbook/templates/runbook.json`** — v1 template; preserved for legacy use only

> **v2 runbooks do not use `schema.json`.** Validation is performed through parser-backed invariant checks (see [Invariant Validation](#invariant-validation)).

## Plan Intake Validation

Before creating a runbook, verify:

1. The plan path exists and matches `.plans/<timestamp>-slug.md`.
2. The plan is a markdown engineering specification produced by the `plan` skill.
3. The plan frontmatter has `status: approved` or the user explicitly authorizes runbook generation from its current status.
4. The plan links to an accepted proposal.
5. The plan contains enough detail to derive executable steps: objective, scope, artifact impact, implementation strategy, validation, rollback/recovery, and acceptance criteria.

If the plan is too vague to execute safely, stop and repair the plan with the `plan` skill before generating a runbook.

## Runbook Generation Workflow (v2 Default)

1. **Extract source context**
   - Proposal path and accepted decisions.
   - Plan goal, non-goals, constraints, implementation strategy, artifact impact, validation, rollback/recovery, and acceptance criteria.

2. **Derive executable steps**
   - Split plan phases into bounded runbook steps.
   - Each step should have one objective, clear file scope, expected output, acceptance criteria, verification, and recovery.
   - Keep steps small enough for the smallest capable worker tier.

3. **Build dependency graph and parallel groups**
   - Serialize steps that read/delete the same files, mutate the same state, or depend on prior outputs.
   - Parallelize independent steps only when file scopes do not conflict.

4. **Select worker guidance**
   - Load `delegation` for dynamic family/size selection.
   - Record worker hints in `delegation_map` and each step's `worker` object.
   - Do not hardcode larger workers when the task can be decomposed.

5. **Create `.runbooks/<id>/main.toon`** (v2 default)
   - Use `skills/runbook/templates/main.toon` as the starting shape if available.
   - Create step files under `.runbooks/<id>/steps/<step-id>.toon`.
   - Fill every required field in both the manifest and each step file.

6. **Validate and prepare state initialization**
   - Validate the runbook via `validate-runbook` (parser-backed invariant checks).
   - Run `init-runbook-state` only after the runbook is approved or execution is authorized.

> **For v1 legacy runbooks:** Substitute `main.toon` → `runbook.json`, use `skills/runbook/templates/runbook.json`, and validate against `schema.json`.

## Required Fields (v2 TOON)

### Manifest-level Required Fields

- `artifact_type: runbook`
- `format_version: 2`
- `id`
- `title`
- `status`
- `created_at`
- `updated_at`
- `proposal`
- `plan`
- `state_dir`
- `active_step`
- `objective`
- `plan_summary`
- `inputs`
- `constraints`
- `execution_strategy`
- `delegation_map`
- `steps` (index array with `id` + `file` references)
- `dependency_graph`
- `parallel_groups`
- `state_initialization`
- `verification_gates`
- `embedded_quality_check`
- `rollback_recovery`
- `final_report_contract`

### Step-level Required Fields

Each step file must include:

- `id`
- `depends_on`
- `parallel_group`
- `worker` (with `family` and `size`)
- `skill`
- `minimum_capable_tier`
- `context_package` (with `user_requirement_slice`, `relevant_proposal_sections`, `relevant_state_files`, `files_in_scope`, `files_out_scope`, `expected_return_format`)
- `objective`
- `expected_output`
- `state_updates`
- `acceptance_criteria`
- `verification`
- `recovery`

## Path Conventions (v2)

Because `main.toon` lives inside `.runbooks/<id>/`, relative paths must resolve from that directory:

```yaml
proposal: ../../.proposals/<proposal_id>.md
plan: ../../.plans/<plan_id>.md
state_dir: ../../.state/<runbook_id>/
```

The runbook directory name, manifest `id`, and `state_dir` runbook ID must match. `init-runbook-state` enforces this.

Step files within the workspace use paths relative to `.runbooks/<id>/`:

```yaml
steps[1]{id,file}:
  01-example,steps/01-example.toon
```

## Invariant Validation (v2)

**v2 TOON runbooks are validated through parser-backed invariant checks, not against a JSON Schema.** The `validate-runbook` command performs the following checks:

| Invariant | Description |
|-----------|-------------|
| **Path shape** | Runbook must be at `.runbooks/<id>/main.toon` |
| **ID match** | Runbook `id` must match directory name |
| **State dir** | `state_dir` must be `../../.state/<id>/` |
| **Required fields** | All required manifest and step fields present |
| **Step index** | Steps array entries have `id` and `file` (or `path`) |
| **File resolution** | Step file references start with `steps/`, end with `.toon`, no `..` |
| **File existence** | Referenced step files exist on disk |
| **ID consistency** | Step file `id` matches index entry `id` |
| **Filename match** | Step filename stem matches step `id` |
| **No duplicates** | No duplicate step IDs in index |
| **No unreferenced files** | All `.toon` files in `steps/` are referenced |
| **Dependency validity** | All dependencies reference existing steps |
| **No cycles** | Dependency graph is acyclic |
| **Parallel group validity** | All parallel group members reference existing steps |
| **Active step validity** | `active_step` references an existing step or is null |

The invariant checks live in `scripts/python/lib/runbook_toon.py` and are exposed via the `validate-runbook` CLI.

> **v1 legacy:** Runbooks using `runbook.json` are validated against `skills/runbook/schema.json` using `validate-json`.

## State Initialization

After creating an approved runbook, initialize state with:

### v2 TOON (default)

```text
uv run --project scripts/python init-runbook-state .runbooks/<runbook_id>/main.toon
```

### v1 JSON (legacy)

```text
uv run --project scripts/python init-runbook-state .runbooks/<runbook_id>/runbook.json
```

The initializer:

1. Validates the manifest via `init-runbook-state` (v2) or against `skills/runbook/schema.json` (v1).
2. Requires the file path `.runbooks/<runbook_id>/main.toon` (v2) or `runbook.json` (v1).
3. Requires `runbook.id == <runbook_id>`.
4. Requires `state_dir == ../../.state/<runbook_id>/`.
5. Creates `.state/<runbook_id>/` only when absent or empty.
6. Seeds `metadata.json`, `MAIN.json`, and step files when required.
7. Validates generated state against `skills/runbook/schemas/`.

> For v2 TOON runbooks, `init-runbook-state` uses the normalized loader from `runbook_toon.py` to load and merge step data before seeding state.

## Validation Commands

### v2 TOON (default — use these for new runbooks)

```text
uv run --project scripts/python validate-runbook .runbooks/<runbook_id>/main.toon
uv run --project scripts/python validate-runbook .runbooks/<runbook_id>/main.toon --strict
uv run --project scripts/python validate-runbook .runbooks/<runbook_id>/main.toon --json
uv run --project scripts/python init-runbook-state .runbooks/<runbook_id>/main.toon
```

### v1 JSON (legacy — only for existing v1 runbooks)

```text
uv run --project scripts/python validate-json skills/runbook/schema.json
uv run --project scripts/python validate-json .runbooks/<runbook_id>/runbook.json --schema skills/runbook/schema.json
uv run --project scripts/python init-runbook-state .runbooks/<runbook_id>/runbook.json
```

### State validation (shared between v1 and v2)

```text
uv run --project scripts/python validate-json .state/<runbook_id>/metadata.json --schema skills/runbook/schemas/state-metadata.schema.json
uv run --project scripts/python validate-json .state/<runbook_id>/MAIN.json --schema skills/runbook/schemas/state-main.schema.json
uv run --project scripts/python validate-json .state/<runbook_id>/<step-id>.json --schema skills/runbook/schemas/state-step.schema.json
```

## Embedded Quality Check

Every non-trivial runbook should include or trigger an embedded quality check using `review-work` and an appropriately sized `analysis-*` worker. The review should check:

- Fidelity to the approved plan and accepted proposal.
- Step granularity and dependency correctness.
- Worker routing and skill choices.
- File scope safety.
- Runbook schema validity (v1) or invariant validity (v2).
- State initialization validity.
- Recovery and rollback coverage.

## Rules

- Do not execute implementation changes while generating the runbook.
- Do not create `.plans/*.json` executable artifacts.
- Do not use `init-plan-state`; use `init-runbook-state` only.
- Do not store runbooks as single files directly under `.runbooks/`; use `.runbooks/<id>/main.toon` (v2) or `.runbooks/<id>/runbook.json` (v1).
- Do not modify worker agent names, model IDs, provider settings, or fallback ordering.
- Do not write outside `.runbooks/`, `.state/`, or explicitly authorized harness files.
- Do not hide unresolved assumptions; either encode them in the runbook or return to the plan/proposal stage.
- Validate v2 runbooks with `validate-runbook` (invariant checks); validate v1 runbooks with `validate-json` (schema checks).
- Do **not** create a v2 JSON Schema; v2 uses parser-backed invariant validation only.