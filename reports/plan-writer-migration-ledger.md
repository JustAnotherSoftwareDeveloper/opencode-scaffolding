# Plan-Writer Migration Ledger

## Pre-cutover scope

- Source workspace: `skills/plan/`.
- Target workspace: `skills/plan-writer/`.
- Required identity: `name: plan-writer`, `class: operation`.
- User-facing command preserved: `/plan` (`commands/plan.md`).
- No alias, shim, or symlink is permitted.

## Exact active identity references

The following active references were identified for the coordinated cutover:

- `commands/plan.md` — internal skill load target.
- `commands/leeroy-jenkins.md` — internal plan-stage skill load target.
- `agents/planner.md` — executable planning skill list.
- `skills/README.md` — operations index.
- `skills/task-contract/SKILL.md` — directional support target.
- `skills/planning-pipeline-architecture/SKILL.md` and its lifecycle reference
  mappings — planning-stage owner names.
- `scripts/python/tests/test_direct_planning_workflows.py` — active workflow path.
- `scripts/python/test-data/semantic-selection-cases.json` — frozen selection
  inventory, expected names, and expected paths.
- `scripts/python/test-data/task-contract-selection-cases.json` — task-contract
  neighboring-selection inventory and expected plan-workspace owner.

Ordinary uses of “plan”, “planning”, `.plans/`, plan workspaces, task plans, and
the `/plan` command name are not identity references and remain unchanged.

## Historical exclusions

- `.plans/` and `.proposals/` are historical or user artifact workspaces and are
  excluded from this cutover.
- `archive/` is historical and is excluded from this cutover.
- This ledger does not claim retroactive byte-level proof for ignored historical
  workspaces. Their exclusion is a migration boundary, not evidence derived from
  `git diff`.

## Collector state before cutover

- `collect-skills --class operation --class documentation` returned one `plan`
  operation at `skills/plan/SKILL.md` and one `task-contract` documentation
  record at `skills/task-contract/SKILL.md`.
- `collect-skills --class planning` returned
  `planning-pipeline-architecture` and `skill-architect`; neither is an
  executable plan owner.

## Source manifest and rollback evidence

The complete source subtree contained these files before the move:

```text
skills/plan/SKILL.md
skills/plan/reference/README.md
skills/plan/reference/scripts.md
skills/plan/reference/task-authoring.md
skills/plan/reference/workspace-contract.md
```

Pre-cutover SHA-256 values:

```text
34e4f0a88fc4f000fc155cd4720ab3aaa8c4bf4f34208115a2b17e70ba875e61  skills/plan/SKILL.md
bd5b2740c3e473fe0491eb958115ec461ff9005f38e6dfaa807847b4733d0adc  skills/plan/reference/README.md
7c4504256e3302e325c7cb3cb1eaae43868c49e49e43efe821c7c7cf28df7e76  skills/plan/reference/scripts.md
ef736d94f7766378350055b4809d2f180ef644b65e977d460e0912255d5f17af  skills/plan/reference/task-authoring.md
6a6506200a54d3f3a023fe231fb8f87867190d38b7f807b2b7b3f46bf0d3cb22  skills/plan/reference/workspace-contract.md
```

Rollback is bounded to moving `skills/plan-writer/` back to `skills/plan/` and
reversing the exact active identity-reference substitutions. Historical artifact
paths are not part of rollback scope.

## Post-cutover evidence

- The operation/documentation collector returned one `plan-writer` operation at
  `skills/plan-writer/SKILL.md` and one `task-contract` documentation record at
  `skills/task-contract/SKILL.md`.
- The planning collector returned `planning-pipeline-architecture` and
  `skill-architect`; no planning profile was treated as an executable assignment.
- `test_plan_writer_migration.py` passed its workspace, collector, contract-order,
  caller/fixture, historical-preservation, and rollback-ledger checks.
- `node scripts/validate-skills.js` and the Python skill validator passed for the
  changed `plan-writer`, `task-contract`, and
  `planning-pipeline-architecture` entry points.

Post-cutover SHA-256 values used by the migration regression test:

```text
4fe372b16bb308c55fa7859c12718990471cd19c63796279af61a0e52e53d025  skills/plan-writer/SKILL.md
06504be2b7436c44c07be44442146d89ec6e4e5cd9cca7f9115d20abcc0cd90d  skills/plan-writer/reference/README.md
87500fcc8096c97686a9dfba860192c0779613eb590950b12f8b98084f027e5b  skills/plan-writer/reference/scripts.md
17001bb9b496d4be823f947196a824e4fc81bd7c996105d648088e349f091f44  skills/plan-writer/reference/task-authoring.md
9b42f2e9b932820c90c5548e946293c5ec7335a40b26d8c8b2c8732645109040  skills/plan-writer/reference/workspace-contract.md
```
