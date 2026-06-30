---
name: customize-opencode
description: "Use when reference is needed for packet execution engine behavior in opencode worker agents."
tags: [opencode, configuration, customization, packet-execution]
class: documentation
---

# Customize OpenCode — Packet Execution Engine Reference

This skill provides reference documentation for the packet execution engine behavior within the OpenCode worker agent system.

## Packet Section Interpretation

The worker treats each packet section as an **authoritative operational directive**, not as parsing targets or suggestions.

### `## PURPOSE` — Operational Directive

The `## PURPOSE` section defines the **operational intent** for the worker. It is not metadata to be parsed and stored—it is a directive that shapes execution context.

- **Worker behavior**: Treat as the primary directive governing what work should be performed
- **Execution impact**: All actions must align with the stated purpose
- **Boundary**: Purpose clarifies scope but does not override explicit instructions in other sections

### `## DETAILS` — Source of Truth

The `## DETAILS` section contains the **authoritative facts** for task execution. The worker must not introduce new facts beyond what is provided here.

- **Worker behavior**: Use exclusively for contextual information needed to execute
- **Execution impact**: Any assumptions or inferences must be documented as such
- **Boundary**: Worker must not invent context, dependencies, or missing information

### `## EXECUTION INSTRUCTIONS` — Sequential Commands

The `## EXECUTION INSTRUCTIONS` section contains **ordered imperative commands** that the worker executes sequentially.

- **Worker behavior**: Execute each step in order, reporting failures at the failing step
- **Execution impact**: Steps are actions, not suggestions—execute until completion or blocker
- **Boundary**: Worker must not skip, reorder, or modify steps without explicit authorization

### `## EXPECTED OUTPUT` — Deliverable Specification

The `## EXPECTED OUTPUT` section defines the **exact deliverable** the worker must produce.

- **Worker behavior**: Produce output matching specifications exactly, nothing more or less
- **Execution impact**: Output is verified against this specification
- **Boundary**: Worker must not add, remove, or modify output without explicit instruction

## Execution Model

### Sequential Execution

Workers execute `## EXECUTION INSTRUCTIONS` steps sequentially:

1. Read all `## FILES TO READ` before executing any step
2. Execute each step in order as an imperative action
3. Report failure at the failing step—do not skip or continue
4. Complete all steps before producing output

### Output Fidelity

Workers produce output matching `## EXPECTED OUTPUT` exactly:

### Verification Step

Before producing output, workers must:

1. Compare the actual output against the `## EXPECTED OUTPUT` specification
2. Verify all requirements in `## VERIFICATION` section are met
3. Check that output scope matches `## EXPECTED OUTPUT` exactly (no more, no less)

### PARTIAL: Signaling for Incomplete Work

When verification reveals incomplete work:

- Use `PARTIAL:` prefix before the deliverable
- Include a brief explanation of what was left undone
- Example: `PARTIAL: Deliverable completed but missing X, Y, Z`

### BLOCKED: Signaling for Unmet Requirements

When requirements cannot be met:

- Use `BLOCKED:` prefix before the deliverable
- Include a clear reason explaining why requirements are unmet
- Example: `BLOCKED: Cannot fulfill requirement because X, Y, Z`

### Success Signal

- Silence is success—clean deliverable only when complete
- No prefixes or additional metadata in successful output

## Skill Integration

When `## SKILLS` section is present in a packet, the worker implements a **skill loading mechanism** to parse, load, and apply named skills:

### 1. Parse SKILLS Section

- Extract skill names from the `## SKILLS` section
- Skill names are listed as a comma-separated or newline-separated list
- Each named skill is treated as a requirement for packet execution

### 2. Load Named Skills

- For each skill name parsed from `## SKILLS`:
  - Invoke the `skill` tool to load the named skill
  - The skill tool returns the skill's guidance and workflows
- Skills are loaded in the order they appear in the `## SKILLS` section

### 3. Apply Skill Guidance

- Apply loaded skills' workflows to enhance packet execution
- Use skill templates/structures when specified in the skill documentation
- Ensure skill guidance serves packet requirements, not independent directives
- Skill guidance supplements but does not override packet instructions

### 4. Handle Unavailable Skills

- When a named skill is unavailable (not found or cannot be loaded):
  - Report `BLOCKED:` status before producing any output
  - Include a clear reason: "BLOCKED: Skill '{skill_name}' is unavailable"
  - Do not proceed with packet execution until skill is available

### 5. Restrict Skill Loading

- Only load skills explicitly named in the `## SKILLS` section
- Never load skills not specified in the packet
- Never load skills based on implicit requirements or assumptions
- Never discover or load skills outside the authorized scope

## Tool Integration Boundaries

The worker enforces strict tool usage boundaries to prevent scope expansion and unauthorized operations:

### `glob` and `grep` Tools

- **Restriction**: Only used when explicitly authorized by `## FILES TO READ`
- **Authorization**: Packet must list specific files or patterns to discover
- **Prohibition**: Never use for exploratory file discovery outside authorized scope
- **Rationale**: Prevents autonomous scope expansion and context invention

### `webfetch` Tool

- **Restriction**: Only used when explicitly directed in `## EXECUTION INSTRUCTIONS`
- **Authorization**: Packet must contain explicit instruction to fetch web content
- **Prohibition**: Never use for unprompted information gathering
- **Rationale**: Prevents unauthorized external data collection

### `edit` and `write` Tools

- **Restriction**: Only used within `## FILES TO WRITE`
- **Authorization**: Packet must explicitly list target files for modification
- **Prohibition**: Never modify or create files outside the authorized list
- **Rationale**: Prevents unauthorized file system modifications

## Strict Delegation Model

The worker operates under strict boundaries:

| Scope | Restriction |
|-------|-------------|
| Read | Only `## FILES TO READ` (including authorized discoveries) |
| Write | Only `## FILES TO WRITE` |
| Output | Only `## EXPECTED OUTPUT` |
| Discovery | Only when packet-authorized via `## FILES TO READ` |
| Tool Usage | Only within authorized scopes per Tool Integration Boundaries |

## Verification

Workers execute `## VERIFICATION` steps when present:

1. **Run verification checks** against output using criteria from `## VERIFICATION` section
2. **Attempt remediation** when verification fails, if possible within packet constraints
3. **Use PARTIAL:** signal for incomplete verification - includes explanation of what was left undone
4. **Report BLOCKED:** for unmet requirements - includes clear reason explaining why requirements cannot be met
5. **Produce clean deliverable** when verification passes - no prefixes or additional metadata

### Verification Checklist

Workers should verify:

- [ ] Output matches `## EXPECTED OUTPUT` specifications exactly
- [ ] All `## VERIFICATION` criteria are satisfied
- [ ] No facts introduced beyond `## DETAILS`
- [ ] No files read outside `## FILES TO READ`
- [ ] No files written outside `## FILES TO WRITE`