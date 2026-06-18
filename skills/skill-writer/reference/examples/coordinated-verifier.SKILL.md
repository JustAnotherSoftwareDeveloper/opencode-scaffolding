---
name: coordinated-verifier
description: "Use when running coordinated verification across multiple quality dimensions."
class: orchestrated
---

# Coordinated Verifier — Orchestrated Skill

Coordinates multiple verifier workers to check code quality, test coverage, and documentation completeness, then collates results into a unified report.

## Execution Steps

1. **Decompose** — Break the verification scope into three independent dimensions: code quality, test coverage, and documentation.
   Each dimension becomes a separate worker task with its own input scope and output file.
2. **Delegated: code-quality-verifier** — Check lint rules, complexity thresholds, and style violations.
   Input: source root directory.
   Output: quality findings in JSON format.
3. **Delegated: test-coverage-verifier** — Analyze test coverage gaps across all test suites.
   Input: coverage report path.
   Output: coverage findings in JSON format.
4. **Inline: documentation-scanner** — Scan docstrings and README files for missing or stale documentation.
   Output: documentation findings in JSON format.
5. **Verify** — Confirm all three dimensions produced results and no dimension was BLOCKED or skipped.

## Worker Strategy

Parallel fan-out.
All three verifier workers execute simultaneously because their workloads are independent.
Orchestrator waits for all workers to complete, then collates results into a unified report.

## Verification Checklist

- All three dimensions completed without BLOCKED status.
- Each finding has a severity label and an actionable message.
- Collation output contains at least one item per dimension.

## Self-Validation

- All delegated skills referenced in Execution Steps are registered under `skills/`.
- Source_tags in collation output match dimension names: code-quality, test-coverage, documentation.
- No old-template sections (Phases, Failure Handling, Quality Gates) remain.

## Cross-References

- `./REFERENCE.md`
- `./reference/orchestrated-usage.md`
- `./reference/collation-reference.md`
- `./reference/worker-patterns.md`
