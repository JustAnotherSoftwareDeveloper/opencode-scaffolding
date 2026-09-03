---
name: command-factory
description: "Use when creating or updating one commands/ contract."
selection:
  role: owner
  tags:
    actions: [create command]
    inputs: [command specification]
    outputs: [command file]
  use_when: [creating or updating one commands/ contract]
  not_for:
    [agent, skill, or arbitrary repository file creation; planning; delegation]
class: operation
---

# Command Factory

Create or update one bounded OpenCode command file under `commands/`.

## Normalize Input

1. Determine the command name, purpose, workflow steps, and constraints from the specification.
2. Map positional `$ARGUMENTS` usage and any referenced loaded skills.
3. Return `BLOCKED: <reason>` when the specification targets `agents/`, `skills/`, an arbitrary file outside `commands/`, a plan, a proposal, a delegated task, or a configuration migration.

## Procedure

1. Identify the target path as `commands/<name>.md`. Confirm the path is under `commands/` and does not overlap an existing file unless the operation is an update.
2. Read every existing command file with a related workflow or overlapping skill reference for discovery bounded to `commands/`. Inventory any shared loading, argument, or constraint conventions.
3. Write or update the command file frontmatter with exactly the supported fields: `description` (required, one-line trigger statement).
4. Write the body with these required sections:
   - A single opening instruction paragraph.
   - A `## Workflow` section with numbered execution steps.
   - A `## Constraints` section listing explicit prohibitions.
5. Validate the command file:
   - Frontmatter contains `description` and no invalid fields.
   - Body contains `## Workflow` and `## Constraints` sections.
   - Referenced skills resolve to existing `skills/<name>/SKILL.md` paths.
   - Referenced agents resolve to existing `agents/<name>.md` paths.
   - No stale, substituted, or non-winning skill or agent references.
6. Run the repository Markdown lint command on every modified file:
   ```sh
   cd scripts/node && bun run src/cli/lint-md.ts "../../commands/<name>.md"
   ```
   Fix every lint diagnostic before reporting completion.
7. Report the exact files read, the exact files written, and a bounded summary of related commands discovered.

## Self-Validation

- [ ] Target path is `commands/<name>.md` and does not escape `commands/`.
- [ ] Frontmatter contains `description` and no invalid, routing, scoring, or registry fields.
- [ ] Body contains `## Workflow` with numbered steps and `## Constraints` with explicit prohibitions.
- [ ] All referenced skills and agents resolve to existing canonical paths.
- [ ] No planning, proposal, delegated, or configuration-migration work was performed.
- [ ] No files outside `commands/` were written.
- [ ] Markdown lint passes on every modified file.

## Docs

See `./reference/README.md` for the command-file boundary and validation summary.
