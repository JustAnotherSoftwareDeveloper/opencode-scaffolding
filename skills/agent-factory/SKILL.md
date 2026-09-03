---
name: agent-factory
description: "Use when creating or updating one agents/ contract."
selection:
  role: owner
  tags:
    actions: [create agent]
    inputs: [agent specification]
    outputs: [agent file]
  use_when: [creating or updating one agents/ contract]
  not_for:
    [command, skill, or arbitrary repository file creation; delegation; runtime agent execution]
class: operation
---

# Agent Factory

Create or update one bounded OpenCode agent file under `agents/`.

## Normalize Input

1. Determine the agent name, description, mode, permission model, version, and capability boundaries from the specification.
2. Identify referenced skills, tools, and guardrails.
3. Return `BLOCKED: <reason>` when the specification targets `commands/`, `skills/`, an arbitrary file outside `agents/`, a delegated task, or runtime agent execution.

## Procedure

1. Identify the target path as `agents/<name>.md`. Confirm the path is under `agents/` and does not overlap an existing file unless the operation is an update.
2. Read every existing agent file with a related mode or overlapping skill/tool declaration for discovery bounded to `agents/`. Inventory shared naming, permission, and guardrail conventions.
3. Write or update the agent file frontmatter with exactly these supported fields:
   - `name` — quoted string matching the filename stem.
   - `description` — one-line role summary.
   - `mode` — `primary` or `subagent`.
   - `permission` — tool permission map; required only when the agent needs non-default permissions.
   - `version` — semantic version string.
   Do not add routing, scoring, registry, or delegation metadata to the frontmatter.
4. Write the body with these required sections:
   - A heading matching the agent name.
   - A role-purpose paragraph.
   - A `## Workflow` section with numbered execution steps when the agent follows a procedural sequence, or a `## Operating Rules` section when it follows constraint-based guidance.
   - A `## Guardrails` section listing explicit prohibitions and capability boundaries.
5. Validate the agent file:
   - Frontmatter contains `name`, `description`, and `mode`.
   - `mode` is `primary` or `subagent`.
   - Referenced skills resolve to existing `skills/<name>/SKILL.md` paths.
   - Tool declarations are explicit and bounded.
   - No stale, substituted, or non-winning references.
   - Prompt and instruction sentences are coherent and non-contradictory.
6. Run the repository Markdown lint command on every modified file:
   ```sh
   cd scripts/node && bun run src/cli/lint-md.ts "../../agents/<name>.md"
   ```
   Fix every lint diagnostic before reporting completion.
7. Report the exact files read, the exact files written, and a bounded summary of related agents discovered.

## Self-Validation

- [ ] Target path is `agents/<name>.md` and does not escape `agents/`.
- [ ] Frontmatter contains `name`, `description`, and `mode` with no invalid, routing, scoring, or registry fields.
- [ ] Body contains a heading, a role-purpose statement, a `## Workflow` or `## Operating Rules` section, and a `## Guardrails` section.
- [ ] All referenced skills resolve to existing canonical paths.
- [ ] No delegation, runtime execution, or agent-orchestration work was performed.
- [ ] No files outside `agents/` were written.
- [ ] Markdown lint passes on every modified file.

## Docs

See `./reference/README.md` for the agent-file boundary and validation summary.
