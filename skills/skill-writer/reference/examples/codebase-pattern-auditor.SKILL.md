---
name: codebase-pattern-auditor
description: "Use when auditing codebase patterns across multiple directories with coordinated workers."
class: orchestrated
---

# Codebase Pattern Auditor — Orchestrated Skill

Coordinates multiple worker skills to scan directory trees, detect pattern violations, and aggregate findings into a collated report.

## Execution Steps

1. **Delegated: pattern-scanner** — Scans each directory tree for configured patterns.
   Input: directory root, pattern config.
   Output: per-file findings.
2. **Inline: severity-classifier** — Classifies each finding as error, warning, or info based on pattern rules.
3. **Delegated: finding-enricher** — Enriches findings with context lines and documentation references.
   Input: raw findings.
   Output: enriched findings.
4. **Verify** — Confirms all directories were scanned, no findings were skipped, and the report is complete.

## Worker Strategy

Sequential pipeline.
Workers run one after another because each depends on the prior output.
The orchestrator passes accumulated state via delegation packets.

## Verification Checklist

- Pattern-scanner produced findings for every target directory.
- Severity-classifier assigned a valid severity (error, warning, or info) to every finding.
- Finding-enricher added context to at least 90% of findings.
- Collation JSON contains status, source_tags, and items fields.

## Self-Validation

- All worker skills referenced in Execution Steps exist under `skills/`.
- Placeholders in the orchestrated skill are replaced with concrete values.
- No old-template sections (Phases, State Ownership, Failure Handling) remain.
- Only one H1; all headings use Title Case.

## Cross-References

- `./REFERENCE.md`
- `./reference/orchestrated-usage.md`
- `./reference/worker-patterns.md`
- `./reference/collation-reference.md`
