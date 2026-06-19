# Orchestrated Skill Usage

Reference for authors filling the 7-section orchestrated template.
See `../templates/orchestrated.SKILL.template.md` (canonical skeleton) and `../REFERENCE.md` (class selection, frontmatter rules, collation).

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
- `../style-guide.md`
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

## H1 Heading Pattern

Use the naming convention:
> `# <<Skill Name>> — Orchestrated Skill`

## Collation Note

Collation output uses JSON with shape `{status, source_tags, items}`.
See `./collation-reference.md` for status values, source tag rules, and item schema guidance.