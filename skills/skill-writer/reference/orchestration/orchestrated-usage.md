# Orchestrated Skill Usage

Reference for authors filling the 7-section orchestrated template.
See `../templates/orchestrated.SKILL.template.md` (canonical skeleton), `../authoring/frontmatter-rules.md` (class selection and frontmatter rules), and `../platform/platform-context.md` (platform rules).

## Seven Sections

1. **Frontmatter** — Standard `name`, `description`, `class` YAML block.
2. **Purpose / H1 Intro** — One-line description of the orchestrated workflow.
3. **Execution Steps** — Ordered sequence of steps, each prefixed with a step type.
4. **Worker Strategy** — Dispatch model, concurrency limits, data flow.
5. **Verification Checklist** — Assertions that every orchestrated run must pass.
6. **Self-Validation** — Structural checks for the SKILL.md itself.
7. **Cross-References** — Relative links to support files.

## Step Types

Each step in the Execution Steps section uses a type prefix in bold:

- **`Delegated: <Worker Skill>`** — Delegates a sub-task to a worker skill by forwarding a delegation packet. The worker is another SKILL.md that receives the packet and executes autonomously. Use when the sub-work is multi-step, domain-specific, or benefits from a separate skill's context.
- **`Inline: <Inline Skill Name>`** — Declares and executes a named inline reasoning step directly within the orchestrator's body. Inline steps are single-pass, non-delegated reasoning blocks that do not merit a standalone skill. Use when the work is a focused logical or transform step that runs in one pass.
- **`Decompose`** — Breaks a complex input or goal into multiple sub-packets, typically fanning out to parallel delegated workers. No worker name follows the prefix; the step body describes the decomposition strategy.
- **`Verify`** — Runs verification checks against the output of prior steps. No worker name follows the prefix; the step body describes what to verify and how.

## Inline Steps vs. Standalone Inline Skills

**Inline steps replace the old standalone Inline Skills section concept.** Do not create a separate Inline Skills section in an orchestrated skill. Instead, use `Inline:` prefixed steps inside Execution Steps. The `inline` class is still valid for standalone skills that are self-contained, but within an orchestrated skill, inline work is expressed as a step type, not a separate section.

## Section Walkthrough

### Frontmatter

Standard YAML with `name`, `description` (starts `"Use when"`), and `class: orchestrated`.
**Pitfall**: `name` must match the directory under `skills/`.
```yaml
name: code-review-pipeline
description: "Use when orchestrating multi-phase code review."
class: orchestrated
```

### Purpose / H1 Intro

One sentence describing the orchestrated workflow.
**Pitfall**: Multi-line summary or tutorial preamble.
> <<Orchestrates static analysis, test execution, and reviewer assignment for pull requests.>>

### Execution Steps

Ordered list of steps, each prefixed with a step type in bold.
**Pitfall**: Mixing step types without clear boundaries or omitting the prefix.
1. **Delegated: <<Static Analysis Worker>>** — <<runs linters and reports violations.>>
2. **Decompose** — <<splits changed files into parallel test batches.>>
3. **Verify** — <<checks all test batches completed.>>

### Worker Strategy

Dispatch model, concurrency limits, and data flow.
**Pitfall**: Describing implementation instead of coordination intent.
> Sequential pipeline: static analysis completes before tests start.
> Fan-out: test batches run in parallel, up to 4 concurrent workers.

### Verification Checklist

Assertions the orchestrator run must satisfy.
**Pitfall**: Listing skill-authoring rules instead of run-time gates.
- All delegated workers returned `"success"` status.
- No critical violations in static analysis output.

### Self-Validation

Structural checks on the SKILL.md file itself.
**Pitfall**: Copying from template without reviewing placeholders.
- Name matches directory name.
- All `<<placeholders>>` are replaced.
- No old-template sections remain.

### Cross-References

Relative links to support files the orchestrator depends on.
**Pitfall**: Absolute paths or omitting links to referenced files.
- `../authoring/authoring-style.md`
- `./collation-reference.md`

## Step Types Reference

Each Execution Step uses a bold type prefix. Choose the type that matches work granularity.

- **Delegated: <<skill-name>>** — <<purpose>>.
  Sends a delegation packet to a worker skill.
  Use for multi-step sub-work that merits a separate skill context.
  Format: `**Delegated: <<skill-name>>** — <<one-line purpose>>. Input: <<input>>. Output: <<output>>.`
- **Inline: <<inline-skill-name>>** — <<description>>.
  Single-pass reasoning step executed directly within the orchestrator.
  Use for focused logical or transform work that runs in one pass.
- **Decompose** — <<what to decompose>>.
  Breaks complex input into multiple sub-packets, typically for parallel fan-out.
  No worker name follows the prefix; describe the decomposition strategy.
- **Verify** — <<what to check>>.
  Runs verification against prior step outputs.
  No worker name follows the prefix; describe what to verify and how.

## Worker Strategy Patterns

- **Sequential pipeline** — One worker completes before the next starts.
  Use when steps have strict input/output dependencies.
- **Parallel fan-out** — All workers execute simultaneously, results collated.
  Use when work units are independent and aggregate output is sufficient.
- **Conditional branching** — Route to different workers based on a condition.
  Use when the next step depends on a prior gate result.
  Example: if lint passes, delegate to test-runner; else delegate to fix-worker.

## Updating an Existing Orchestrated Skill

When updating an orchestrated skill (a skill using the 7-section canonical layout), apply the general update procedure from `../../SKILL.md` and `../maintenance/update-workflow.md` with these orchestration-specific considerations.

### Identifying Changed Sections

Before editing, compare the update request against each of the 7 sections:

- **Frontmatter** — Does the requirement change `name`, `description`, or `class`? If not, leave unchanged.
- **Purpose / H1 Intro** — Does the workflow scope change? If the purpose remains the same, keep the intro.
- **Execution Steps** — Are steps being added, removed, reordered, or retyped? This is the most common update target.
- **Worker Strategy** — Did the dispatch model, concurrency, or data flow change? If not, preserve the existing strategy.
- **Verification Checklist** — Are new run-time gates needed? Existing checks are rarely removed; additions are common.
- **Self-Validation** — Does the update affect structural SKILL.md conventions? Update only if the template or convention changed.
- **Cross-References** — Are new support files added or old ones moved? Add or update links as needed.

Mark each section as **unchanged**, **modified**, or **new**. Do not touch unchanged sections.

### Preserving Worker Strategy Decisions

Worker strategy patterns (sequential pipeline, parallel fan-out, conditional branching) embody design decisions that may predate the current update:

- Keep existing strategy descriptions unless the update explicitly changes the dispatch model.
- If adding a new execution step that runs alongside existing steps, extend the strategy description (e.g., "Fan-out: existing test batches plus new lint worker, concurrent up to 5").
- If the update changes concurrency limits or data flow, update only the affected part of the strategy.
- Do not rewrite strategy prose that the request does not address.

### Preserving Verification Checklist Items

The Verification Checklist accumulates run-time assertions that must be satisfied on every execution:

- Retain all pre-existing checklist items unless the request explicitly deprecates or replaces them.
- Add new items below existing ones. Order matters only if it reflects execution sequence.
- If a worker or step is being removed, remove only the verification item that gates it.
- If the update introduces a new step type (e.g., adding a `Verify` step), add a corresponding verification item for that step's outcome.

### Step Types in the Update Context

The same step type prefixes (`Delegated`, `Inline`, `Decompose`, `Verify`) apply regardless of CREATE or UPDATE mode. However, during an update:

- **Changing a step's type** — If a previously `Inline` step now merits a separate worker skill, change the prefix to `Delegated: <Worker Skill>` and add the worker to Cross-References.
- **Adding a new step** — Choose the step type as you would for a new skill: `Delegated` for multi-step sub-work, `Inline` for single-pass reasoning, `Decompose` for fan-out, `Verify` for gates.
- **Removing a step** — Delete the step line and its description. Also remove any Cross-Reference link that pointed exclusively to that step's worker.
- **Reordering steps** — Update the step numbers. Ensure the Worker Strategy still describes the resulting dispatch order.

## H1 Heading Pattern

Use the naming convention:
> `# <<Skill Name>> — Orchestrated Skill`

## Collation Note

Collation output uses JSON with shape `{status, source_tags, items}`.
See `./collation-reference.md` for status values, source tag rules, and item schema guidance.