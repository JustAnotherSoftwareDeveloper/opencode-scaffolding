# Reference Documentation Navigation

Guidance for using local reference files alongside canonical harness schemas without overloading context.

## Local vs Canonical References

| Purpose | Use This File | Also See |
|---------|---------------|----------|
| Authoring checklist | `reference/authoring-workflow.md` (this directory) | `skill-hygiene/reference/authoring-checklist.md` |
| Class selection guide | `reference/class-selection.md` (this directory) | N/A |
| Trigger description guidance | *Local understanding* | `skill-hygiene/reference/description-evals.md` |
| Script safety rules | *Reference when writing scripts* | `skill-hygiene/reference/script-safety.md` |

## Schema Definitions (Authoritative)

Canonical XSD schemas are in `skills/skill-hygiene/schemas/`:

- `delegated.xsd` — Delegated skill class contract  
- `orchestrated.xsd` — Orchestrated skill class contract
- `documentation.xsd` — Documentation skill class contract  
- `planning.xsd` — Planning skill class contract

> Runbooks also use schemas from `skills/runbook/schemas/` for state.xml, main.xml validation.

## Key Cross-Cutting References

### Skill Hygiene Rules

| Topic | Reference File |
|-------|---------------|
| Frontmatter hygiene (name/description/class) | This directory's `*selection.md` and `authoring-workflow.md` | 
| Script safety & permissions | `../skill-hygiene/reference/script-safety.md` |
| Trigger description eval patterns | `../skill-hygiene/reference/description-evals.md` |

### Runbook Validation Contracts  

For skills that produce runbooks, reference these XSDs under `skills/runbook/schemas/`:
- `runbook.xsd` — main.xml structure validation  
- `state.xsd` — state.xml execution tracking
- Manifest schemas for evidence/snippets/reference directories

## Progressive Loading Guidance

When documenting in SKILL.md body:

1. **Keep it lean** — Only include what's needed upfront (triggers, key steps)
2. **Reference supporting files** — Use relative paths like `reference/class-selection.md` 
3. **Explain when to read more** — "See reference/ for detailed schema mappings" is sufficient.

## Citation Pattern for External Sources

When referencing canonical harness documents:

```text
[Source Title](relative-path) — Used for <specific purpose>
```

Example from `skill-writer/SKILL.md`:
- See `reference/class-selection.md` for trigger language guidance